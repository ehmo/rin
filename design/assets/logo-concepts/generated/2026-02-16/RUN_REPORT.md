# Logo Generation Run Report

Date: 2026-02-16

## What Was Run
- In-repo generator script: `scripts/generate_logos_gemini.py`
- Model used: `gemini-3-pro-image-preview`
- Output directory: `design/assets/logo-concepts/generated/2026-02-16`
- Concepts generated: 12/12

## Generated Files
- `01_signal_lens_r.png`
- `02_bridge_node_r.png`
- `03_orbit_core.png`
- `04_notched_circle_r.png`
- `05_pathline_r.png`
- `06_twin_arc_trustmark.png`
- `07_constellation_cut.png`
- `08_compass_notch.png`
- `09_prism_r.png`
- `10_keyhole_node.png`
- `11_echo_loop.png`
- `12_carved_r_monolith.png`

## Eval Attempt
- In-repo evaluator script: `scripts/eval_logos_gemini.py`
- Eval model: `gemini-2.0-flash`
- Result: all eval calls failed with `HTTP 429` (quota exceeded) on current API key.
- Raw eval output retained in `eval.json`.

## Immediate Fallback Ranking
Until quota is available for automated vision scoring, use the concept-predicted shortlist from
`design/assets/logo-concepts/RIN_LOGO_12_CONCEPTS_NANO_BANANA_V1.md`:
1. `12_carved_r_monolith.png`
2. `01_signal_lens_r.png`
3. `02_bridge_node_r.png`
4. `04_notched_circle_r.png`

## Re-run Commands
```bash
export GEMINI_API_KEY='<your-key>'
python3 scripts/generate_logos_gemini.py --overwrite
python3 -u scripts/eval_logos_gemini.py
```
