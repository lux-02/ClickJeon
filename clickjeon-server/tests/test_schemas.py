import pytest
from pydantic import ValidationError
from models.schemas import AnalyzeRequest, SearchResult, VendorMatch


def test_analyze_request_valid():
    req = AnalyzeRequest(
        query="카카오톡 다운로드",
        results=[
            SearchResult(rank=1, url="https://kakao.com", domain="kakao.com",
                        title="카카오톡", snippet="공식")
        ],
        vendor_match=VendorMatch(id="kakaotalk", official_domains=["kakao.com"])
    )
    assert req.query == "카카오톡 다운로드"
    assert len(req.results) == 1


def test_analyze_request_no_vendor_match():
    req = AnalyzeRequest(
        query="unknown software",
        results=[SearchResult(rank=1, url="https://example.com",
                             domain="example.com", title="test", snippet="")]
    )
    assert req.vendor_match is None


def test_result_grade_valid():
    from models.schemas import ResultGrade
    grade = ResultGrade(rank=1, grade="OFFICIAL", reason="공식 도메인")
    assert grade.vt_malicious == 0
    assert grade.domain_age_days is None


def test_result_grade_invalid_grade():
    from models.schemas import ResultGrade
    with pytest.raises(ValidationError):
        ResultGrade(rank=1, grade="INVALID", reason="test")
