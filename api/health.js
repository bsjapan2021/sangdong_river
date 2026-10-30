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
      let okm = false; try { await nodemailer.createTransport({ service: 'gmail', auth: { user: process.env.MAIL_USER, pass: process.env.MAIL_APP_PASSWORD } }).verify(); okm = true } catch (e) { okm = false }
      mailCheck = { t: Date.now(), ok: okm } } out.mailLogin = mailCheck.ok; }
  return ok(res, out);
}
