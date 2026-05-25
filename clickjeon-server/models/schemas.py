from typing import Literal
from pydantic import BaseModel, Field


class SearchResult(BaseModel):
    rank: int
    url: str = Field(..., max_length=2048)
    domain: str = Field(..., max_length=253)
    title: str = Field(..., max_length=300)
    snippet: str = Field("", max_length=500)
    is_ad: bool = False


class VendorMatch(BaseModel):
    id: str
    official_domains: list[str]


class AnalyzeRequest(BaseModel):
    query: str = Field(..., max_length=200)
    results: list[SearchResult] = Field(..., max_length=30)
    vendor_match: VendorMatch | None = None


class ResultGrade(BaseModel):
    rank: int
    domain: str = ""
    grade: Literal["OFFICIAL", "TRUSTED", "WARNING", "DANGER", "UNKNOWN"]
    reason: str
    vt_malicious: int = 0
    vt_total: int = 0
    domain_age_days: int | None = None


class AnalyzeResponse(BaseModel):
    official_domain: str | None
    results: list[ResultGrade]
    cached: bool = False
