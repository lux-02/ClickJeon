import pytest
import httpx
from unittest.mock import patch

from main import app

SAMPLE_REQUEST = {
    "query": "카카오톡 다운로드",
    "results": [
        {"rank": 1, "url": "https://kakao.com", "domain": "kakao.com",
         "title": "카카오톡", "snippet": "공식"},
        {"rank": 2, "url": "https://kakaotalk-download.net",
         "domain": "kakaotalk-download.net", "title": "카카오톡 설치", "snippet": "빠른 설치"},
    ],
    "vendor_match": {"id": "kakaotalk", "official_domains": ["kakao.com"]},
}

MOCK_VT = {"domain": "kakao.com", "malicious": 0, "total_engines": 89, "domain_age_days": 4000}
MOCK_GPT = {
    "official_domain": "kakao.com",
    "results": [
        {"rank": 1, "grade": "OFFICIAL", "reason": "공식 도메인"},
        {"rank": 2, "grade": "DANGER", "reason": "비공식 타이포스쿼팅"},
    ],
}


async def test_analyze_success():
    with (
        patch("routers.analyze.cache_get", return_value=None),
        patch("routers.analyze.cache_set"),
        patch("routers.analyze.get_domain_report", return_value=MOCK_VT),
        patch("routers.analyze.analyze_results", return_value=MOCK_GPT),
    ):
        async with httpx.AsyncClient(
            transport=httpx.ASGITransport(app=app), base_url="http://test"
        ) as ac:
            response = await ac.post("/analyze", json=SAMPLE_REQUEST)

    assert response.status_code == 200
    data = response.json()
    assert data["official_domain"] == "kakao.com"
    assert data["results"][0]["grade"] == "OFFICIAL"
    assert data["results"][1]["grade"] == "DANGER"
    assert data["cached"] is False


async def test_analyze_returns_cached():
    cached_response = {
        "official_domain": "kakao.com",
        "results": [{"rank": 1, "grade": "OFFICIAL", "reason": "캐시됨",
                     "vt_malicious": 0, "vt_total": 89, "domain_age_days": None}],
        "cached": True,
    }

    with patch("routers.analyze.cache_get", return_value=cached_response):
        async with httpx.AsyncClient(
            transport=httpx.ASGITransport(app=app), base_url="http://test"
        ) as ac:
            response = await ac.post("/analyze", json=SAMPLE_REQUEST)

    assert response.status_code == 200
    assert response.json()["cached"] is True


async def test_analyze_vt_failure_still_returns():
    with (
        patch("routers.analyze.cache_get", return_value=None),
        patch("routers.analyze.cache_set"),
        patch("routers.analyze.get_domain_report", side_effect=Exception("VT down")),
        patch("routers.analyze.analyze_results", return_value=MOCK_GPT),
    ):
        async with httpx.AsyncClient(
            transport=httpx.ASGITransport(app=app), base_url="http://test"
        ) as ac:
            response = await ac.post("/analyze", json=SAMPLE_REQUEST)

    assert response.status_code == 200


async def test_analyze_invalid_request():
    async with httpx.AsyncClient(
        transport=httpx.ASGITransport(app=app), base_url="http://test"
    ) as ac:
        response = await ac.post("/analyze", json={"query": "test"})  # missing results

    assert response.status_code == 422
