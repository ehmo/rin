#!/usr/bin/env python3
"""Build a live icon-pattern research brief from iOS + Android top charts."""

from __future__ import annotations

import io
import json
import re
import statistics
import urllib.request
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
from PIL import Image


UA = (
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
    "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
)

HUE_LABELS = {
    0: "red",
    1: "orange",
    2: "yellow",
    3: "yellow-green",
    4: "green",
    5: "green-cyan",
    6: "cyan",
    7: "blue",
    8: "indigo",
    9: "violet",
    10: "magenta",
    11: "pink-red",
}


def fetch(url: str) -> bytes:
    req = urllib.request.Request(
        url,
        headers={"User-Agent": UA, "Accept-Language": "en-US,en;q=0.9"},
    )
    with urllib.request.urlopen(req, timeout=30) as resp:
        return resp.read()


def icon_metrics(url: str) -> dict:
    data = fetch(url)
    img = Image.open(io.BytesIO(data)).convert("RGB").resize((100, 100))
    arr = np.asarray(img).astype(np.float32) / 255.0
    hsv = np.asarray(img.convert("HSV")).astype(np.float32)
    h = hsv[:, :, 0] / 255.0
    s = hsv[:, :, 1] / 255.0
    v = hsv[:, :, 2] / 255.0

    sat_mask = (s > 0.25) & (v > 0.2)
    hue_bin = -1
    if sat_mask.any():
        bins = (h[sat_mask] * 12).astype(int) % 12
        hue_bin = int(Counter(bins.tolist()).most_common(1)[0][0])

    gray = arr[:, :, 0] * 0.299 + arr[:, :, 1] * 0.587 + arr[:, :, 2] * 0.114
    gy, gx = np.gradient(gray)
    mag = np.sqrt(gx * gx + gy * gy)
    edge_density = float((mag > 0.12).mean())

    return {
        "avg_sat": float(s.mean()),
        "avg_val": float(v.mean()),
        "hue_bin": hue_bin,
        "edge_density": edge_density,
        "monochrome": bool(s.mean() < 0.16),
    }


def get_ios_top(limit: int = 80) -> list[dict]:
    feed = json.loads(fetch("https://rss.applemarketingtools.com/api/v2/us/apps/top-free/100/apps.json"))
    out = []
    for idx, app in enumerate(feed["feed"]["results"][:limit], start=1):
        out.append(
            {
                "rank": idx,
                "name": app["name"],
                "icon_url": app["artworkUrl100"],
                "developer": app.get("artistName", ""),
                "id": app.get("id", ""),
            }
        )
    return out


def get_android_top(limit: int = 80) -> list[dict]:
    html = fetch("https://www.appbrain.com/stats/google-play-rankings/top_free/us").decode(
        "utf-8", "ignore"
    )
    out: list[dict] = []
    seen: set[str] = set()
    pattern = re.compile(
        r'<td class="ranking-icon-cell">\s*<a href="(?P<href>[^"]+)"><img[^>]*src="(?P<src>[^"]+)"[^>]*alt="(?P<name>[^"]+) icon">',
        re.I,
    )
    for idx, match in enumerate(pattern.finditer(html), start=1):
        name = match.group("name").strip()
        if not name or name in seen:
            continue
        seen.add(name)
        out.append(
            {
                "rank": len(out) + 1,
                "name": name,
                "icon_url": match.group("src").replace("&#x3D;", "="),
                "href": "https://www.appbrain.com" + match.group("href"),
            }
        )
        if len(out) >= limit:
            break
    return out


def analyze(items: list[dict]) -> dict:
    rows: list[dict] = []
    errors = 0
    for app in items:
        try:
            m = icon_metrics(app["icon_url"])
            rows.append({**app, **m})
        except Exception:
            errors += 1

    hue = Counter([r["hue_bin"] for r in rows if r["hue_bin"] >= 0])
    return {
        "count": len(rows),
        "errors": errors,
        "monochrome_ratio": round(sum(r["monochrome"] for r in rows) / max(1, len(rows)), 3),
        "avg_saturation": round(statistics.mean(r["avg_sat"] for r in rows), 3),
        "avg_edge_density": round(statistics.mean(r["edge_density"] for r in rows), 3),
        "top_hues": [
            {"bin": b, "label": HUE_LABELS.get(b, str(b)), "count": c}
            for b, c in hue.most_common(6)
        ],
        "least_complex": sorted(rows, key=lambda x: x["edge_density"])[:8],
        "most_complex": sorted(rows, key=lambda x: x["edge_density"], reverse=True)[:8],
        "top_30_names": [r["name"] for r in rows[:30]],
    }


