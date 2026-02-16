#!/usr/bin/env python3
"""Evaluate generated logos against the Rin rubric via Gemini vision."""

from __future__ import annotations

import argparse
import base64
import json
import os
import pathlib
import time
import re
import urllib.error
import urllib.request


RUBRIC_PROMPT = """You are evaluating a single logo image for the Rin app.

Score each dimension from 0 to 10 (integer only):
- distinctive_silhouette
- first_glance_clarity
- hidden_meaning_relevance
- memorability
- small_size_legibility
- category_differentiation
- monochrome_robustness
- brand_fit_trust_intelligence_clarity

Then compute weighted_total_100 using:
- distinctive_silhouette * 2.0
- first_glance_clarity * 1.5
- hidden_meaning_relevance * 1.0
- memorability * 1.5
- small_size_legibility * 1.5
- category_differentiation * 1.0
- monochrome_robustness * 1.0
- brand_fit_trust_intelligence_clarity * 0.5

Return JSON only with this schema:
{
  "scores": {
    "distinctive_silhouette": 0,
    "first_glance_clarity": 0,
    "hidden_meaning_relevance": 0,
    "memorability": 0,
    "small_size_legibility": 0,
    "category_differentiation": 0,
    "monochrome_robustness": 0,
    "brand_fit_trust_intelligence_clarity": 0
  },
  "weighted_total_100": 0,
  "strengths": ["...","..."],
  "weaknesses": ["...","..."],
  "recommendation": "keep|refine|drop"
}
"""


def _parse_json_text(text: str) -> dict:
    text = text.strip()
    if text.startswith("```"):
        text = re.sub(r"^```(?:json)?\s*", "", text)
        text = re.sub(r"\s*```$", "", text)
    return json.loads(text)


def eval_one(api_key: str, model: str, image_path: pathlib.Path) -> dict:
    data_b64 = base64.b64encode(image_path.read_bytes()).decode()
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={api_key}"
    payload = {
        "contents": [
            {
                "parts": [
                    {"inline_data": {"mime_type": "image/png", "data": data_b64}},
                    {"text": RUBRIC_PROMPT},
                ]
            }
        ],
        "generationConfig": {"responseMimeType": "application/json"},
    }
    req = urllib.request.Request(
        url,
        data=json.dumps(payload).encode(),
        headers={"Content-Type": "application/json"},
    )
    with urllib.request.urlopen(req, timeout=60) as resp:
        body = json.loads(resp.read())
    text = body["candidates"][0]["content"]["parts"][0]["text"]
    return _parse_json_text(text)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--input-dir",
        default="design/assets/logo-concepts/generated/2026-02-16",
        help="Directory containing generated logo PNG files",
    )
    parser.add_argument("--model", default="gemini-2.0-flash")
    args = parser.parse_args()

    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        raise SystemExit("GEMINI_API_KEY is required")

    in_dir = pathlib.Path(args.input_dir)
    files = sorted([p for p in in_dir.glob("*.png") if p.name[:2].isdigit()])
    if not files:
        raise SystemExit(f"No concept png files found in {in_dir}")

    results: dict[str, dict] = {}
    for idx, path in enumerate(files, start=1):
        attempt_err = None
        for attempt in range(1, 4):
            try:
                res = eval_one(api_key, args.model, path)
                results[path.name] = res
                print(
                    f"[{idx:02d}/{len(files):02d}] ok   {path.name} score={res.get('weighted_total_100')}",
                    flush=True,
                )
                break
            except urllib.error.HTTPError as exc:
                try:
                    body = exc.read().decode("utf-8", "ignore")
                except Exception:
                    body = ""
                attempt_err = f"HTTP {exc.code}: {body[:180]}"
            except Exception as exc:  # pragma: no cover - runtime/network dependent
                attempt_err = str(exc)
            time.sleep(2 * attempt)
        else:
            print(f"[{idx:02d}/{len(files):02d}] fail {path.name} ({attempt_err})", flush=True)
            results[path.name] = {"error": attempt_err}

    out_json = in_dir / "eval.json"
    out_json.write_text(json.dumps(results, indent=2))

    ranked = [
        (name, payload.get("weighted_total_100", -1))
        for name, payload in results.items()
        if isinstance(payload, dict) and "weighted_total_100" in payload
    ]
    ranked.sort(key=lambda x: x[1], reverse=True)

    out_md = in_dir / "EVAL_SUMMARY.md"
    lines = [
        "# Rin Logo Eval Summary",
        "",
        f"Model: `{args.model}`",
        "",
        "## Ranking",
        "",
    ]
    for rank, (name, score) in enumerate(ranked, start=1):
        lines.append(f"{rank}. `{name}` - {score}")
    lines.extend(["", "## Files", "", f"- Raw eval JSON: `{out_json}`"])
    out_md.write_text("\n".join(lines) + "\n")

    print(f"wrote: {out_json}")
    print(f"wrote: {out_md}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
