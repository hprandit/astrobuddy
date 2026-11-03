"""Web app: compute charts, teach rules, get analyses, correct them."""
from __future__ import annotations

import os
import threading
from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from pydantic import BaseModel

from jyotish.analyze import analyze
from jyotish.chart import chart_factors, chart_summary, compute_chart, current_dasha
from jyotish.knowledge import KnowledgeBase
from jyotish.parashari import aspects, functional_nature, yogas
from jyotish.places import search_places, utc_offset

kb = KnowledgeBase(os.environ.get("JYOTISH_DB", "data/jyotish.db"))
app = FastAPI(title="Jyotish Learning Assistant")
STATIC = Path(__file__).parent / "static"

# Load the city list in the background so the first lookup is instant.
threading.Thread(target=lambda: search_places("delhi"), daemon=True).start()


class BirthIn(BaseModel):
    name: str
    date: str
    time: str
    utc_offset: float | None = None   # hours; worked out from timezone when omitted
    latitude: float
    longitude: float
    place: str = ""
    timezone: str = ""                # IANA name, e.g. Asia/Kolkata


class RuleIn(BaseModel):
    condition: str
    interpretation: str
    topic: str = ""
    source: str = ""


class AnalyzeIn(BaseModel):
    chart_id: int
    question: str = ""


class CorrectionIn(BaseModel):
    analysis_id: int
    correction: str
    also_as_rule: RuleIn | None = None


def _chart(inp: dict):
    return compute_chart(inp["name"], inp["date"], inp["time"], inp["utc_offset"],
                         inp["latitude"], inp["longitude"])


@app.get("/")
def index():
    return FileResponse(STATIC / "index.html")


@app.post("/api/charts")
def new_chart(b: BirthIn):
    inp = b.model_dump()
    if b.timezone:
        inp["utc_offset"] = utc_offset(b.timezone, b.date, b.time)
    if inp["utc_offset"] is None:
        raise HTTPException(422, "Give a birth place (timezone) or a UTC offset.")
    c = _chart(inp)
    cid = kb.save_chart(b.name, inp)
    return {"id": cid, **_chart_view(c)}


@app.get("/api/charts")
def list_charts():
    return kb.charts()


@app.get("/api/charts/{chart_id}")
def get_chart(chart_id: int):
    row = kb.chart(chart_id)
    if not row:
        raise HTTPException(404)
    return {"id": chart_id, **_chart_view(_chart(row["input"]))}


def _chart_view(c):
    md, ad = current_dasha(c)
    return {"chart": c.to_dict(), "summary": chart_summary(c), "factors": chart_factors(c),
            "current_dasha": {"mahadasha": md, "antardasha": ad},
            "yogas": yogas(c), "functional": functional_nature(c), "aspects": aspects(c)}


@app.get("/api/places")
def places(q: str):
    return search_places(q)


@app.get("/api/rules")
def list_rules():
    return kb.rules()


@app.post("/api/rules")
def add_rule(r: RuleIn):
    return {"id": kb.add_rule(**r.model_dump())}


@app.put("/api/rules/{rule_id}")
def edit_rule(rule_id: int, r: RuleIn):
    kb.update_rule(rule_id, **r.model_dump())
    return {"ok": True}


@app.delete("/api/rules/{rule_id}")
def remove_rule(rule_id: int):
    kb.delete_rule(rule_id)
    return {"ok": True}


@app.post("/api/analyze")
def run_analysis(a: AnalyzeIn):
    row = kb.chart(a.chart_id)
    if not row:
        raise HTTPException(404)
    text, rules = analyze(_chart(row["input"]), kb, a.question)
    aid = kb.save_analysis(a.chart_id, a.question, text, [r["id"] for r in rules])
    return {"id": aid, "answer": text, "rules_used": rules}


@app.post("/api/corrections")
def correct(c: CorrectionIn):
    cid = kb.add_correction(c.analysis_id, c.correction)
    rid = kb.add_rule(**c.also_as_rule.model_dump()) if c.also_as_rule else None
    return {"id": cid, "rule_id": rid}


@app.get("/api/corrections")
def list_corrections():
    return kb.corrections(200)


@app.get("/api/export")
def export():
    return kb.export()