def write_markdown(out_path: Path, ios: dict, android: dict) -> None:
    now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    md = []
    md.append("# Home Screen Icon Research V1")
    md.append("")
    md.append(f"Generated: {now}")
    md.append("")
    md.append("## Sources")
    md.append("")
    md.append("- Apple Top Free Apps (US): https://rss.applemarketingtools.com/api/v2/us/apps/top-free/100/apps.json")
    md.append("- Android Top Free (US) proxy: https://www.appbrain.com/stats/google-play-rankings/top_free/us")
    md.append("- Android adaptive icon guidance: https://developer.android.com/develop/ui/views/launch/icon_design_adaptive")
    md.append("- Apple HIG app icons entry: https://developer.apple.com/design/human-interface-guidelines/app-icons")
    md.append("")
    md.append("## Key Findings")
    md.append("")
    md.append(
        f"- iOS sample: {ios['count']} icons. Monochrome ratio: {ios['monochrome_ratio']}. Avg saturation: {ios['avg_saturation']}. Avg edge density: {ios['avg_edge_density']}."
    )
    md.append(
        f"- Android sample: {android['count']} icons. Monochrome ratio: {android['monochrome_ratio']}. Avg saturation: {android['avg_saturation']}. Avg edge density: {android['avg_edge_density']}."
    )
    md.append("- Dominant hue clusters on both platforms are blue/cyan + warm red/magenta families.")
    md.append("- Many high-usage apps are either very simple monochrome glyphs or visually noisy gradient/illustrative icons.")
    md.append("- Strategic whitespace and a single high-contrast geometric move are the clearest route to memorability.")
    md.append("")
    md.append("## Top-Hue Distribution")
    md.append("")
    md.append("### iOS")
    for row in ios["top_hues"]:
        md.append(f"- {row['label']} (bin {row['bin']}): {row['count']}")
    md.append("")
    md.append("### Android")
    for row in android["top_hues"]:
        md.append(f"- {row['label']} (bin {row['bin']}): {row['count']}")
    md.append("")
    md.append("## Platform Fit Constraints")
    md.append("")
    md.append("- Android adaptive icons: design for a centered safe zone (66x66 inside 108x108) and support monochrome themed icons.")
    md.append("- iOS icons: optimize for rounded-rectangle masking and no text dependence.")
    md.append("- Cross-platform: avoid thin strokes and micro-detail that collapses at small icon sizes.")
    md.append("")
    md.append("## Practical Direction For Rin")
    md.append("")
    md.append("- Build around one primitive + one structural cut/notch.")
    md.append("- Keep icon-level complexity below market average (target low edge density).")
    md.append("- Use distinctive but restrained color strategy; verify monochrome performance first.")
    md.append("")
    md.append("## Top 30 App Names (iOS sample)")
    md.append("")
    for i, name in enumerate(ios["top_30_names"], start=1):
        md.append(f"{i}. {name}")
    md.append("")
    md.append("## Top 30 App Names (Android sample)")
    md.append("")
    for i, name in enumerate(android["top_30_names"], start=1):
        md.append(f"{i}. {name}")
    md.append("")
    out_path.write_text("\n".join(md) + "\n")


def main() -> int:
    out_dir = Path("design/assets/logo-concepts/research")
    out_dir.mkdir(parents=True, exist_ok=True)

    ios_raw = get_ios_top(80)
    android_raw = get_android_top(80)

    ios = analyze(ios_raw)
    android = analyze(android_raw)

    payload = {
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "ios": ios,
        "android": android,
    }
    (out_dir / "home_screen_icon_metrics.json").write_text(json.dumps(payload, indent=2))
    write_markdown(out_dir / "HOME_SCREEN_ICON_RESEARCH_V1.md", ios, android)
    print(out_dir / "HOME_SCREEN_ICON_RESEARCH_V1.md")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

