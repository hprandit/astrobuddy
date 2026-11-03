"""The knowledge base you teach: rules, saved charts, analyses and corrections (SQLite)."""
from __future__ import annotations

import json
import re
import sqlite3
from datetime import datetime
from pathlib import Path

SCHEMA = """
CREATE TABLE IF NOT EXISTS rules (
  id INTEGER PRIMARY KEY, condition TEXT NOT NULL, interpretation TEXT NOT NULL,
  topic TEXT DEFAULT '', source TEXT DEFAULT '', created TEXT NOT NULL);
CREATE TABLE IF NOT EXISTS charts (
  id INTEGER PRIMARY KEY, name TEXT, input TEXT NOT NULL, created TEXT NOT NULL);
CREATE TABLE IF NOT EXISTS analyses (
  id INTEGER PRIMARY KEY, chart_id INTEGER, question TEXT, answer TEXT,
  rule_ids TEXT, created TEXT NOT NULL);
CREATE TABLE IF NOT EXISTS corrections (
  id INTEGER PRIMARY KEY, analysis_id INTEGER, chart_id INTEGER, correction TEXT NOT NULL,
  created TEXT NOT NULL);
"""

STOP = set("a an the of in on and or is are to for with by at as be it its this that from "
           "will gives give can may when if".split())


def _now() -> str:
    return datetime.now().isoformat(timespec="seconds")


def _words(text: str) -> set[str]:
    return {w for w in re.findall(r"[a-z0-9]+", text.lower()) if w not in STOP}


class KnowledgeBase:
    def __init__(self, path: str | Path = "data/jyotish.db"):
        Path(path).parent.mkdir(parents=True, exist_ok=True)
        self.db = sqlite3.connect(str(path), check_same_thread=False)
        self.db.row_factory = sqlite3.Row
        self.db.executescript(SCHEMA)

    # --- rules -------------------------------------------------------------
    def add_rule(self, condition: str, interpretation: str, topic="", source="") -> int:
        cur = self.db.execute(
            "INSERT INTO rules (condition, interpretation, topic, source, created) VALUES (?,?,?,?,?)",
            (condition.strip(), interpretation.strip(), topic.strip(), source.strip(), _now()))
        self.db.commit()
        return cur.lastrowid

    def update_rule(self, rule_id: int, **fields) -> None:
        allowed = {k: v for k, v in fields.items() if k in {"condition", "interpretation", "topic", "source"}}
        if allowed:
            sets = ", ".join(f"{k}=?" for k in allowed)
            self.db.execute(f"UPDATE rules SET {sets} WHERE id=?", (*allowed.values(), rule_id))
            self.db.commit()

    def delete_rule(self, rule_id: int) -> None:
        self.db.execute("DELETE FROM rules WHERE id=?", (rule_id,))
        self.db.commit()

    def rules(self) -> list[dict]:
        return [dict(r) for r in self.db.execute("SELECT * FROM rules ORDER BY id DESC")]

    def relevant_rules(self, factors: list[str], question: str = "", limit: int = 40) -> list[dict]:
        """Score each rule by how well its condition matches the chart's factors.

        A whole factor phrase found in the condition ("saturn in house 7") scores high;
        shared words score a little, so loosely worded rules still surface."""
        factor_text = [f.lower() for f in factors]
        factor_words = set().union(*(_words(f) for f in factors)) if factors else set()
        q_words = _words(question)
        scored = []
        for r in self.rules():
            cond = " " + re.sub(r"\s+", " ", r["condition"].lower()) + " "
            cond = re.sub(r"\b(the|a)\s+", "", cond)
            cond = re.sub(r"(\d+)(st|nd|rd|th)\s+house", r"house \1", cond)
            cond = re.sub(r"house\s+(\d+)\s*(st|nd|rd|th)\b", r"house \1", cond)
            score = sum(10 for f in factor_text if f" {f} " in cond or f" {f}," in cond)
            cw = _words(r["condition"])
            score += len(cw & factor_words) * 0.5
            score += len((_words(r["interpretation"]) | _words(r["topic"])) & q_words) * 1.0
            if score >= 10 or (q_words and score >= 2):
                scored.append((score, r))
        scored.sort(key=lambda x: -x[0])
        return [dict(r, score=s) for s, r in scored[:limit]]

    # --- charts, analyses, corrections ---------------------------------------
    def save_chart(self, name: str, inp: dict) -> int:
        cur = self.db.execute("INSERT INTO charts (name, input, created) VALUES (?,?,?)",
                              (name, json.dumps(inp), _now()))
        self.db.commit()
        return cur.lastrowid

    def charts(self) -> list[dict]:
        return [dict(r, input=json.loads(r["input"]))
                for r in self.db.execute("SELECT * FROM charts ORDER BY id DESC")]

    def chart(self, chart_id: int) -> dict | None:
        r = self.db.execute("SELECT * FROM charts WHERE id=?", (chart_id,)).fetchone()
        return dict(r, input=json.loads(r["input"])) if r else None

    def save_analysis(self, chart_id, question, answer, rule_ids) -> int:
        cur = self.db.execute(
            "INSERT INTO analyses (chart_id, question, answer, rule_ids, created) VALUES (?,?,?,?,?)",
            (chart_id, question, answer, json.dumps(rule_ids), _now()))
        self.db.commit()
        return cur.lastrowid

    def analysis(self, analysis_id: int) -> dict | None:
        r = self.db.execute("SELECT * FROM analyses WHERE id=?", (analysis_id,)).fetchone()
        return dict(r) if r else None

    def add_correction(self, analysis_id: int, correction: str) -> int:
        a = self.analysis(analysis_id)
        cur = self.db.execute(
            "INSERT INTO corrections (analysis_id, chart_id, correction, created) VALUES (?,?,?,?)",
            (analysis_id, a["chart_id"] if a else None, correction.strip(), _now()))
        self.db.commit()
        return cur.lastrowid

    def corrections(self, limit: int = 30) -> list[dict]:
        return [dict(r) for r in self.db.execute(
            "SELECT c.*, a.question, a.answer FROM corrections c LEFT JOIN analyses a "
            "ON a.id = c.analysis_id ORDER BY c.id DESC LIMIT ?", (limit,))]

    def export(self) -> dict:
        """Everything you've taught, as JSON. Later this becomes fine-tuning data."""
        return {"rules": self.rules(), "corrections": self.corrections(10_000)}
