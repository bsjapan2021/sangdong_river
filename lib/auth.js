/* 회원 인증 공용 — scrypt 비밀번호, HMAC 세션/목적 토큰, 관리자 시드, 레이트리밋, 메일(Gmail SMTP), 요청 유틸.
   자격증명은 모두 환경변수로만: DATABASE_URL · ADMIN_EMAIL/ADMIN_PASSWORD · MAIL_USER/MAIL_APP_PASSWORD · (선택) AUTH_SECRET */
import crypto from 'node:crypto';
import nodemailer from 'nodemailer';
import { q, kvGet, kvSet, memberByEmail, dbEnabled } from './db.js';

export const ADMIN_EMAIL = (process.env.ADMIN_EMAIL || 'kr.seunghunyeo@gmail.com').trim().toLowerCase();
const SESSION_TTL = 7 * 24 * 3600e3, VERIFY_TTL = 24 * 3600e3, RESET_TTL = 3600e3;

/* ---------- responses / request ---------- */
export function ok(res, data) { res.setHeader('Cache-Control', 'no-store'); res.status(200).json({ success: true, data: data ?? null }); }
export function fail(res, status, code, message) { res.setHeader('Cache-Control', 'no-store'); res.status(status).json({ success: false, error: { code, message } }); }
export function clientIp(req) {
  const h = req.headers || {}; const x = h['x-forwarded-for'] || h['x-real-ip'] || '';
  let ip = String(Array.isArray(x) ? x[0] : x).split(',')[0].trim() || (req.socket && req.socket.remoteAddress) || 'unknown';
  return ip.startsWith('::ffff:') ? ip.slice(7) : ip;
}
export function geo(req) { const h = req.headers || {}; const d = s => { try { return s ? decodeURIComponent(String(s)) : null } catch { return String(s) } };
  return { country: d(h['x-vercel-ip-country']), city: d(h['x-vercel-ip-city']) }; }
export function body(req) { const b = req.body; if (!b) return {}; if (typeof b === 'string') { try { return JSON.parse(b) } catch { return {} } } return b; }
export function bearer(req) { const a = String((req.headers || {}).authorization || ''); return a.startsWith('Bearer ') ? a.slice(7) : ''; }
export function appUrl(req) { if (process.env.APP_URL) return process.env.APP_URL.replace(/\/$/, '');
  const h = req.headers || {}; const host = h['x-forwarded-host'] || h.host || 'park.nanohydroin.com'; return `${/localhost|127\./.test(host) ? 'http' : 'https'}://${host}`; }
export function authEnabled() { return dbEnabled(); }

/* ---------- passwords ---------- */
export function hashPassword(pw) { const salt = crypto.randomBytes(16).toString('hex'); return { hash: crypto.scryptSync(pw, salt, 64).toString('hex'), salt }; }
export function verifyPassword(pw, hash, salt) { const a = crypto.scryptSync(pw, salt, 64), b = Buffer.from(hash, 'hex'); return a.length === b.length && crypto.timingSafeEqual(a, b); }
export function tempPassword() { const A = 'ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnpqrstuvwxyz23456789'; let s = ''; for (const b of crypto.randomBytes(10)) s += A[b % A.length]; return s + '!7'; }

