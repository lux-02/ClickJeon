import hashlib
import logging

from fastapi import APIRouter, HTTPException, Request
from slowapi import Limiter

from cache.kv_cache import cache_get, cache_set
from models.schemas import AnalyzeRequest, AnalyzeResponse, ResultGrade
from services.gpt_client import analyze_results
from utils.rate_limit import get_client_ip

logger = logging.getLogger("clickjeon")
router = APIRouter()
limiter = Limiter(key_func=get_client_ip)

GPT_TTL = 1800


async def _fetch_vt_cached(domain: str) -> dict:
    cached = cache_get(f"vt:{domain}")
    if cached:
        return cached
    try:
        data = await get_domain_report(domain)
        cache_set(f"vt:{domain}", data, VT_TTL)
        return data
    except Exception:
        return {"domain": domain, "malicious": 0, "total_engines": 0, "domain_age_days": None}


@router.post("/analyze", response_model=AnalyzeResponse)
@limiter.limit("10/minute")
async def analyze(request: Request, body: AnalyzeRequest):
    try:
        query_hash = hashlib.md5(body.query.encode()).hexdigest()
        cached = cache_get(f"gpt:{query_hash}")
        if cached:
            return AnalyzeResponse.model_validate({**cached, "cached": True})

        vt_data = {r.domain: {"domain": r.domain, "malicious": 0, "total_engines": 0, "domain_age_days": None} for r in body.results}

        results_list = [r.model_dump() for r in body.results]
        vendor_dict = body.vendor_match.model_dump() if body.vendor_match else None
        gpt_response = await analyze_results(body.query, results_list, vendor_dict, vt_data)

        grade_map = {r["rank"]: r for r in gpt_response.get("results", [])}
        result_grades = []
        for r in body.results:
            grade_info = grade_map.get(r.rank, {})
            vt = vt_data.get(r.domain, {})
            result_grades.append(
                ResultGrade(
                    rank=r.rank,
                    domain=r.domain,
                    grade=grade_info.get("grade", "UNKNOWN"),
                    reason=grade_info.get("reason", ""),
                    vt_malicious=vt.get("malicious", 0),
                    vt_total=vt.get("total_engines", 0),
                    domain_age_days=vt.get("domain_age_days"),
                )
            )

        response_data = AnalyzeResponse(
            official_domain=gpt_response.get("official_domain"),
            results=result_grades,
            cached=False,
        )
        cache_set(f"gpt:{query_hash}", response_data.model_dump(), GPT_TTL)
        return response_data
    except Exception as e:
        logger.exception("analyze error")
        raise HTTPException(status_code=500, detail="분석 중 오류가 발생했습니다") from e
