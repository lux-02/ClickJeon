import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, HTMLResponse
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


@app.get("/")
async def landing():
    path = os.path.join(os.path.dirname(__file__), "public", "index.html")
    return FileResponse(path, media_type="text/html")


@app.get("/health")
async def health():
    return {"status": "ok"}


@app.get("/privacy", response_class=HTMLResponse)
async def privacy():
    return """<!DOCTYPE html>
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


