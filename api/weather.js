/* /api/weather — OpenWeather 프록시(키는 서버 환경변수 OPENWEATHER_API_KEY 에만 둔다. 공개 번들 노출 금지)
   One Call 3.0(현재 + 8일 일간) 우선, 구독이 없으면 2.5 현재날씨 + 5일/3시간 예보를 일간으로 집계해 폴백.
   ?lang=ko|en|ja  →  { src, cur:{...}, daily:[{...}], tz } · 언어별 10분 캐시 */
import { ok, fail } from '../lib/auth.js';
const LAT = 37.5038, LON = 126.745, TTL = 600e3;
const cache = new Map();
const OWL = { ko: 'kr', en: 'en', ja: 'ja' };
async function j(url) { const r = await fetch(url, { signal: AbortSignal.timeout(8000) }); if (!r.ok) { const e = new Error('owm ' + r.status); e.status = r.status; throw e } return r.json() }
const w0 = w => (w && w[0]) || { id: 800, main: 'Clear', description: '', icon: '01d' };
function fromOneCall(d) {
  const c = d.current || {}, cw = w0(c.weather);
  return { src: 'onecall3', tz: d.timezone_offset ?? 32400,
    cur: { dt: c.dt * 1e3, id: cw.id, main: cw.main, desc: cw.description, icon: cw.icon, temp: c.temp, feels: c.feels_like, hum: c.humidity, wind: c.wind_speed, windDeg: c.wind_deg, clouds: c.clouds, vis: c.visibility,
      rain1h: (c.rain && c.rain['1h']) || 0, snow1h: (c.snow && c.snow['1h']) || 0, sunrise: c.sunrise * 1e3, sunset: c.sunset * 1e3 },
    daily: (d.daily || []).slice(0, 8).map(x => { const w = w0(x.weather); return { dt: x.dt * 1e3, id: w.id, main: w.main, desc: w.description, icon: w.icon, max: x.temp && x.temp.max, min: x.temp && x.temp.min, pop: x.pop ?? 0, rain: x.rain || 0, snow: x.snow || 0 } }) };
}
function fromV25(c, f) {
  const cw = w0(c.weather), tz = c.timezone ?? 32400, days = new Map();
  for (const x of f.list || []) { const key = new Date((x.dt + tz) * 1e3).toISOString().slice(0, 10); const d = days.get(key) || { dt: x.dt * 1e3, max: -99, min: 99, pop: 0, rain: 0, snow: 0, w: {} };
    d.max = Math.max(d.max, x.main.temp_max); d.min = Math.min(d.min, x.main.temp_min); d.pop = Math.max(d.pop, x.pop || 0);
    d.rain += (x.rain && x.rain['3h']) || 0; d.snow += (x.snow && x.snow['3h']) || 0;
    const w = w0(x.weather); const sev = w.id >= 800 ? (w.id === 800 ? 0 : 1) : 10 - Math.floor(w.id / 100); /* 강수 쪽 날씨를 대표로 */
    if (!d.rep || sev > d.rep.sev || (sev === d.rep.sev && x.sys && x.sys.pod === 'd')) d.rep = { sev, w }; days.set(key, d) }
  return { src: 'v25', tz,
    cur: { dt: c.dt * 1e3, id: cw.id, main: cw.main, desc: cw.description, icon: cw.icon, temp: c.main.temp, feels: c.main.feels_like, hum: c.main.humidity, wind: c.wind && c.wind.speed, windDeg: c.wind && c.wind.deg, clouds: c.clouds && c.clouds.all, vis: c.visibility,
      rain1h: (c.rain && c.rain['1h']) || 0, snow1h: (c.snow && c.snow['1h']) || 0, sunrise: c.sys.sunrise * 1e3, sunset: c.sys.sunset * 1e3 },
    daily: [...days.values()].slice(0, 6).map(d => ({ dt: d.dt, id: d.rep.w.id, main: d.rep.w.main, desc: d.rep.w.description, icon: d.rep.w.icon.replace('n', 'd'), max: d.max, min: d.min, pop: d.pop, rain: +d.rain.toFixed(1), snow: +d.snow.toFixed(1) })) };
}
export default async function handler(req, res) {
  const key = String(process.env.OPENWEATHER_API_KEY || '').trim();
  if (!key) return fail(res, 503, 'WEATHER_DISABLED', 'OPENWEATHER_API_KEY not configured');
  const lang = OWL[String((req.query && req.query.lang) || 'ko')] ? String(req.query.lang) : 'ko';
  const hit = cache.get(lang); if (hit && Date.now() - hit.t < TTL) return send(res, hit.v);
  const base = `https://api.openweathermap.org/data/`, qs = `lat=${LAT}&lon=${LON}&units=metric&lang=${OWL[lang]}&appid=${encodeURIComponent(key)}`;
  try {
    let v; try { v = fromOneCall(await j(`${base}3.0/onecall?${qs}&exclude=minutely,hourly,alerts`)) }
    catch (e) { if (e.status !== 401 && e.status !== 403 && e.status !== 404) throw e;
      const [c, f] = await Promise.all([j(`${base}2.5/weather?${qs}`), j(`${base}2.5/forecast?${qs}`)]); v = fromV25(c, f) }
    v.fetchedAt = Date.now(); cache.set(lang, { t: Date.now(), v }); return send(res, v);
  } catch (e) { if (hit) return send(res, hit.v); console.error('weather', e && e.message); return fail(res, 502, 'WEATHER_UPSTREAM', 'weather provider unavailable') }
}
function send(res, v) { res.setHeader('Cache-Control', 'public, s-maxage=300, stale-while-revalidate=600'); res.status(200).json({ success: true, data: v }) }
