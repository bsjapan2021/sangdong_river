# member-auth kit — 스플래시 · 회원 인증 · 최고관리자 접속자 관리

해미수산 · 상동호수공원 디지털트윈에서 검증된 회원 기능을 다른 프로젝트에 그대로 옮기기 위한 키트입니다.
스킬 `member-auth-access-admin`이 이 폴더를 기준으로 구현합니다.

| 경로 | 내용 |
|---|---|
| `lib/db.js`, `lib/auth.js` | Postgres 스키마·헬퍼, 토큰·scrypt·관리자 시드·메일·세션 가드 |
| `api/auth.js` · `admin.js` · `track.js` · `health.js` | Vercel 서버리스 API |
| `frontend/auth.css` · `auth.html` · `auth-i18n.js` · `auth.js` | 스플래시·로그인/가입/찾기/재설정/변경 카드·관리자 모달 |
| `example/index.html` | 위 4개를 합친 최소 예제 페이지 |
| `test/api.test.mjs` | pg-mem 기반 API 시나리오 테스트 (`npm i && node test/api.test.mjs`) |

자리표시자 `__APP_TITLE__`, `__APP_SUB__`, `__LOGO_URL__`, `__YEAR__`, `__BUILD__`를 프로젝트 값으로 바꾸고,
환경변수(DATABASE_URL, ADMIN_PASSWORD, MAIL_USER, MAIL_APP_PASSWORD …)는 Vercel에서 직접 등록합니다. 비밀번호를 코드에 넣지 마세요.
