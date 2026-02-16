# iOS Score and Explanation Screen Spec V1

## 1) Purpose

Screen-level specification for the Score tab. Defines every screen for viewing, understanding, and exploring the Rin Score.

Companion docs:
- `docs/product/RIN_SCORE_V1.md` (score formula and components)
- `docs/operations/SCORE_RELEASE_CADENCE_V1.md` (computation cadence)
- `docs/architecture/IOS_NAVIGATION_STATE_V1.md` (navigation model)

---

## 2) Score Tab Screens

### SC1: Score Home

**Layout:**
- Large score display: number (0-100) centered, circular progress ring.
- Score quality label below number: "Strong" / "Good" / "Building" / "New".
- Last updated timestamp: "Updated today at 2:00 AM".
- Staleness indicator if >24h: "Estimated" badge.
- Score trend sparkline: last 30 days mini chart.
- Component breakdown section (4 bars):
  - Network Quality (40%) — horizontal bar with fill level.
  - Network Position (30%) — horizontal bar.
  - Stability (20%) — horizontal bar.
  - Trust (10%) — horizontal bar.
- Explainability card: one-sentence summary of score drivers.
- "Learn More" link → SC3 (How Scoring Works).

**Score quality labels:**

| Range | Label | Color |
|-------|-------|-------|
| 80-100 | Strong | Green |
| 60-79 | Good | Blue |
| 30-59 | Building | Yellow |
| 0-29 | New | Grey |

**States:**
- Score loaded (default).
- Score stale (>24h): "Estimated" badge, muted colors.
- Score unavailable (first day, no data): "Your score is being calculated" with explanation.
- Score changed since last view: delta indicator (+3 ▲ or -2 ▼).

**Transitions:**
- Tap any component bar → SC2 (Component Detail).
- Tap sparkline → SC4 (Score History).
- Tap "Learn More" → SC3 (How Scoring Works).

---

### SC2: Component Detail

**Layout:**
- Component name and weight (e.g., "Network Quality — 40% of your score").
- Large bar showing component value (0-100% fill).
- Signal breakdown list:
  - Each signal with name, current value, and impact indicator (↑ positive / ↓ negative / — neutral).
  - Example signals for Quality: "Reciprocal connections: 72%" ↑, "Verified contacts: 45%" ↑, "Circle organization bonus: +3%" ↑.
- Improvement suggestions section:
  - Actionable tips specific to this component.
  - Example: "Verify your email to boost Trust" or "Your network has grown steadily — Stability is strong."
- Back button → SC1.

**Component-specific signals:**

| Component | Signals shown |
|-----------|--------------|
| Quality | Reciprocity ratio, verified contact %, circle bonus |
| Position | Network reach, bridge connections, cluster diversity |
| Stability | Core tie persistence, churn rate, verification continuity |
| Trust | Abuse flag count, dispute history, account integrity |

**States:**
- Loaded with signals.
- Improvement suggestion highlighted if component is weakest.

---

### SC3: How Scoring Works

**Layout:**
- Educational screen (scrollable).
- Section: "What is Rin Score?" — brief explanation.
- Section: "How it's calculated" — component weights with visual bars.
- Section: "What helps your score" — bullet list of positive behaviors.
- Section: "What doesn't help" — bullet list of things that don't boost score (bulk adding, non-reciprocal contacts).
- Section: "How often it updates" — daily cadence explanation.
- Section: "Privacy" — what data is used, what isn't (no message content, no invasive tracking).
- Back button → SC1.

**Content examples:**

"What helps your score":
- Having contacts who also have you in their phone.
- Maintaining stable, long-term connections.
- Verifying your phone and email.
- Keeping your account in good standing.

"What doesn't help":
- Adding hundreds of contacts you don't know.
- Having contacts who don't have you back.
- Frequent changes to your contact list.

---

### SC4: Score History

**Layout:**
- Line chart showing score over time (last 30 days default).
- Time range selector: 7 days / 30 days / 90 days.
- Chart shows daily score points connected by line.
- Tap any point → tooltip with exact date and score value.
- Below chart: "Notable changes" list.
  - Date + delta + brief explanation (e.g., "+5 — 12 new reciprocal connections detected").
- Back button → SC1.

**States:**
- Loaded with history data.
- Insufficient data (<7 days): "Your score history is building. Check back in a few days."
- 90-day view: cached locally from score history.

---

## 3) Score Tab Navigation Map

```
SC1 Score Home
├── SC2 Component Detail (Quality)
├── SC2 Component Detail (Position)
├── SC2 Component Detail (Stability)
├── SC2 Component Detail (Trust)
├── SC3 How Scoring Works
└── SC4 Score History
```

---

## 4) Score Display Component (Reusable)

Used in Score tab (SC1) and Profile Home (P1 stats row).

### 4.1 Large Score Display

```
        ┌─────────┐
       ╱    72     ╲
      │    Good     │
       ╲           ╱
        └─────────┘
     Updated today 2:00 AM
```

- Circular progress ring: fill proportional to score (72/100 = 72% arc).
- Color: matches quality label color (blue for Good).
- Number: large bold font, centered.
- Label: below number, smaller font.

### 4.2 Mini Score Badge

For use in Profile Home stats row and contact cards:
```
[72 ●]
```
- Compact: number + colored dot.
- Tappable: navigates to Score tab.

### 4.3 Component Bar

```
Network Quality (40%)
████████████░░░░░  68%
```
- Horizontal bar with label and percentage.
- Fill color matches component (Quality=blue, Position=purple, Stability=green, Trust=orange).
- Tappable: navigates to SC2 for that component.

---

## 5) Explainability Strings

Dynamic one-sentence summary generated from component data:

| Condition | String |
|-----------|--------|
| Quality highest, all good | "Your score is strong because many of your connections are mutual and verified." |
| Position highest | "You're well-connected across different groups in your network." |
| Stability improving | "Your network is becoming more stable as connections persist over time." |
| Trust penalty active | "Your trust score is lower due to a recent account flag. Maintaining good standing will help." |
| New user, building | "Your score is building as we learn about your network. Keep adding and verifying contacts." |
| Quality low, many one-way | "Many of your contacts don't have you in their phone. Mutual connections boost your score." |

---

## 6) Premium Score Features

### 6.1 Who Viewed Me (Premium)

- Section on SC1 below components: "Who viewed your profile this week: 3 people".
- Tap → Premium paywall if not subscribed.
- If subscribed → Viewer list with names and timestamps.

### 6.2 Enhanced How Am I Stored (Premium)

- Section on SC1 or Profile: "How your contacts store you".
- Shows how your name appears in others' contact books.
- Tap → Premium paywall if not subscribed.
- If subscribed → List of stored names with match confidence.

---

## 7) Accessibility

- Score number: VoiceOver reads "Rin Score: 72 out of 100, rated Good".
- Component bars: "Network Quality: 68 percent, contributing 40 percent of total score".
- Sparkline: "Score trend over last 30 days. Tap for details."
- History chart: "Score history chart. Tap data points for exact values."

---

## 8) Open Decisions

1. Whether to show score comparison (e.g., "Top 20% of Rin users") or keep it purely personal.
2. Whether score change notifications should deep-link to SC2 (component that changed most) or SC1 (overview).
3. Whether the "Notable changes" in SC4 should explain the cause or just show the delta.
4. Whether to animate the score ring on first view (count-up animation from 0 to current value).
