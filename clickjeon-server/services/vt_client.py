import os
from datetime import datetime, timezone
import httpx

VT_BASE_URL = "https://www.virustotal.com/api/v3"


async def get_domain_report(domain: str) -> dict:
    api_key = os.environ["VT_API_KEY"].strip()
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"{VT_BASE_URL}/domains/{domain}",
            headers={"x-apikey": api_key},
            timeout=3.0,
        )
        response.raise_for_status()
        data = response.json()

    attrs = data["data"]["attributes"]
    stats = attrs.get("last_analysis_stats", {})
    total = sum(stats.values())

    creation_date = attrs.get("creation_date")
    domain_age_days = None
    if creation_date:
        age_seconds = datetime.now(timezone.utc).timestamp() - creation_date
        domain_age_days = int(age_seconds / 86400)

    return {
        "domain": domain,
        "malicious": stats.get("malicious", 0),
        "suspicious": stats.get("suspicious", 0),
        "harmless": stats.get("harmless", 0),
        "undetected": stats.get("undetected", 0),
        "total_engines": total,
        "domain_age_days": domain_age_days,
    }
