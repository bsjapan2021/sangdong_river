/* Postgres (Neon) — 회원·접속자·차단·설정 저장소. DATABASE_URL(또는 POSTGRES_URL) 미설정이면 회원 기능 비활성. */
import pg from 'pg';
let pool = null, ready = null;
export function dbUrl() { return process.env.DATABASE_URL || process.env.DATABASE_POSTGRES_URL || process.env.POSTGRES_URL || process.env.DATABASE_DATABASE_URL || ''; }
export function dbEnabled() { return Boolean(globalThis.__SD_TEST_POOL || dbUrl()); }
function getPool() {
  if (globalThis.__SD_TEST_POOL) return globalThis.__SD_TEST_POOL;
  if (!pool) pool = new pg.Pool({ connectionString: dbUrl(), max: 3, idleTimeoutMillis: 10000, ssl: /localhost|127\.0\.0\.1/.test(dbUrl()) ? false : { rejectUnauthorized: false } });
  return pool;
}
const SCHEMA = [
  `CREATE TABLE IF NOT EXISTS sd_members (id SERIAL PRIMARY KEY, email TEXT UNIQUE NOT NULL, pw_hash TEXT NOT NULL, pw_salt TEXT NOT NULL,
     name TEXT NOT NULL, phone TEXT NOT NULL DEFAULT '', org TEXT NOT NULL DEFAULT '', memo TEXT, role TEXT NOT NULL DEFAULT 'user',
     status TEXT NOT NULL DEFAULT 'pending', email_verified BOOLEAN NOT NULL DEFAULT FALSE, created_at BIGINT NOT NULL, last_login BIGINT, last_ip TEXT)`,
  `CREATE TABLE IF NOT EXISTS sd_kv (k TEXT PRIMARY KEY, v TEXT NOT NULL)`,
  `CREATE TABLE IF NOT EXISTS sd_visitors (ip TEXT PRIMARY KEY, ua TEXT NOT NULL DEFAULT '', member_email TEXT, member_name TEXT, member_role TEXT,
     country TEXT, city TEXT, first_seen BIGINT NOT NULL, last_seen BIGINT NOT NULL, hits INTEGER NOT NULL DEFAULT 0)`,
  `CREATE TABLE IF NOT EXISTS sd_blocked (ip TEXT PRIMARY KEY, reason TEXT, at BIGINT NOT NULL, by_email TEXT)`,
  `CREATE TABLE IF NOT EXISTS sd_reports (id SERIAL PRIMARY KEY, member_email TEXT NOT NULL, at BIGINT NOT NULL, ros BIGINT NOT NULL DEFAULT 0, data TEXT NOT NULL)`,
];
export async function q(sql, params = []) {
  if (!ready) ready = (async () => { for (const s of SCHEMA) await getPool().query(s); })().catch(e => { ready = null; throw e; });
  await ready;
  return getPool().query(sql, params);
}
export async function kvGet(k) { const r = await q('SELECT v FROM sd_kv WHERE k=$1', [k]); return r.rows[0] ? r.rows[0].v : null; }
export async function kvSet(k, v) { await q('INSERT INTO sd_kv(k,v) VALUES($1,$2) ON CONFLICT (k) DO UPDATE SET v=EXCLUDED.v', [k, v]); }
export async function memberByEmail(email) { const r = await q('SELECT * FROM sd_members WHERE email=$1', [email]); return r.rows[0] || null; }
export async function memberById(id) { const r = await q('SELECT * FROM sd_members WHERE id=$1', [id]); return r.rows[0] || null; }
export async function isIpBlocked(ip) { const r = await q('SELECT 1 FROM sd_blocked WHERE ip=$1', [ip]); return r.rows.length > 0; }
export function __resetForTests() { ready = null; }
