#!/usr/bin/env python3
"""Generate Rin logo concepts via Gemini image models.

Usage:
  GEMINI_API_KEY=... python3 scripts/generate_logos_gemini.py
"""

from __future__ import annotations

import argparse
import base64
import json
import os
import pathlib
import time
import urllib.error
import urllib.request


CONCEPTS = [
    (
        "01_signal_lens_r",
        "Design a minimalist R monogram logo where the bowl of the R contains a precise circular lens/iris shape. "
        "The lens is integrated, not pasted. Use balanced stroke weight, calm geometry, and one intelligent cut that "
        "suggests focus and analysis. Optional accent color: #1A73E8 on white.",
    ),
    (
        "02_bridge_node_r",
        "Create a geometric R logo mark built from two solid forms connected by one clean bridge element at the midsection, "
        "symbolizing trusted connection across people. Keep silhouette bold and memorable. Monochrome first.",
    ),
    (
        "03_orbit_core",
        "Create an abstract logo mark with one central node and one near-complete orbital ring that opens into a subtle directional break. "
        "The form should feel intelligent, calm, and ownable, with minimal components and strong negative space.",
    ),
    (
        "04_notched_circle_r",
        "Design a minimal circular logo where a single diagonal notch transforms an almost-complete ring into an implied R structure. "
        "The notch must feel intentional and iconic, not decorative.",
    ),
    (
        "05_pathline_r",
        "Generate a monoline R symbol formed by one continuous path with one decisive directional turn. "
        "Keep stroke endings purposeful and compact. The logo should remain legible at app icon size.",
    ),
    (
        "06_twin_arc_trustmark",
        "Create an abstract trustmark using two interlocking arcs that produce a stable central void and subtle R-read if viewed closely. "
        "Emphasize harmony, balance, and premium restraint.",
    ),
    (
        "07_constellation_cut",
        "Design a compact R silhouette containing a very sparse constellation of 3-4 nodes connected by short geometric links, "
        "using negative space to keep it clean. Avoid generic social-network icon style.",
    ),
    (
        "08_compass_notch",
        "Design a minimalist circular logo with a subtle north-east notch/indicator integrated into the form, "
        "suggesting directional intelligence and guidance. Keep it non-literal, no arrows pasted on top.",
    ),
    (
        "09_prism_r",
        "Create a Bauhaus-inspired R mark reduced to three essential geometric facets with perfect spacing and structural clarity. "
        "No ornament. Timeless, rational, and highly legible.",
    ),
    (
        "10_keyhole_node",
        "Generate a bold abstract R block mark with a rounded keyhole-like interior void that implies selective access and trust. "
        "Keep the shape friendly, not security-cliche. Strong silhouette required.",
    ),
    (
        "11_echo_loop",
        "Create a minimal dual-loop symbol where concentric echoes are interrupted by one asymmetric break that forms a distinct brand signature. "
        "Keep spacing optically perfect and scalable.",
    ),
    (
        "12_carved_r_monolith",
        "Design an app-icon-first logo: a solid rounded-square field with an R carved from negative space. "
        "The carving should be thick, clean, and recognizable at tiny sizes. Monochrome-first, then blue variant.",
    ),
]


SHARED_SUFFIX = (
    "single logo mark, flat vector, geometric precision, centered composition, white background, no text, no wordmark, "
    "no mockup, no shadows, no gradients unless specified, no photorealism, high contrast, export-ready brand symbol. "
    "avoid: 3D, bevel, shadow, mockup, gradient overload, tiny details, photorealism, watermark, extra symbols, letters beyond intended mark."
)


def load_concepts(concept_file: str | None) -> list[tuple[str, str]]:
    if not concept_file:
        return CONCEPTS

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
        raise ValueError("No concepts loaded from concept file")
    return out


def call_model(api_key: str, model: str, prompt: str) -> tuple[bytes | None, str]:
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={api_key}"
    payload = {
        "contents": [{"parts": [{"text": prompt}]}],
        "generationConfig": {"responseModalities": ["IMAGE", "TEXT"]},
    }
    req = urllib.request.Request(
        url,
        data=json.dumps(payload).encode(),
        headers={"Content-Type": "application/json"},
    )
    with urllib.request.urlopen(req, timeout=180) as resp:
        body = json.loads(resp.read())

    parts = body.get("candidates", [{}])[0].get("content", {}).get("parts", [])
    image_bytes = None
    text_chunks: list[str] = []
    for part in parts:
        inline = part.get("inlineData") or part.get("inline_data")
        if inline and inline.get("data") and image_bytes is None:
            image_bytes = base64.b64decode(inline["data"])
        if part.get("text"):
            text_chunks.append(part["text"])
    return image_bytes, "\n".join(text_chunks)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--output-dir",
        default="design/assets/logo-concepts/generated/2026-02-16",
        help="Output directory",
    )
    parser.add_argument("--model", default="gemini-3-pro-image-preview")
    parser.add_argument("--overwrite", action="store_true")
    parser.add_argument("--concept-file", help="Path to JSON file with concept prompts")
    parser.add_argument("--shared-suffix", default=SHARED_SUFFIX, help="Shared style suffix")
    args = parser.parse_args()

    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        raise SystemExit("GEMINI_API_KEY is required")

    concepts = load_concepts(args.concept_file)
    out_dir = pathlib.Path(args.output_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    manifest_path = out_dir / "manifest.json"
    manifest: list[dict] = []

    total = len(concepts)
    for idx, (slug, core_prompt) in enumerate(concepts, start=1):
        out_file = out_dir / f"{slug}.png"
        full_prompt = f"{core_prompt}\n\n{args.shared_suffix}"

        if out_file.exists() and not args.overwrite:
            print(f"[{idx:02d}/{total:02d}] skip {slug} (exists)")
            manifest.append(
                {
                    "slug": slug,
                    "file": str(out_file),
                    "core_prompt": core_prompt,
                    "full_prompt": full_prompt,
                    "model": args.model,
                    "attempts": 0,
                    "status": "skipped_existing",
                }
            )
            continue

        image = None
        response_text = ""
        error = None
        attempts = 0
        for attempts in range(1, 4):
            try:
                image, response_text = call_model(api_key, args.model, full_prompt)
                if image:
                    break
                error = "no image in response"
            except urllib.error.HTTPError as exc:
                try:
                    body = exc.read().decode("utf-8", "ignore")
                except Exception:
                    body = ""
                error = f"HTTP {exc.code}: {body[:200]}"
            except Exception as exc:  # pragma: no cover - runtime/network dependent
                error = str(exc)
            time.sleep(2 * attempts)

        if image:
            out_file.write_bytes(image)
            print(f"[{idx:02d}/{total:02d}] ok   {slug}")
            manifest.append(
                {
                    "slug": slug,
                    "file": str(out_file),
                    "core_prompt": core_prompt,
                    "full_prompt": full_prompt,
                    "model": args.model,
                    "attempts": attempts,
                    "status": "ok",
                    "response_text": response_text[:2000],
                }
            )
        else:
            print(f"[{idx:02d}/{total:02d}] fail {slug} ({error})")
            manifest.append(
                {
                    "slug": slug,
                    "file": None,
                    "core_prompt": core_prompt,
                    "full_prompt": full_prompt,
                    "model": args.model,
                    "attempts": attempts,
                    "status": "failed",
                    "error": error,
                }
            )

    manifest_path.write_text(json.dumps(manifest, indent=2))
    ok_count = sum(1 for item in manifest if item.get("status") in {"ok", "skipped_existing"})
    print(f"done: {ok_count}/{total} available")
    print(f"manifest: {manifest_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
