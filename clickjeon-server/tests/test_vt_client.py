import pytest
import httpx
import respx
from datetime import datetime, timezone

from services.vt_client import get_domain_report

MOCK_VT_RESPONSE = {
    "data": {
        "attributes": {
            "last_analysis_stats": {
                "malicious": 10,
                "suspicious": 2,
                "harmless": 70,
                "undetected": 7,
            },
            "creation_date": int(datetime(2020, 1, 1, tzinfo=timezone.utc).timestamp()),
        }
    }
}

MOCK_VT_CLEAN = {
    "data": {
        "attributes": {
            "last_analysis_stats": {
                "malicious": 0,
                "suspicious": 0,
                "harmless": 85,
                "undetected": 4,
            },
            "creation_date": int(datetime(2010, 1, 1, tzinfo=timezone.utc).timestamp()),
        }
    }
}


async def test_get_domain_report_malicious():
    async with respx.mock as mock:
        mock.get("https://www.virustotal.com/api/v3/domains/malicious.com").mock(
            return_value=httpx.Response(200, json=MOCK_VT_RESPONSE)
        )
        result = await get_domain_report("malicious.com")
    assert result["domain"] == "malicious.com"
    assert result["malicious"] == 10
    assert result["total_engines"] == 89
    assert result["domain_age_days"] > 1000


async def test_get_domain_report_clean():
    async with respx.mock as mock:
        mock.get("https://www.virustotal.com/api/v3/domains/kakao.com").mock(
            return_value=httpx.Response(200, json=MOCK_VT_CLEAN)
        )
        result = await get_domain_report("kakao.com")
    assert result["malicious"] == 0
    assert result["total_engines"] == 89


async def test_get_domain_report_api_error():
    async with respx.mock as mock:
        mock.get("https://www.virustotal.com/api/v3/domains/error.com").mock(
            return_value=httpx.Response(404, json={"error": {"code": "NotFoundError"}})
        )
        with pytest.raises(Exception):
            await get_domain_report("error.com")