/* ---------- secret + tokens ---------- */
let SECRET = null;
async function secret() {
  if (SECRET) return SECRET;
  if (process.env.AUTH_SECRET) return (SECRET = process.env.AUTH_SECRET);
  let s = await kvGet('auth_secret');   /* 자동 생성·DB 보관(서버측 전용) */
  if (!s) { s = crypto.randomBytes(48).toString('hex'); await kvSet('auth_secret', s); s = (await kvGet('auth_secret')) || s; }
  return (SECRET = s);
}
const b64u = b => Buffer.from(b).toString('base64').replace(/\+/g, '-').replace(/\//g, '_').replace(/=+$/, '');
const unb64u = s => Buffer.from(s.replace(/-/g, '+').replace(/_/g, '/'), 'base64');
async function sign(payload) { const body = b64u(JSON.stringify(payload)); const sig = b64u(crypto.createHmac('sha256', await secret()).update(body).digest()); return `${body}.${sig}`; }
async function open(tok) {
  if (!tok || tok.indexOf('.') < 1) return null; const [body, sig] = tok.split('.');
  const exp = b64u(crypto.createHmac('sha256', await secret()).update(body).digest());
  const a = Buffer.from(sig || ''), b = Buffer.from(exp); if (a.length !== b.length || !crypto.timingSafeEqual(a, b)) return null;
  try { const p = JSON.parse(unb64u(body).toString('utf8')); return typeof p.exp === 'number' && p.exp > Date.now() ? p : null } catch { return null }
}
export async function signSession(m) { const now = Date.now(); return sign({ sub: Number(m.id), role: m.role, email: m.email, iat: now, exp: now + SESSION_TTL }); }
export async function readSession(tok) { const p = await open(tok); return p && !p.kind ? p : null; }
export async function signPurpose(sub, kind, bind) { const now = Date.now(); return sign({ sub, kind, bind, iat: now, exp: now + (kind === 'verify' ? VERIFY_TTL : RESET_TTL) }); }
export async function readPurpose(tok, kind) { const p = await open(tok); return p && p.kind === kind ? p : null; }

/* ---------- admin seed (env 비밀번호 → 해시만 DB 저장, 평문 미보관) ---------- */
let seeded = false;
export async function seedAdmin() {
  if (seeded) return; seeded = true;
  const pw = (process.env.ADMIN_PASSWORD || '').trim(); const ex = await memberByEmail(ADMIN_EMAIL);
  if (ex) {
    if (ex.role === 'admin' && (ex.status !== 'active' || !ex.email_verified)) await q("UPDATE sd_members SET status='active', email_verified=TRUE WHERE id=$1", [ex.id]);
    /* 복구: Vercel에 ADMIN_RESYNC=1 을 넣고 재배포하면 ADMIN_PASSWORD 값으로 최고관리자 비밀번호를 다시 맞춤(복구 후 ADMIN_RESYNC 삭제) */
    if (ex.role === 'admin' && pw && process.env.ADMIN_RESYNC === '1' && !verifyPassword(pw, ex.pw_hash, ex.pw_salt)) {
      const { hash, salt } = hashPassword(pw); await q('UPDATE sd_members SET pw_hash=$1, pw_salt=$2 WHERE id=$3', [hash, salt, ex.id]); console.log('admin password resynced from ADMIN_PASSWORD'); }
    return; }
  if (!pw) { seeded = false; return; }   /* ADMIN_PASSWORD 설정 전: 최고관리자 미생성(다음 요청에서 재시도) */
  const { hash, salt } = hashPassword(pw);
  await q(`INSERT INTO sd_members(email,pw_hash,pw_salt,name,phone,org,role,status,email_verified,created_at)
           VALUES($1,$2,$3,'여승훈','-','NanoHydroIn','admin','active',TRUE,$4) ON CONFLICT (email) DO NOTHING`, [ADMIN_EMAIL, hash, salt, Date.now()]);
}

/* ---------- profile ---------- */
export function profile(m) { return { id: Number(m.id), email: m.email, name: m.name, phone: m.phone, org: m.org, memo: m.memo, role: m.role, status: m.status,
  emailVerified: !!m.email_verified, createdAt: Number(m.created_at), lastLogin: m.last_login == null ? null : Number(m.last_login), lastIp: m.last_ip || null, superAdmin: m.email === ADMIN_EMAIL }; }

/* ---------- rate limit (인스턴스 메모리, 근사 방어) ---------- */
const buckets = new Map();
export function limited(key, n, win = 60e3) { const now = Date.now(); if (buckets.size > 5000) for (const [k, v] of buckets) if (v.r < now) buckets.delete(k);
  const b = buckets.get(key); if (!b || b.r < now) { buckets.set(key, { c: 1, r: now + win }); return false } b.c++; return b.c > n; }

/* ---------- mail ---------- */
export function mailEnabled() { return Boolean(process.env.MAIL_USER && process.env.MAIL_APP_PASSWORD); }
let tx = null; export const sentMail = [];   /* 테스트용 기록 */
async function send(to, subject, html) {
  if (globalThis.__SD_TEST_MAIL) { sentMail.push({ to, subject, html }); return true; }
  if (!mailEnabled()) return false;
  try { tx = tx || nodemailer.createTransport({ service: 'gmail', auth: { user: process.env.MAIL_USER, pass: process.env.MAIL_APP_PASSWORD } });
    const info = await tx.sendMail({ from: `NanoHydroIn 상동호수공원 DT <${process.env.MAIL_FROM || process.env.MAIL_USER}>`, to, subject, html }); console.log('mail sent', subject.slice(0, 40), info && info.response); kvSet('last_mail', JSON.stringify({ t: Date.now(), ok: true, r: String(info && info.response || '').slice(0, 60) })).catch(() => {}); return true; }
  catch (e) { console.error('mail send failed', e && e.message); tx = null; kvSet('last_mail', JSON.stringify({ t: Date.now(), ok: false, r: String(e && e.message || '').slice(0, 90) })).catch(() => {}); return false; }
}
export function mailOn() { return Boolean(globalThis.__SD_TEST_MAIL) || mailEnabled(); }
const esc = s => String(s).replace(/[&<>"]/g, c => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c]));
function shell(title, inner, cta) {
  return `<div style="font-family:-apple-system,Segoe UI,Roboto,'Malgun Gothic',sans-serif;background:#eef4f5;padding:28px 0">
  <div style="max-width:480px;margin:0 auto;background:#07161c;border-radius:14px;overflow:hidden;border:1px solid #12323a">
  <div style="padding:22px 26px 6px;text-align:center"><div style="font-size:11px;letter-spacing:.28em;color:#7fe3ff;font-weight:700">NANOHYDROIN CO.,LTD.</div>
  <div style="font-size:16px;color:#fff;font-weight:700;margin-top:6px">상동호수공원 디지털트윈 · NHI PhotoNano</div></div>
  <div style="padding:8px 30px 24px;color:#c9d9de;font-size:14px;line-height:1.7"><h2 style="color:#fff;font-size:17px;margin:14px 0 10px">${title}</h2>${inner}
  ${cta ? `<div style="text-align:center;margin:24px 0 8px"><a href="${cta.url}" style="display:inline-block;background:#8fe6ff;color:#04202a;font-weight:700;text-decoration:none;padding:12px 26px;border-radius:10px">${cta.label}</a></div>
  <p style="font-size:11px;color:#7fa3b0">버튼이 안 되면 주소를 붙여넣으세요 / If the button fails, paste this URL:<br><span style="color:#8fe6ff;word-break:break-all">${cta.url}</span></p>` : ''}</div>
  <div style="padding:12px 26px;background:#04100f;color:#5b6e77;font-size:10px;text-align:center">© 2026 주식회사 나노하이드로인 (NanoHydroIn Co., Ltd.) · All rights reserved</div></div></div>`;
}
export function mailVerify(to, name, url) { return send(to, '[NanoHydroIn] 이메일 인증 / Email verification',
  shell('이메일 인증을 완료해 주세요', `<p>${esc(name)}님, 가입해 주셔서 감사합니다. 아래 버튼으로 이메일 인증을 완료하세요(24시간 유효). 인증 후 관리자 승인이 끝나면 로그인할 수 있습니다.</p><p style="color:#8aa">Please verify your email (valid 24 h). You can sign in once an administrator approves your account.</p>`, { url, label: '이메일 인증하기 / Verify' })); }
export function mailReset(to, name, url) { return send(to, '[NanoHydroIn] 비밀번호 재설정 / Password reset',
  shell('비밀번호 재설정', `<p>${esc(name)}님, 비밀번호 재설정을 요청하셨습니다. 아래 버튼으로 새 비밀번호를 설정하세요(1시간 유효). 본인이 요청하지 않았다면 이 메일을 무시하세요.</p><p style="color:#8aa">Reset your password (link valid 1 h). Ignore this mail if you did not request it.</p>`, { url, label: '비밀번호 재설정 / Reset' })); }
export function mailAdminNotice(m, url) { return send(ADMIN_EMAIL, `[NanoHydroIn] 신규 가입 승인 요청: ${m.name}`,
  shell('신규 회원 가입 — 승인 대기', `<p>${esc(m.name)} (${esc(m.email)}) · ${esc(m.org || '-')} · ${esc(m.phone || '-')}</p><p>${esc(m.memo || '')}</p><p>관리자 패널 ‘접속자 관리 → 회원’에서 승인하세요.</p>`, { url, label: '관리자 패널 열기' })); }
export function mailApproved(to, name, url) { return send(to, '[NanoHydroIn] 가입 승인 완료 / Account approved',
  shell('가입이 승인되었습니다', `<p>${esc(name)}님, 회원 가입이 승인되었습니다. 이제 로그인할 수 있습니다.</p><p style="color:#8aa">Your account has been approved. You can now sign in.</p>`, { url, label: '로그인 / Sign in' })); }

/* ---------- session guard ---------- */
export async function currentMember(req) {
  const p = await readSession(bearer(req)); if (!p) return null;
  const r = await q('SELECT * FROM sd_members WHERE id=$1', [p.sub]); const m = r.rows[0];
  return m && m.status === 'active' ? m : null;
}
export async function requireAdmin(req, res) {
  const m = await currentMember(req);
  if (!m) { fail(res, 401, 'UNAUTHORIZED', '로그인이 필요합니다.'); return null; }
  if (m.role !== 'admin' || m.email !== ADMIN_EMAIL) { fail(res, 403, 'FORBIDDEN', '최고관리자만 접근할 수 있습니다.'); return null; }
  return m;
}
