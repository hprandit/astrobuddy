"""Offline city lookup (GeoNames, towns of 5,000+ people) and historical UTC offsets."""
from __future__ import annotations

import unicodedata
from datetime import datetime
from functools import lru_cache
from zoneinfo import ZoneInfo


def _fold(s: str) -> str:
    return "".join(c for c in unicodedata.normalize("NFKD", s.lower()) if not unicodedata.combining(c))


@lru_cache(maxsize=1)
def _index() -> list[tuple[set[str], dict]]:
    import geonamescache
    gc = geonamescache.GeonamesCache(min_city_population=5000)
    countries = {k: v["name"] for k, v in gc.get_countries().items()}
    out = []
    for c in gc.get_cities().values():
        names = {_fold(c["name"])} | {_fold(a) for a in c.get("alternatenames", []) if a.isascii()}
        out.append((names, {"name": c["name"], "country": countries.get(c["countrycode"], c["countrycode"]),
                            "latitude": c["latitude"], "longitude": c["longitude"],
                            "timezone": c["timezone"], "population": c["population"]}))
    return out


def search_places(query: str, limit: int = 8) -> list[dict]:
    q = _fold(query.strip())
    if len(q) < 2:
        return []
    hits = []
    for names, city in _index():
        if q in names:
            hits.append((0, -city["population"], city))
        elif any(n.startswith(q) for n in names):
            hits.append((1, -city["population"], city))
    hits.sort(key=lambda h: h[:2])
    return [h[2] for h in hits[:limit]]


def utc_offset(timezone: str, date: str, time: str) -> float:
    """UTC offset in hours at that local moment, including historical DST/war time."""
    local = datetime.fromisoformat(f"{date}T{time}").replace(tzinfo=ZoneInfo(timezone))
    return local.utcoffset().total_seconds() / 3600
