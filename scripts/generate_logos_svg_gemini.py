#!/usr/bin/env python3
"""Generate Rin logo concepts as SVG via Gemini text models.

Usage:
  GEMINI_API_KEY=... python3 scripts/generate_logos_svg_gemini.py --concept-file <path>
"""

from __future__ import annotations

import argparse
import json
import os
import pathlib
import re
import time
import urllib.error
import urllib.request


SHARED_SUFFIX = (
    "Output ONLY valid SVG code — no markdown fences, no explanation, no commentary. "
    "Use viewBox=\"0 0 512 512\". White background rectangle. Black foreground marks. "
    "Flat vector, geometric precision, centered composition. No text, no wordmark. "
    "No gradients, no shadows, no 3D effects. Thick bold strokes (stroke-width >= 30). "
    "The symbol must be clearly visible and centered within the canvas. "
    "Keep the SVG simple: minimal path commands, clean geometry."
)


def load_concepts(concept_file: str) -> list[tuple[str, str]]:
    path = pathlib.Path(concept_file)
    payload = json.loads(path.read_text())
    items = payload.get("concepts", payload)
    out: list[tuple[str, str]] = []
    for item in items:
        slug = item["slug"]
        prompt = item.get("prompt") or item.get("core_prompt")
        if not prompt:
            raise ValueError(f"Concept {slug} missing prompt/core_prompt")
        out.append((slug, prompt))
    if not out:
        raise ValueError("No concepts loaded")
    return out


def extract_svg(text: str) -> str | None:
    """Extract SVG from response, stripping markdown fences if present."""
    # Try to find SVG within markdown code fences
    fence_match = re.search(r"```(?:svg|xml)?\s*\n?(.*?)```", text, re.DOTALL)
    if fence_match:
        text = fence_match.group(1).strip()

    # Find the SVG element
    svg_match = re.search(r"(<svg[\s\S]*?</svg>)", text)
    if svg_match:
        return svg_match.group(1)
    return None


def call_model(api_key: str, model: str, prompt: str) -> str | None:
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={api_key}"
    payload = {
        "contents": [{"parts": [{"text": prompt}]}],
        "generationConfig": {"temperature": 0.8, "maxOutputTokens": 4096},
    }
    req = urllib.request.Request(
        url,
        data=json.dumps(payload).encode(),
        headers={"Content-Type": "application/json"},
    )
    with urllib.request.urlopen(req, timeout=120) as resp:
        body = json.loads(resp.read())

    text = (
        body.get("candidates", [{}])[0]
        .get("content", {})
        .get("parts", [{}])[0]
        .get("text", "")
    )
    return extract_svg(text)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--concept-file", required=True)
    parser.add_argument(
        "--output-dir",
        default="design/assets/logo-concepts/generated/svg-latest",
    )
    parser.add_argument("--model", default="gemini-2.5-flash")
    parser.add_argument("--overwrite", action="store_true")
    args = parser.parse_args()

    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        raise SystemExit("GEMINI_API_KEY is required")

    concepts = load_concepts(args.concept_file)
    out_dir = pathlib.Path(args.output_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    manifest: list[dict] = []

    total = len(concepts)
    for idx, (slug, core_prompt) in enumerate(concepts, start=1):
        out_file = out_dir / f"{slug}.svg"
        full_prompt = f"{core_prompt}\n\n{SHARED_SUFFIX}"

        if out_file.exists() and not args.overwrite:
            print(f"[{idx:02d}/{total:02d}] skip {slug} (exists)")
            manifest.append({"slug": slug, "file": str(out_file), "status": "skipped"})
            continue

        svg = None
        error = None
        attempts = 0
        for attempts in range(1, 4):
            try:
                svg = call_model(api_key, args.model, full_prompt)
                if svg:
                    break
                error = "no SVG in response"
            except urllib.error.HTTPError as exc:
                try:
                    body = exc.read().decode("utf-8", "ignore")
                except Exception:
                    body = ""
                error = f"HTTP {exc.code}: {body[:200]}"
                if exc.code == 429:
                    time.sleep(5 * attempts)
                    continue
            except Exception as exc:
                error = str(exc)
            time.sleep(2 * attempts)

        if svg:
            out_file.write_text(svg)
            print(f"[{idx:02d}/{total:02d}] ok   {slug}")
            manifest.append({
                "slug": slug,
                "file": str(out_file),
                "core_prompt": core_prompt,
                "status": "ok",
                "attempts": attempts,
            })
        else:
            print(f"[{idx:02d}/{total:02d}] fail {slug} ({error})")
            manifest.append({
                "slug": slug,
                "file": None,
                "core_prompt": core_prompt,
                "status": "failed",
                "error": error,
                "attempts": attempts,
            })

        # Rate limit courtesy
        if idx < total:
            time.sleep(2)

    manifest_path = out_dir / "manifest.json"
    manifest_path.write_text(json.dumps(manifest, indent=2))

    # Generate index.html for viewing
    ok_items = [m for m in manifest if m["status"] in {"ok", "skipped"}]
    html_parts = [
        "<!DOCTYPE html><html><head><title>Rin Logo V5 — SVG Concepts</title>",
        "<style>",
        "body{font-family:SF Pro,system-ui,sans-serif;background:#f5f5f5;padding:40px;max-width:1400px;margin:0 auto}",
        "h1{font-size:24px;font-weight:600;margin-bottom:32px}",
        ".grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(280px,1fr));gap:24px}",
        ".card{background:#fff;border-radius:16px;padding:24px;box-shadow:0 1px 3px rgba(0,0,0,.08)}",
        ".card img,.card object{width:100%;aspect-ratio:1;object-fit:contain;border-radius:8px;background:#fff;border:1px solid #eee}",
        ".card h3{font-size:14px;font-weight:500;margin:12px 0 4px;color:#333}",
        ".card p{font-size:11px;color:#888;margin:0;line-height:1.4}",
        "</style></head><body>",
        "<h1>Rin Logo V5 — 12 SVG Concepts</h1>",
        '<div class="grid">',
    ]
    for item in ok_items:
        slug = item["slug"]
        fname = f"{slug}.svg"
        prompt = item.get("core_prompt", "")[:120]
        html_parts.append(
            f'<div class="card">'
            f'<object data="{fname}" type="image/svg+xml"></object>'
            f"<h3>{slug.replace('_', ' ').title()}</h3>"
            f"<p>{prompt}...</p></div>"
        )
    html_parts.append("</div></body></html>")
    (out_dir / "index.html").write_text("\n".join(html_parts))

    ok_count = len(ok_items)
    print(f"\ndone: {ok_count}/{total} available")
    print(f"manifest: {manifest_path}")
    print(f"viewer:   {out_dir / 'index.html'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
