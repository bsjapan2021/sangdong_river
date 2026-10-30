/* /api/report?a=save|list|get — 게이트 운항 보고서 저장·조회(로그인 회원: 본인 것, 최고관리자: 전체) */
import { q } from '../lib/db.js';
import { ok, fail, body, authEnabled, currentMember, ADMIN_EMAIL } from '../lib/auth.js';
export default async function handler(req, res) {
  if (!authEnabled()) return fail(res, 503, 'AUTH_DISABLED', '회원 기능이 아직 설정되지 않았습니다.');
  try {
    const m = await currentMember(req); if (!m) return fail(res, 401, 'UNAUTHORIZED', '로그인이 필요합니다.');
    const a = String((req.query && req.query.a) || 'list'), su = m.role === 'admin' && m.email === ADMIN_EMAIL;
    if (a === 'save') {
      if (req.method !== 'POST') return fail(res, 405, 'METHOD', 'POST only');
      const r = body(req).report; if (!r || typeof r !== 'object' || !Array.isArray(r.gates)) return fail(res, 400, 'INVALID', '보고서 형식이 올바르지 않습니다.');
      const data = JSON.stringify(r); if (data.length > 60000) return fail(res, 400, 'TOO_LARGE', '보고서가 너무 큽니다.');
      const cnt = await q('SELECT COUNT(*)::int AS n FROM sd_reports WHERE member_email=$1', [m.email]); if (cnt.rows[0].n >= 200) await q('DELETE FROM sd_reports WHERE id IN (SELECT id FROM sd_reports WHERE member_email=$1 ORDER BY at ASC LIMIT 1)', [m.email]);
      const ins = await q('INSERT INTO sd_reports(member_email,at,ros,data) VALUES($1,$2,$3,$4) RETURNING id', [m.email, Date.now(), Math.max(0, Math.round(+r.ros || 0)), data]);
      return ok(res, { id: ins.rows[0].id });
    }
    if (a === 'list') { const r = su ? await q('SELECT id,member_email,at,ros FROM sd_reports ORDER BY at DESC LIMIT 50') : await q('SELECT id,member_email,at,ros FROM sd_reports WHERE member_email=$1 ORDER BY at DESC LIMIT 50', [m.email]);
      return ok(res, r.rows.map(x => ({ id: x.id, by: x.member_email, at: Number(x.at), ros: Number(x.ros) }))); }
    if (a === 'get') { const id = Number(req.query.id); const r = await q('SELECT * FROM sd_reports WHERE id=$1', [id]); const x = r.rows[0];
      if (!x || (!su && x.member_email !== m.email)) return fail(res, 404, 'NOT_FOUND', '보고서를 찾을 수 없습니다.'); return ok(res, JSON.parse(x.data)); }
    return fail(res, 404, 'NOT_FOUND', 'unknown action');
  } catch (e) { console.error('report error', e); return fail(res, 500, 'SERVER_ERROR', '서버 오류가 발생했습니다.'); }
}
