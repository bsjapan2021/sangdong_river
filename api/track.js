/* /api/track — 접속 하트비트(페이지 로드·45초 주기). IP·브라우저·지역·로그인 회원을 기록하고 차단 여부를 반환. */
import { q, isIpBlocked } from '../lib/db.js';
import { ok, fail, clientIp, geo, authEnabled, currentMember } from '../lib/auth.js';
export default async function handler(req, res) {
  if (!authEnabled()) return ok(res, { blocked: false, auth: false });
  try {
    const ip = clientIp(req), g = geo(req), now = Date.now(), ua = String((req.headers || {})['user-agent'] || '').slice(0, 300);
    const m = await currentMember(req).catch(() => null);
    await q(`INSERT INTO sd_visitors(ip,ua,member_email,member_name,member_role,country,city,first_seen,last_seen,hits) VALUES($1,$2,$3,$4,$5,$6,$7,$8,$8,1)
      ON CONFLICT (ip) DO UPDATE SET ua=EXCLUDED.ua, last_seen=EXCLUDED.last_seen, hits=sd_visitors.hits+1,
        member_email=COALESCE(EXCLUDED.member_email, sd_visitors.member_email), member_name=COALESCE(EXCLUDED.member_name, sd_visitors.member_name),
        member_role=COALESCE(EXCLUDED.member_role, sd_visitors.member_role), country=COALESCE(EXCLUDED.country, sd_visitors.country), city=COALESCE(EXCLUDED.city, sd_visitors.city)`,
      [ip, ua, m ? m.email : null, m ? m.name : null, m ? m.role : null, g.country, g.city, now]);
    const blocked = (m && m.role === 'admin') ? false : await isIpBlocked(ip);
    return ok(res, { blocked, auth: true, member: m ? { email: m.email, role: m.role } : null });
  } catch (e) { console.error('track error', e); return fail(res, 500, 'SERVER_ERROR', 'track failed'); }
}
