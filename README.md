# Jyotish Learning Assistant

A small platform that learns Vedic astrology with you and learns to give chart analysis.

1. **Chart engine**: sidereal zodiac, Lahiri ayanamsa (Swiss Ephemeris), whole-sign houses,
   nakshatra and pada, D9 Navamsa, dignity, house lordship, Vimshottari mahadasha/antardasha.
2. **Knowledge base you teach**: IF/THEN rules with topic and source (SQLite, `data/jyotish.db`).
3. **Analysis**: Claude reads the chart, the rules that match it, and your past corrections.
   It cites rules as `[R12]`, marks anything not taught as *(general knowledge)*, and ends
   with questions for you, so each session gives you something new to teach.
4. **Corrections**: every correction is saved and fed into future analyses; you can also turn
   it straight into a rule. `/api/export` gives all taught material as JSON, which becomes the
   dataset for fine-tuning a custom model later.

## Run

```bash
python3 -m venv .venv && . .venv/bin/activate
pip install -r requirements.txt
export ANTHROPIC_API_KEY=sk-ant-...      # without it, Analyze shows the prompt instead
python seed_rules.py                     # optional starter rules
uvicorn app:app --reload                 # open http://localhost:8000
```

`JYOTISH_MODEL` picks the Claude model (default `claude-opus-5-5`).

## Birth place

Type a city and pick it from the list: latitude, longitude and timezone fill in, and the UTC offset
is worked out for the birth date itself (including historical changes such as India's +6:30 war
time in 1942-45). Lookup is offline (GeoNames, towns of 5,000+ people). For a smaller village,
type the coordinates and UTC offset by hand.

## Writing rules that match well

Conditions are matched against the chart's factor phrases (shown on the Chart tab), e.g.
`Saturn in house 7`, `Venus in Pisces`, `Moon in Rohini`, `Jupiter exalted`,
`Mars retrograde`, `lord of house 10 in house 9`, `Rahu mahadasha`, `libra lagna`.
"7th house" is understood as "house 7".

## Not yet included

Aspects (drishti) as matchable factors, yoga detection, other divisional charts, transits, multi-user accounts, hosting.
