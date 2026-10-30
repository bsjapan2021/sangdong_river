/* /api/health — 서버 설정 점검(비밀값은 노출하지 않음): DB 연결 · 최고관리자 생성 여부 · 메일 SMTP 로그인 */
import nodemailer from 'nodemailer';
import { q } from '../lib/db.js';
import { ok, authEnabled, seedAdmin, mailEnabled, ADMIN_EMAIL } from '../lib/auth.js';
let mailCheck = null;
export default async function handler(req, res) {
  const out = { db: false, adminReady: false, mailConfigured: mailEnabled(), mailLogin: null };
  if (authEnabled()) { try { await seedAdmin(); out.db = true;
    const r = await q("SELECT 1 FROM sd_members WHERE email=$1 AND role='admin' AND status='active'", [ADMIN_EMAIL]); out.adminReady = r.rows.length > 0; } catch (e) { out.dbError = 'connection failed'; } }
  if (out.mailConfigured) { if (!mailCheck || Date.now() - mailCheck.t > 600e3) {
      let okm = false, why = null; try { await nodemailer.createTransport({ service: 'gmail', auth: { user: process.env.MAIL_USER, pass: process.env.MAIL_APP_PASSWORD } }).verify(); okm = true } catch (e) { okm = false; why = [e && e.code, e && e.responseCode, String((e && e.response) || '').slice(0, 90)].filter(Boolean).join(' ') }
      mailCheck = { t: Date.now(), ok: okm, why } } out.mailLogin = mailCheck.ok; if (!mailCheck.ok) out.mailError = mailCheck.why;
    const u = String(process.env.MAIL_USER || ''); out.mailUserHint = u.replace(/^(.{2}).*(@.*)$/, '$1***$2'); out.mailPassLen = String(process.env.MAIL_APP_PASSWORD || '').replace(/\s/g, '').length; }
  return ok(res, out);
}
