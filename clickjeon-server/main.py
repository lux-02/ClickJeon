from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from routers.analyze import router as analyze_router
from utils.rate_limit import get_client_ip

limiter = Limiter(key_func=get_client_ip)

app = FastAPI(title="ClickJeon API")
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

app.add_middleware(
    CORSMiddleware,
    allow_origin_regex=r"chrome-extension://[a-z]+",
    allow_methods=["POST", "GET"],
    allow_headers=["Content-Type"],
)

app.include_router(analyze_router)

_LANDING_HTML = """<!DOCTYPE html>
<html lang="ko">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>클릭전 — 검색 결과를 클릭하기 전에, AI가 먼저 확인합니다</title>
  <meta name="description" content="구글 검색 결과에서 피싱·우회 광고를 찾아내고 수상한 링크를 블러 처리해 실수 클릭을 막는 Chrome / 네이버 웨일 확장 프로그램">
  <style>
    *, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }
    :root {
      --bg: #0d1117; --surface: #161b22; --border: #30363d;
      --text: #e6edf3; --muted: #8b949e;
      --green: #3fb950; --blue: #58a6ff; --yellow: #d29922;
      --orange: #f0883e; --red: #f85149; --accent: #3fb950;
    }
    html { scroll-behavior: smooth; }
    body { background: var(--bg); color: var(--text); font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif; line-height: 1.6; }
    nav {
      position: sticky; top: 0; z-index: 100;
      background: rgba(13,17,23,0.85); backdrop-filter: blur(12px);
      border-bottom: 1px solid var(--border);
      padding: 0 24px; display: flex; align-items: center; justify-content: space-between; height: 56px;
    }
    .nav-logo { font-weight: 700; font-size: 1rem; color: var(--text); text-decoration: none; display: flex; align-items: center; gap: 8px; }
    .nav-logo span { color: var(--accent); }
    .nav-links { display: flex; gap: 24px; }
    .nav-links a { color: var(--muted); text-decoration: none; font-size: 0.9rem; transition: color 0.15s; }
    .nav-links a:hover { color: var(--text); }
    .hero { text-align: center; padding: 96px 24px 80px; max-width: 800px; margin: 0 auto; }
    .hero-badge {
      display: inline-flex; align-items: center; gap: 6px;
      background: rgba(63,185,80,0.1); border: 1px solid rgba(63,185,80,0.3);
      border-radius: 20px; padding: 4px 14px; font-size: 0.8rem; color: var(--green); margin-bottom: 28px;
    }
    .hero-badge::before { content: '●'; font-size: 0.5rem; }
    .hero h1 { font-size: clamp(2rem, 5vw, 3.2rem); font-weight: 800; line-height: 1.2; letter-spacing: -0.02em; margin-bottom: 20px; }
    .hero h1 em { font-style: normal; color: var(--accent); }
    .hero p { font-size: 1.1rem; color: var(--muted); max-width: 560px; margin: 0 auto 40px; }
    .cta-group { display: flex; gap: 12px; justify-content: center; flex-wrap: wrap; }
    .btn { display: inline-flex; align-items: center; gap: 8px; padding: 12px 24px; border-radius: 8px; font-size: 0.95rem; font-weight: 600; text-decoration: none; transition: all 0.15s; cursor: pointer; border: none; }
    .btn-primary { background: var(--accent); color: #0d1117; border: 1px solid var(--accent); }
    .btn-primary:hover { background: #2ea043; border-color: #2ea043; }
    .btn-secondary { background: transparent; color: var(--text); border: 1px solid var(--border); }
    .btn-secondary:hover { background: var(--surface); border-color: var(--muted); }
    .btn svg { width: 18px; height: 18px; }
    section { padding: 80px 24px; max-width: 960px; margin: 0 auto; }
    .section-label { font-size: 0.78rem; font-weight: 600; letter-spacing: 0.1em; text-transform: uppercase; color: var(--accent); margin-bottom: 12px; }
    .section-title { font-size: clamp(1.4rem, 3vw, 2rem); font-weight: 700; margin-bottom: 12px; }
    .section-desc { color: var(--muted); max-width: 520px; margin-bottom: 48px; }
    .grade-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(160px, 1fr)); gap: 12px; }
    .grade-card { background: var(--surface); border: 1px solid var(--border); border-radius: 10px; padding: 20px 16px; }
    .grade-badge { display: inline-flex; align-items: center; gap: 6px; padding: 3px 10px; border-radius: 6px; font-size: 0.78rem; font-weight: 700; margin-bottom: 10px; }
    .grade-official  { background: rgba(63,185,80,0.15);  color: var(--green);  border: 1px solid rgba(63,185,80,0.3); }
    .grade-trusted   { background: rgba(88,166,255,0.15); color: var(--blue);   border: 1px solid rgba(88,166,255,0.3); }
    .grade-unknown   { background: rgba(210,153,34,0.15); color: var(--yellow); border: 1px solid rgba(210,153,34,0.3); }
    .grade-warning   { background: rgba(240,136,62,0.15); color: var(--orange); border: 1px solid rgba(240,136,62,0.3); }
    .grade-danger    { background: rgba(248,81,73,0.15);  color: var(--red);    border: 1px solid rgba(248,81,73,0.3); }
    .grade-card h3 { font-size: 0.88rem; font-weight: 600; margin-bottom: 4px; }
    .grade-card p  { font-size: 0.8rem; color: var(--muted); }
    .screenshot-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 16px; }
    .screenshot-grid .wide { grid-column: 1 / -1; }
    .screenshot-card { background: var(--surface); border: 1px solid var(--border); border-radius: 12px; overflow: hidden; }
    .screenshot-card img { width: 100%; height: auto; display: block; }
    .screenshot-card figcaption { padding: 12px 16px; font-size: 0.82rem; color: var(--muted); border-top: 1px solid var(--border); }
    .steps { display: flex; flex-direction: column; gap: 20px; }
    .step { display: flex; gap: 20px; align-items: flex-start; }
    .step-num { flex-shrink: 0; width: 32px; height: 32px; background: rgba(63,185,80,0.1); border: 1px solid rgba(63,185,80,0.3); border-radius: 50%; display: flex; align-items: center; justify-content: center; font-size: 0.85rem; font-weight: 700; color: var(--accent); }
    .step-body h3 { font-size: 0.95rem; font-weight: 600; margin-bottom: 4px; }
    .step-body p  { font-size: 0.88rem; color: var(--muted); }
    hr { border: none; border-top: 1px solid var(--border); margin: 0; }
    footer { text-align: center; padding: 40px 24px; font-size: 0.82rem; color: var(--muted); border-top: 1px solid var(--border); }
    footer a { color: var(--muted); text-decoration: none; }
    footer a:hover { color: var(--text); }
    footer .links { display: flex; justify-content: center; gap: 24px; margin-top: 8px; }
    @media (max-width: 600px) { .screenshot-grid { grid-template-columns: 1fr; } .screenshot-grid .wide { grid-column: 1; } }
  </style>
</head>
<body>
<nav>
  <a class="nav-logo" href="/">클릭<span>전</span></a>
  <div class="nav-links">
    <a href="#grades">등급</a>
    <a href="#screenshots">스크린샷</a>
    <a href="#how">사용법</a>
    <a href="https://github.com/lux-02/ClickJeon" target="_blank">GitHub</a>
  </div>
</nav>
<div class="hero">
  <div class="hero-badge">Chrome · 네이버 웨일 확장 프로그램</div>
  <h1>검색 결과를 클릭하기 전에,<br><em>AI가 먼저 확인합니다</em></h1>
  <p>구글 검색 결과에서 피싱이나 우회 광고를 찾아내고, 수상한 링크는 흐릿하게 보여 실수로 누르는 일을 막습니다.</p>
  <div class="cta-group">
    <a class="btn btn-primary" href="https://chromewebstore.google.com/detail/inopiebmhgffoijdijpimkbmkicbeejh" target="_blank">
      <img src="https://raw.githubusercontent.com/lux-02/ClickJeon/main/clickjeon-extension/icons/icon-48.png" width="20" height="20" alt="클릭전 아이콘" style="border-radius:4px">
      Chrome에 설치
    </a>
    <a class="btn btn-secondary" href="https://store.whale.naver.com/detail/nhpnnlhomdaheccmmcoikdmaacicmbbj" target="_blank">
      <svg viewBox="0 0 24 24" fill="currentColor"><path d="M12 2C6.477 2 2 6.477 2 12s4.477 10 10 10 10-4.477 10-10S17.523 2 12 2zm0 1.5c4.687 0 8.5 3.813 8.5 8.5S16.687 20.5 12 20.5 3.5 16.187 3.5 12 7.313 3.5 12 3.5zm-1 3v2.25L8.75 10H7v4h1.75l2.25 1.25V17.5l4-5.5-4-5.5z"/></svg>
      웨일에 설치
    </a>
    <a class="btn btn-secondary" href="https://github.com/lux-02/ClickJeon" target="_blank">
      <svg viewBox="0 0 24 24" fill="currentColor"><path d="M12 0C5.37 0 0 5.37 0 12c0 5.31 3.435 9.795 8.205 11.385.6.105.825-.255.825-.57 0-.285-.015-1.23-.015-2.235-3.015.555-3.795-.735-4.035-1.41-.135-.345-.72-1.41-1.23-1.695-.42-.225-1.02-.78-.015-.795.945-.015 1.62.87 1.845 1.23 1.08 1.815 2.805 1.305 3.495.99.105-.78.42-1.305.765-1.605-2.67-.3-5.46-1.335-5.46-5.925 0-1.305.465-2.385 1.23-3.225-.12-.3-.54-1.53.12-3.18 0 0 1.005-.315 3.3 1.23.96-.27 1.98-.405 3-.405s2.04.135 3 .405c2.295-1.56 3.3-1.23 3.3-1.23.66 1.65.24 2.88.12 3.18.765.84 1.23 1.905 1.23 3.225 0 4.605-2.805 5.625-5.475 5.925.435.375.81 1.095.81 2.22 0 1.605-.015 2.895-.015 3.3 0 .315.225.69.825.57A12.02 12.02 0 0024 12c0-6.63-5.37-12-12-12z"/></svg>
      GitHub 소스 보기
    </a>
  </div>
</div>
<hr>
<section id="grades">
  <div class="section-label">신뢰도 등급</div>
  <h2 class="section-title">공식·위험·광고, 배지로 바로 구분됩니다</h2>
  <p class="section-desc">도메인과 검색 의도를 바탕으로 각 결과에 등급을 표시합니다.</p>
  <div class="grade-grid">
    <div class="grade-card"><span class="grade-badge grade-official">공식 배포처</span><h3>OFFICIAL</h3><p>검색 키워드의 공식 도메인 또는 공식 앱스토어</p></div>
    <div class="grade-card"><span class="grade-badge grade-trusted">신뢰할 수 있음</span><h3>TRUSTED</h3><p>나무위키, GitHub 등 공인된 신뢰 플랫폼</p></div>
    <div class="grade-card"><span class="grade-badge grade-unknown">알 수 없음</span><h3>UNKNOWN</h3><p>블로그·커뮤니티 등 신뢰도 불명확</p></div>
    <div class="grade-card"><span class="grade-badge grade-warning">주의</span><h3>WARNING</h3><p>비공식 배포처, 경쟁사 우회 광고</p></div>
    <div class="grade-card"><span class="grade-badge grade-danger">위험</span><h3>DANGER</h3><p>공식 브랜드 사칭, SEO 포이즈닝 의심 도메인</p></div>
  </div>
</section>
<hr>
<section id="screenshots">
  <div class="section-label">스크린샷</div>
  <h2 class="section-title">실제 동작 화면</h2>
  <p class="section-desc">카카오톡이나 클로드 같은 실제 검색에서 피싱과 사칭 사이트가 어떻게 걸러졌는지 확인해 보세요.</p>
  <div class="screenshot-grid">
    <figure class="screenshot-card">
      <img src="https://raw.githubusercontent.com/lux-02/ClickJeon/main/docs/screenshots/popup.png" alt="확장 팝업" loading="lazy">
      <figcaption>팝업 — "지금 분석하기" 버튼 하나로 시작</figcaption>
    </figure>
    <figure class="screenshot-card">
      <img src="https://raw.githubusercontent.com/lux-02/ClickJeon/main/docs/screenshots/loading-overlay.png" alt="분석 중 오버레이" loading="lazy">
      <figcaption>분석 중 — 전체 화면 오버레이로 실수 클릭 차단</figcaption>
    </figure>
    <figure class="screenshot-card wide">
      <img src="https://raw.githubusercontent.com/lux-02/ClickJeon/main/docs/screenshots/kakao-official.png" alt="카카오톡 공식 배포처" loading="lazy">
      <figcaption>카카오톡 검색 — App Store·Google Play·공식 도메인은 <strong style="color:var(--green)">공식 배포처</strong></figcaption>
    </figure>
    <figure class="screenshot-card">
      <img src="https://raw.githubusercontent.com/lux-02/ClickJeon/main/docs/screenshots/kakao-warning-softonic.png" alt="Softonic 주의" loading="lazy">
      <figcaption>Softonic — <strong style="color:var(--orange)">주의</strong> 배지와 블러 처리</figcaption>
    </figure>
    <figure class="screenshot-card">
      <img src="https://raw.githubusercontent.com/lux-02/ClickJeon/main/docs/screenshots/claude-multi-grade.png" alt="복합 등급" loading="lazy">
      <figcaption>클로드 검색 — 위험·주의·공식 복합 표시</figcaption>
    </figure>
  </div>
</section>
<hr>
<section id="how">
  <div class="section-label">사용 방법</div>
  <h2 class="section-title">설치 후 버튼 하나로 바로 분석 시작</h2>
  <p class="section-desc">Chrome 웹스토어 또는 네이버 웨일 스토어에서 바로 설치할 수 있습니다.</p>
  <div class="steps">
    <div class="step"><div class="step-num">1</div><div class="step-body"><h3>브라우저에 설치하기</h3><p><a href="https://chromewebstore.google.com/detail/inopiebmhgffoijdijpimkbmkicbeejh" target="_blank" style="color:var(--accent)">Chrome 웹스토어</a> 또는 <a href="https://store.whale.naver.com/detail/nhpnnlhomdaheccmmcoikdmaacicmbbj" target="_blank" style="color:var(--accent)">네이버 웨일 스토어</a>에서 클릭전을 설치합니다.</p></div></div>
    <div class="step"><div class="step-num">2</div><div class="step-body"><h3>검색 후 아이콘을 눌러 분석 시작</h3><p>원하는 키워드를 검색한 뒤, 툴바의 클릭전 아이콘을 클릭하고 "지금 분석하기"를 누릅니다.</p></div></div>
    <div class="step"><div class="step-num">3</div><div class="step-body"><h3>배지 확인 후 링크 방문</h3><p>AI 분석이 완료되면 각 결과에 등급 배지가 표시됩니다. 블러 처리된 결과는 클릭해서 내용을 확인할 수 있습니다.</p></div></div>
  </div>
</section>
<hr>
<footer>
  <div>© 2026 클릭전 (ClickJeon) · MIT License</div>
  <div class="links">
    <a href="https://chromewebstore.google.com/detail/inopiebmhgffoijdijpimkbmkicbeejh" target="_blank">Chrome 웹스토어</a>
    <a href="https://store.whale.naver.com/detail/nhpnnlhomdaheccmmcoikdmaacicmbbj" target="_blank">웨일 스토어</a>
    <a href="https://github.com/lux-02/ClickJeon" target="_blank">GitHub</a>
    <a href="/privacy">개인정보처리방침</a>
  </div>
</footer>
</body>
</html>"""

