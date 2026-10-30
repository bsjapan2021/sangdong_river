/* /api/auth?a=register|login|me|verify|resend|forgot|reset|logout */
import { q, memberByEmail, memberById, isIpBlocked } from '../lib/db.js';
import { ok, fail, body, clientIp, appUrl, authEnabled, hashPassword, verifyPassword, signSession, currentMember, signPurpose, readPurpose,
  seedAdmin, profile, limited, ADMIN_EMAIL, mailOn, mailVerify, mailReset, mailAdminNotice } from '../lib/auth.js';

const EMAIL_RE = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
const str = (v, n = 200) => (typeof v === 'string' ? v.trim().slice(0, n) : '');
const fails = new Map();   /* 계정별 연속 실패 잠금 */

export default async function handler(req, res) {
  const a = String((req.query && req.query.a) || '');
  if (!authEnabled()) return fail(res, 503, 'AUTH_DISABLED', '회원 기능이 아직 설정되지 않았습니다(DB 연결 필요).');
  try {
    await seedAdmin();
    const ip = clientIp(req);
    if (a !== 'me' && await isIpBlocked(ip)) return fail(res, 403, 'IP_BLOCKED', '접속이 차단된 IP입니다. 관리자에게 문의하세요.');
    if (req.method !== 'POST' && a !== 'me') return fail(res, 405, 'METHOD', 'POST only');
    const b = body(req);

    if (a === 'register') {
      if (limited('reg:' + ip, 5)) return fail(res, 429, 'RATE_LIMIT', '요청이 많습니다. 잠시 후 다시 시도하세요.');
      const email = str(b.email).toLowerCase(), password = typeof b.password === 'string' ? b.password : '', name = str(b.name, 60), phone = str(b.phone, 40), org = str(b.org, 80), memo = str(b.memo, 300);
      if (!name) return fail(res, 400, 'INVALID', '이름을 입력하세요.');
      if (!EMAIL_RE.test(email)) return fail(res, 400, 'INVALID', '올바른 이메일 형식이 아닙니다.');
      if (password.length < 8 || password.length > 128) return fail(res, 400, 'INVALID', '비밀번호는 8자 이상이어야 합니다.');
      if (!phone) return fail(res, 400, 'INVALID', '연락처를 입력하세요.');
      if (email === ADMIN_EMAIL) return fail(res, 409, 'EMAIL_TAKEN', '이미 가입된 이메일입니다.');   /* 최고관리자 이메일은 예약(가입 선점 방지) */
      if (await memberByEmail(email)) return fail(res, 409, 'EMAIL_TAKEN', '이미 가입된 이메일입니다.');
      const { hash, salt } = hashPassword(password); const mail = mailOn();
      const r = await q(`INSERT INTO sd_members(email,pw_hash,pw_salt,name,phone,org,memo,role,status,email_verified,created_at,last_ip)
        VALUES($1,$2,$3,$4,$5,$6,$7,'user','pending',$8,$9,$10) ON CONFLICT (email) DO NOTHING RETURNING id`, [email, hash, salt, name, phone, org, memo || null, !mail, Date.now(), ip]);
      if (!r.rows[0]) return fail(res, 409, 'EMAIL_TAKEN', '이미 가입된 이메일입니다.');
      const id = r.rows[0].id; let sent = false;
      if (mail) { const t = await signPurpose(id, 'verify'); sent = await mailVerify(email, name, `${appUrl(req)}/?verify=${encodeURIComponent(t)}`); }
      mailAdminNotice({ name, email, org, phone, memo }, `${appUrl(req)}/?admin=1`).catch(() => {});
      return ok(res, { verificationSent: sent, pending: true, email });
    }

    if (a === 'login') {
      if (limited('login:' + ip, 20)) return fail(res, 429, 'RATE_LIMIT', '요청이 많습니다. 잠시 후 다시 시도하세요.');
      const email = str(b.email).toLowerCase(), password = typeof b.password === 'string' ? b.password : '';
      if (!email || !password) return fail(res, 400, 'INVALID', '이메일과 비밀번호를 입력하세요.');
      const f = fails.get(email); if (f && f.lock > Date.now()) return fail(res, 429, 'LOGIN_LOCKED', `로그인 시도가 많아 잠겼습니다. ${Math.ceil((f.lock - Date.now()) / 60e3)}분 후 다시 시도하세요.`);
      const m = await memberByEmail(email);
      if (!m || !verifyPassword(password, m.pw_hash, m.pw_salt)) {
        const r = fails.get(email) || { n: 0, lock: 0 }; r.n++; if (r.n >= 6) { r.n = 0; r.lock = Date.now() + 10 * 60e3 } fails.set(email, r);
        return fail(res, 401, 'BAD_CREDENTIALS', '이메일 또는 비밀번호가 올바르지 않습니다.');
      }
      fails.delete(email);
      if (mailOn() && !m.email_verified) return fail(res, 403, 'EMAIL_UNVERIFIED', '이메일 인증이 필요합니다. 메일함의 인증 링크를 확인하세요.');
      if (m.status === 'pending') return fail(res, 403, 'PENDING_APPROVAL', '관리자 승인 대기 중입니다. 승인 후 로그인할 수 있습니다.');
      if (m.status === 'blocked') return fail(res, 403, 'ACCOUNT_BLOCKED', '이용이 차단된 계정입니다. 관리자에게 문의하세요.');
      await q('UPDATE sd_members SET last_login=$1, last_ip=$2 WHERE id=$3', [Date.now(), ip, m.id]);
      return ok(res, { token: await signSession(m), member: profile(m) });
    }

    if (a === 'me') {
      const m = await currentMember(req);
      if (!m) return fail(res, 401, 'UNAUTHORIZED', '로그인이 필요합니다.');
      if (await isIpBlocked(ip) && m.role !== 'admin') return fail(res, 403, 'IP_BLOCKED', '접속이 차단된 IP입니다. 관리자에게 문의하세요.');
      return ok(res, { member: profile(m), mail: mailOn() });
    }

    if (a === 'verify') {
      const p = await readPurpose(str(b.token, 2000), 'verify');
      if (!p) return fail(res, 400, 'INVALID_TOKEN', '인증 링크가 유효하지 않거나 만료되었습니다.');
      const m = await memberById(p.sub); if (!m) return fail(res, 400, 'INVALID_TOKEN', '인증 링크가 유효하지 않습니다.');
      await q('UPDATE sd_members SET email_verified=TRUE WHERE id=$1', [p.sub]);
      return ok(res, { status: m.status });
    }

    if (a === 'resend') {
      if (limited('mail:' + ip, 3)) return fail(res, 429, 'RATE_LIMIT', '요청이 많습니다. 잠시 후 다시 시도하세요.');
      const m = await memberByEmail(str(b.email).toLowerCase());
      if (m && !m.email_verified && mailOn()) { const t = await signPurpose(Number(m.id), 'verify'); await mailVerify(m.email, m.name, `${appUrl(req)}/?verify=${encodeURIComponent(t)}`); }
      return ok(res, { mail: mailOn() });   /* 계정 존재 여부 비노출 */
    }

    if (a === 'forgot') {
      if (limited('mail:' + ip, 3)) return fail(res, 429, 'RATE_LIMIT', '요청이 많습니다. 잠시 후 다시 시도하세요.');
      const m = await memberByEmail(str(b.email).toLowerCase());
      if (m && m.status !== 'blocked' && mailOn()) { const t = await signPurpose(Number(m.id), 'reset', m.pw_hash.slice(0, 16)); await mailReset(m.email, m.name, `${appUrl(req)}/?reset=${encodeURIComponent(t)}`); }
      return ok(res, { mail: mailOn() });
    }

    if (a === 'reset') {
      if (limited('reset:' + ip, 8)) return fail(res, 429, 'RATE_LIMIT', '요청이 많습니다. 잠시 후 다시 시도하세요.');
      const p = await readPurpose(str(b.token, 2000), 'reset'); const pw = typeof b.password === 'string' ? b.password : '';
      if (!p) return fail(res, 400, 'INVALID_TOKEN', '재설정 링크가 유효하지 않거나 만료되었습니다.');
      if (pw.length < 8 || pw.length > 128) return fail(res, 400, 'INVALID', '비밀번호는 8자 이상이어야 합니다.');
      const m = await memberById(p.sub);
      if (!m || (p.bind && p.bind !== m.pw_hash.slice(0, 16))) return fail(res, 400, 'INVALID_TOKEN', '이미 사용되었거나 유효하지 않은 링크입니다.');
      const { hash, salt } = hashPassword(pw);
      await q('UPDATE sd_members SET pw_hash=$1, pw_salt=$2, email_verified=TRUE WHERE id=$3', [hash, salt, m.id]);
      return ok(res, { status: m.status });
    }

    if (a === 'password') {   /* 로그인 상태에서 비밀번호 변경 */
      const m = await currentMember(req); if (!m) return fail(res, 401, 'UNAUTHORIZED', '로그인이 필요합니다.');
      const cur = typeof b.current === 'string' ? b.current : '', pw = typeof b.password === 'string' ? b.password : '';
      if (!verifyPassword(cur, m.pw_hash, m.pw_salt)) return fail(res, 401, 'BAD_CREDENTIALS', '현재 비밀번호가 올바르지 않습니다.');
      if (pw.length < 8 || pw.length > 128) return fail(res, 400, 'INVALID', '비밀번호는 8자 이상이어야 합니다.');
      const { hash, salt } = hashPassword(pw); await q('UPDATE sd_members SET pw_hash=$1, pw_salt=$2 WHERE id=$3', [hash, salt, m.id]);
      return ok(res, {});
    }

    if (a === 'logout') return ok(res, {});
    return fail(res, 404, 'NOT_FOUND', 'unknown action');
  } catch (e) { console.error('auth error', e); return fail(res, 500, 'SERVER_ERROR', '서버 오류가 발생했습니다.'); }
}
