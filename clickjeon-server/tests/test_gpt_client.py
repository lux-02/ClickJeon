import json
import pytest
from unittest.mock import AsyncMock, patch, MagicMock

from services.gpt_client import analyze_results

SAMPLE_RESULTS = [
    {"rank": 1, "url": "https://kakao.com", "domain": "kakao.com",
     "title": "카카오톡 공식", "snippet": "공식 다운로드"},
    {"rank": 2, "url": "https://kakaotalk-download.net",
     "domain": "kakaotalk-download.net",
     "title": "카카오톡 무료 설치", "snippet": "빠른 다운로드"},
]

SAMPLE_VT = {
    "kakao.com": {"malicious": 0, "total_engines": 89, "domain_age_days": 4000},
    "kakaotalk-download.net": {"malicious": 15, "total_engines": 89, "domain_age_days": 12},
}

MOCK_GPT_RESPONSE = {
    "official_domain": "kakao.com",
    "results": [
        {"rank": 1, "grade": "OFFICIAL", "reason": "공식 카카오 도메인"},
        {"rank": 2, "grade": "DANGER", "reason": "비공식 도메인, VT 15개 엔진 악성 탐지"},
    ],
}

@pytest.mark.asyncio
async def test_analyze_results_returns_grades():
    mock_completion = MagicMock()
    mock_completion.choices[0].message.content = json.dumps(MOCK_GPT_RESPONSE)

    with patch("services.gpt_client._client") as mock_client:
        mock_client.chat.completions.create = AsyncMock(return_value=mock_completion)
        result = await analyze_results(
            query="카카오톡 다운로드",
            results=SAMPLE_RESULTS,
            vendor_match={"id": "kakaotalk", "official_domains": ["kakao.com"]},
            vt_data=SAMPLE_VT,
        )

    assert result["official_domain"] == "kakao.com"
    assert len(result["results"]) == 2
    assert result["results"][0]["grade"] == "OFFICIAL"
    assert result["results"][1]["grade"] == "DANGER"

@pytest.mark.asyncio
async def test_analyze_results_no_vendor_match():
    mock_completion = MagicMock()
    mock_completion.choices[0].message.content = json.dumps({
        "official_domain": None,
        "results": [{"rank": 1, "grade": "UNKNOWN", "reason": "알 수 없음"}],
    })

    with patch("services.gpt_client._client") as mock_client:
        mock_client.chat.completions.create = AsyncMock(return_value=mock_completion)
        result = await analyze_results(
            query="unknown tool",
            results=[SAMPLE_RESULTS[0]],
            vendor_match=None,
            vt_data={},
        )

    assert result["official_domain"] is None
