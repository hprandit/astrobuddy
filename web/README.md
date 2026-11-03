# AstroBuddy hosted app

`index.html` is the hosted version published as a claude.ai Artifact. It runs entirely in the
browser: charts are computed with astronomy-engine plus a Lahiri ayanamsa fit (within about
11 arcseconds of Swiss Ephemeris on test charts), rules/charts/corrections live in the
artifact's database, and analysis is written by Claude through the artifact's `sample`
capability, so no API key or server is needed.

- `engine.js`: chart, Parashari layer and rule matching (same logic as the Python package).
  `index.html` contains an inlined copy.
- `places.json`: GeoNames cities (40k+ people worldwide, 15k+ in South Asia) with time zones.