_PRIVACY_HTML = """<!DOCTYPE html>
<html lang="ko">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>클릭전 개인정보처리방침</title>
  <style>
    body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
           max-width: 720px; margin: 48px auto; padding: 0 24px;
           color: #1a1a1a; line-height: 1.7; }
    h1 { font-size: 1.6rem; margin-bottom: 8px; }
    h2 { font-size: 1.1rem; margin-top: 36px; }
    p, li { font-size: 0.95rem; color: #333; }
    footer { margin-top: 48px; font-size: 0.85rem; color: #888; }
  </style>
</head>
<body>
  <h1>클릭전 (ClickJeon) 개인정보처리방침</h1>
  <p>시행일: 2026년 5월 25일</p>
  <h2>1. 수집하는 정보</h2>
  <p>클릭전은 다음 정보를 일시적으로 처리합니다.</p>
  <ul>
    <li><strong>구글 검색어</strong>: 분석 요청 시 서버로 전송됩니다.</li>
    <li><strong>검색 결과 메타데이터</strong>: 결과 제목, URL, 도메인, 스니펫(검색 결과 요약 텍스트)</li>
  </ul>
  <p>이름, 이메일, 계정 정보 등 개인 식별 정보는 수집하지 않습니다.</p>
  <h2>2. 정보 이용 목적</h2>
  <p>수집된 정보는 오직 <strong>SEO 포이즈닝 및 악성 사이트 탐지</strong> 목적으로만 사용됩니다.
  분석 결과는 Redis 캐시에 최대 30분간 보관 후 자동 삭제됩니다.</p>
  <h2>3. 제3자 제공</h2>
  <p>분석을 위해 다음 서비스에 데이터가 전달됩니다.</p>
  <ul>
    <li><strong>OpenAI API</strong>: 검색어 및 결과 메타데이터 (신뢰도 분석)</li>
    <li><strong>Upstash Redis</strong>: 분석 결과 캐시 저장</li>
  </ul>
  <p>이 외 제3자에게 데이터를 판매하거나 제공하지 않습니다.</p>
  <h2>4. 데이터 보관 기간</h2>
  <p>검색 결과 분석 캐시는 30분 후 자동 삭제됩니다. 별도의 영구 저장소를 운영하지 않습니다.</p>
  <h2>5. 사용자 권리</h2>
  <p>본 확장 프로그램은 분석 요청 시에만 데이터를 전송하며, 백그라운드에서 자동으로 데이터를 수집하지 않습니다.
  확장 프로그램을 제거하면 모든 처리가 중단됩니다.</p>
  <h2>6. 문의</h2>
  <p>개인정보 관련 문의: <a href="https://github.com/lux-02/ClickJeon/issues">GitHub Issues</a></p>
  <footer>© 2026 lux-02 · <a href="https://clickjeon.n2f.site/privacy">clickjeon.n2f.site/privacy</a></footer>
</body>
</html>"""


@app.get("/", response_class=HTMLResponse)
async def landing():
    return _LANDING_HTML


@app.get("/health")
async def health():
    return {"status": "ok"}


@app.get("/privacy", response_class=HTMLResponse)
async def privacy():
    return _PRIVACY_HTML
