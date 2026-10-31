/* /api/admin?a=overview|approve|block|unblock|verify|temp-password|delete|ip-block|ip-unblock — 최고관리자 전용 */
import { q, memberById, kvGet, kvSet } from '../lib/db.js';
import { ok, fail, body, clientIp, appUrl, authEnabled, requireAdmin, profile, hashPassword, tempPassword, seedAdmin, mailOn, mailApproved, ADMIN_EMAIL } from '../lib/auth.js';
const ONLINE_MS = 120e3;

export default async function handler(req, res) {
  if (!authEnabled()) return fail(res, 503, 'AUTH_DISABLED', '회원 기능이 아직 설정되지 않았습니다.');
  try {
    await seedAdmin();
    const admin = await requireAdmin(req, res); if (!admin) return;
    const a = String((req.query && req.query.a) || 'overview'), b = body(req), myIp = clientIp(req), now = Date.now();
    if (a === 'overview') {
      const [m, v, bl] = await Promise.all([
        q('SELECT * FROM app_members ORDER BY (status=\'pending\') DESC, created_at DESC LIMIT 500'),
        q('SELECT * FROM app_visitors WHERE last_seen > $1 ORDER BY last_seen DESC LIMIT 400', [now - 14 * 86400e3]),
        q('SELECT * FROM app_blocked ORDER BY at DESC')]);
      const blocked = new Set(bl.rows.map(r => r.ip)); let release = null; try { const r = await kvGet('release'); if (r) release = JSON.parse(r) } catch {}
      return ok(res, { me: { ip: myIp }, mail: mailOn(), now, release,
        members: m.rows.map(profile),
        visitors: v.rows.map(r => ({ ip: r.ip, ua: r.ua, email: r.member_email, name: r.member_name, role: r.member_role, country: r.country, city: r.city,
          firstSeen: Number(r.first_seen), lastSeen: Number(r.last_seen), hits: r.hits, online: now - Number(r.last_seen) < ONLINE_MS, blocked: blocked.has(r.ip) })),
        blocked: bl.rows.map(r => ({ ip: r.ip, reason: r.reason, at: Number(r.at), by: r.by_email })) });
    }
    if (req.method !== 'POST') return fail(res, 405, 'METHOD', 'POST only');
    if (a === 'release') {   /* 회원 화면 일괄 업데이트: 이 빌드보다 오래된 화면은 자동 새로고침 */
      const version = String(b.version || '').trim(); if (!/^\d{8}-\d{6}$/.test(version)) return fail(res, 400, 'INVALID', '빌드 버전 형식이 올바르지 않습니다.');
      await kvSet('release', JSON.stringify({ version, note: String(b.note || '').slice(0, 120), at: now, by: admin.email })); return ok(res, { version });
    }
    if (a.startsWith('ip-')) {
      const ip = String(b.ip || '').trim().slice(0, 64); if (!ip) return fail(res, 400, 'INVALID', 'IP가 필요합니다.');
      if (a === 'ip-block') { if (ip === myIp) return fail(res, 400, 'SELF_BLOCK', '현재 사용 중인 내 IP는 차단할 수 없습니다.');
        await q('INSERT INTO app_blocked(ip,reason,at,by_email) VALUES($1,$2,$3,$4) ON CONFLICT (ip) DO UPDATE SET reason=EXCLUDED.reason, at=EXCLUDED.at', [ip, String(b.reason || '').slice(0, 200) || null, now, admin.email]); }
      else if (a === 'ip-unblock') await q('DELETE FROM app_blocked WHERE ip=$1', [ip]);
      else return fail(res, 404, 'NOT_FOUND', 'unknown action');
      return ok(res, {});
    }
    const id = Number(b.id); const m = Number.isFinite(id) ? await memberById(id) : null;
    if (!m) return fail(res, 404, 'NOT_FOUND', '회원을 찾을 수 없습니다.');
    if (m.email === ADMIN_EMAIL && a !== 'temp-password') return fail(res, 400, 'SELF', '최고관리자 계정은 변경할 수 없습니다.');
    if (a === 'approve') { await q("UPDATE app_members SET status='active' WHERE id=$1", [id]); if (m.status === 'pending') mailApproved(m.email, m.name, appUrl(req)).catch(() => {}); return ok(res, {}); }
    if (a === 'block') { await q("UPDATE app_members SET status='blocked' WHERE id=$1", [id]); return ok(res, {}); }
    if (a === 'unblock') { await q("UPDATE app_members SET status='active' WHERE id=$1", [id]); return ok(res, {}); }
    if (a === 'verify') { await q('UPDATE app_members SET email_verified=$1 WHERE id=$2', [b.verified !== false, id]); return ok(res, {}); }
    if (a === 'temp-password') { if (m.email === ADMIN_EMAIL) return fail(res, 400, 'SELF', '최고관리자는 비밀번호 변경 메뉴를 이용하세요.');
      const pw = tempPassword(), { hash, salt } = hashPassword(pw); await q('UPDATE app_members SET pw_hash=$1, pw_salt=$2 WHERE id=$3', [hash, salt, id]); return ok(res, { tempPassword: pw }); }
    if (a === 'delete') { if (b.confirm !== m.email) return fail(res, 400, 'CONFIRM', '확인용 이메일이 일치하지 않습니다.'); await q('DELETE FROM app_members WHERE id=$1', [id]); return ok(res, {}); }
    return fail(res, 404, 'NOT_FOUND', 'unknown action');
  } catch (e) { console.error('admin error', e); return fail(res, 500, 'SERVER_ERROR', '서버 오류가 발생했습니다.'); }
}
