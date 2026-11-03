"""Chart analysis with Claude, grounded in the rules you taught and your past corrections."""
from __future__ import annotations

import os

from .chart import Chart, chart_factors, chart_summary
from .knowledge import KnowledgeBase

MODEL = os.environ.get("JYOTISH_MODEL", "claude-opus-5-5")

SYSTEM = """You are a student of Parashari Jyotish (the system of Brihat Parashara Hora Shastra),
learning from your teacher. Use the sidereal (Lahiri) chart data given; never recompute positions.
Reason the Parashari way: lagna and lagna lord first, then house lords and their placements,
graha drishti, functional benefics/malefics for this lagna, yogas, dignity, then the
Vimshottari dasha for timing. Use the Moon chart and D9 to confirm. The yogas listed are
detected mechanically: confirm their strength before relying on them.

How to reason:
1. The teacher's rules are your primary source. When a rule's condition is met by the chart,
   apply it and cite it as [R<id>]. Check that the condition is truly met before citing.
2. The teacher's past corrections override anything else. Follow them.
3. You may add general classical knowledge (Parashari principles) where no taught rule
   covers a point, but mark each such statement as (general knowledge) so the teacher can
   confirm or correct it.
4. Weigh conflicting indications, mention dignity, house lordship, aspects and the current
   dasha, and say how confident you are.
5. End with "Questions for my teacher": 1-3 things you were unsure about, so the teacher
   can teach you a new rule.
Be concrete and kind. Do not make fatalistic or medical/legal predictions."""


def build_prompt(chart: Chart, kb: KnowledgeBase, question: str) -> tuple[str, list[dict]]:
    rules = kb.relevant_rules(chart_factors(chart), question)
    corrections = kb.corrections(20)
    parts = ["## Chart\n" + chart_summary(chart)]
    if rules:
        parts.append("## Teacher's rules that may apply\n" + "\n".join(
            f"[R{r['id']}] IF {r['condition']} THEN {r['interpretation']}"
            + (f" (source: {r['source']})" if r["source"] else "") for r in rules))
    else:
        parts.append("## Teacher's rules that may apply\n(none taught yet for these placements)")
    if corrections:
        parts.append("## Teacher's past corrections (follow these)\n" + "\n".join(
            f"- On \"{(c['question'] or 'general analysis')[:80]}\": {c['correction']}"
            for c in corrections))
    parts.append("## Question\n" + (question or "Give an overall analysis of this chart."))
    return "\n\n".join(parts), rules


def analyze(chart: Chart, kb: KnowledgeBase, question: str = "") -> tuple[str, list[dict]]:
    prompt, rules = build_prompt(chart, kb, question)
    if not os.environ.get("ANTHROPIC_API_KEY"):
        return ("(No ANTHROPIC_API_KEY set, so here is the prompt that would be sent.)\n\n"
                + prompt), rules
    import anthropic
    client = anthropic.Anthropic()
    msg = client.messages.create(model=MODEL, max_tokens=4000, system=SYSTEM,
                                 messages=[{"role": "user", "content": prompt}])
    text = "".join(b.text for b in msg.content if b.type == "text")
    return text, rules
