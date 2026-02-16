# Rin Logo Concepts (12) + Nano Banana Prompts

Date: 2026-02-16

Guide used:
- `design/assets/logo-concepts/LOGO_RESEARCH_SYNTHESIS_V2.md`

Nano Banana library seeds used:
- `app-web-design.json` "Minimalist Word-as-Object Logo Design"
- `app-web-design.json` "Bauhaus Functional Identity Brand Logo Generation"
- `app-web-design.json` minimalist geometric/vector templates

All prompts below are custom remixes for Rin (AI-generated), designed for Nano Banana.

## Shared Prompt Footer
Append to each prompt:
- "single logo mark, flat vector, geometric precision, centered composition, white background, no text, no wordmark, no mockup, no shadows, no gradients unless specified, no photorealism, high contrast, export-ready brand symbol"

## 12 Concepts

### 1) Signal Lens R
Idea: An R monogram with an iris/lens counter.
Hidden meaning: "See your network clearly."
Prompt:
```text
Design a minimalist R monogram logo where the bowl of the R contains a precise circular lens/iris shape. The lens is integrated, not pasted. Use balanced stroke weight, calm geometry, and one intelligent cut that suggests focus and analysis. Optional accent color: #1A73E8 on white.
```
Predicted score: 88

### 2) Bridge Node R
Idea: R with a bridge-like cross connection between two masses.
Hidden meaning: Relationship bridging.
Prompt:
```text
Create a geometric R logo mark built from two solid forms connected by one clean bridge element at the midsection, symbolizing trusted connection across people. Keep silhouette bold and memorable. Monochrome first.
```
Predicted score: 86

### 3) Orbit Core
Idea: Near-complete ring orbiting a stable center node.
Hidden meaning: Network structure around a trusted core.
Prompt:
```text
Create an abstract logo mark with one central node and one near-complete orbital ring that opens into a subtle directional break. The form should feel intelligent, calm, and ownable, with minimal components and strong negative space.
```
Predicted score: 82

### 4) Notched Circle R
Idea: A circle interrupted by one diagonal notch that resolves to R identity.
Hidden meaning: Signal extraction from noise.
Prompt:
```text
Design a minimal circular logo where a single diagonal notch transforms an almost-complete ring into an implied R structure. The notch must feel intentional and iconic, not decorative.
```
Predicted score: 85

### 5) Pathline R
Idea: Continuous single-stroke R with one directional inflection.
Hidden meaning: Relationship path and progression.
Prompt:
```text
Generate a monoline R symbol formed by one continuous path with one decisive directional turn. Keep stroke endings purposeful and compact. The logo should remain legible at app icon size.
```
Predicted score: 79

### 6) Twin Arc Trustmark
Idea: Two interlocking arcs creating a stable interior void.
Hidden meaning: Mutual trust and reciprocity.
Prompt:
```text
Create an abstract trustmark using two interlocking arcs that produce a stable central void and subtle R-read if viewed closely. Emphasize harmony, balance, and premium restraint.
```
Predicted score: 81

### 7) Constellation Cut
Idea: Minimal star/node constellation constrained inside an R silhouette.
Hidden meaning: Network intelligence map.
Prompt:
```text
Design a compact R silhouette containing a very sparse constellation of 3-4 nodes connected by short geometric links, using negative space to keep it clean. Avoid generic social-network icon style.
```
Predicted score: 76

### 8) Compass Notch
Idea: Circular form with north-east directional cue.
Hidden meaning: Guidance to high-value relationships.
Prompt:
```text
Design a minimalist circular logo with a subtle north-east notch/indicator integrated into the form, suggesting directional intelligence and guidance. Keep it non-literal, no arrows pasted on top.
```
Predicted score: 78

### 9) Prism R
Idea: R reduced into three planar geometric facets.
Hidden meaning: Multiple perspectives unified into clarity.
Prompt:
```text
Create a Bauhaus-inspired R mark reduced to three essential geometric facets with perfect spacing and structural clarity. No ornament. Timeless, rational, and highly legible.
```
Predicted score: 84

### 10) Keyhole Node
Idea: Rounded keyhole-like interior inside an abstract R block.
Hidden meaning: Trusted access, permissioned visibility.
Prompt:
```text
Generate a bold abstract R block mark with a rounded keyhole-like interior void that implies selective access and trust. Keep the shape friendly, not security-cliche. Strong silhouette required.
```
Predicted score: 80

### 11) Echo Loop
Idea: Dual concentric echoes with one asymmetric break.
Hidden meaning: Relationship signals and ripple effects.
Prompt:
```text
Create a minimal dual-loop symbol where concentric echoes are interrupted by one asymmetric break that forms a distinct brand signature. Keep spacing optically perfect and scalable.
```
Predicted score: 77

### 12) Carved R Monolith
Idea: Solid rounded square with R carved as negative space.
Hidden meaning: Signal carved out of raw data.
Prompt:
```text
Design an app-icon-first logo: a solid rounded-square field with an R carved from negative space. The carving should be thick, clean, and recognizable at tiny sizes. Monochrome-first, then blue variant.
```
Predicted score: 90

## First-Round Shortlist
Top 4 by predicted score:
1. Carved R Monolith (90)
2. Signal Lens R (88)
3. Bridge Node R (86)
4. Notched Circle R (85)

## Eval Workflow For Generated Outputs
For each generated option:
1. Export monochrome SVG-like clean output.
2. Downscale to 1024, 180, 64, 32, 16 px and test recognizability.
3. Run rubric from `LOGO_RESEARCH_SYNTHESIS_V2.md`.
4. Keep only concepts scoring >= 85.
5. Produce 3 micro-variants for each finalist:
- stroke-weight variant
- corner-radius variant
- notch/gap size variant

## Practical Next Batch Prompt
Use this to run a high-quality first pass in Nano Banana:
```text
Generate 12 separate minimalist logo marks for a brand named Rin, each one based on a single idea of trust, clarity, and network intelligence. Style: premium geometric vector, app-icon ready, memorable silhouette, hidden meaning optional but relevant, no text, no wordmark, pure white background, monochrome black first. Avoid cliches: chat bubble, generic social nodes, shield-lock icon, address book, literal people icons. Include concepts: Signal Lens R, Bridge Node R, Orbit Core, Notched Circle R, Pathline R, Twin Arc Trustmark, Constellation Cut, Compass Notch, Prism R, Keyhole Node, Echo Loop, Carved R Monolith.
```

