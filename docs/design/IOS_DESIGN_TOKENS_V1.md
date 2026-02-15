# iOS Design Tokens and Component Inventory V1

## 1) Purpose

Define the visual foundation for the Rin iOS app: color tokens, typography scale, spacing system, and component inventory.

Companion docs:
- `docs/architecture/IOS_APP_ARCHITECTURE_V1.md` (RinUI package)
- `docs/product/IOS_ONBOARDING_SCREEN_SPEC_V1.md` (screen reference)

---

## 2) Color Tokens

### 2.1 Brand Colors

| Token | Hex | Usage |
|-------|-----|-------|
| `rin.brand.primary` | `#1A73E8` | Primary actions, links, active states |
| `rin.brand.secondary` | `#34A853` | Success states, positive indicators |
| `rin.brand.accent` | `#7C3AED` | Score ring, premium badge |
| `rin.brand.warning` | `#F59E0B` | Warnings, building state |
| `rin.brand.error` | `#EF4444` | Errors, destructive actions |

### 2.2 Semantic Colors

| Token | Light mode | Dark mode | Usage |
|-------|-----------|-----------|-------|
| `rin.bg.primary` | `#FFFFFF` | `#000000` | Main background |
| `rin.bg.secondary` | `#F9FAFB` | `#111111` | Grouped sections, cards |
| `rin.bg.tertiary` | `#F3F4F6` | `#1A1A1A` | Input fields, search bar |
| `rin.text.primary` | `#111827` | `#F9FAFB` | Headings, body text |
| `rin.text.secondary` | `#6B7280` | `#9CA3AF` | Captions, timestamps |
| `rin.text.tertiary` | `#9CA3AF` | `#6B7280` | Placeholders, disabled |
| `rin.border.default` | `#E5E7EB` | `#374151` | Card borders, dividers |
| `rin.border.focus` | `#1A73E8` | `#1A73E8` | Focused input borders |

### 2.3 Score Colors

| Token | Hex | Usage |
|-------|-----|-------|
| `rin.score.strong` | `#22C55E` | Score 80-100 |
| `rin.score.good` | `#3B82F6` | Score 60-79 |
| `rin.score.building` | `#F59E0B` | Score 30-59 |
| `rin.score.new` | `#9CA3AF` | Score 0-29 |

### 2.4 Component Colors

| Token | Hex | Usage |
|-------|-----|-------|
| `rin.component.quality` | `#3B82F6` | Quality bar |
| `rin.component.position` | `#8B5CF6` | Position bar |
| `rin.component.stability` | `#22C55E` | Stability bar |
| `rin.component.trust` | `#F97316` | Trust bar |

### 2.5 Circle Default Colors

| Circle | Hex | Token |
|--------|-----|-------|
| Contacts | `#6B7280` | `rin.circle.contacts` |
| Public | `#3B82F6` | `rin.circle.public` |
| Family | `#EF4444` | `rin.circle.family` |
| Friends | `#22C55E` | `rin.circle.friends` |
| Colleagues | `#8B5CF6` | `rin.circle.colleagues` |

---

## 3) Typography

### 3.1 Type Scale

All fonts use SF Pro (system font). Dynamic Type supported.

| Token | Size | Weight | Line height | Usage |
|-------|------|--------|-------------|-------|
| `rin.type.hero` | 34pt | Bold | 41pt | Score number |
| `rin.type.title1` | 28pt | Bold | 34pt | Screen titles |
| `rin.type.title2` | 22pt | Bold | 28pt | Section headers |
| `rin.type.title3` | 20pt | Semibold | 25pt | Card titles |
| `rin.type.headline` | 17pt | Semibold | 22pt | List item titles |
| `rin.type.body` | 17pt | Regular | 22pt | Body text |
| `rin.type.callout` | 16pt | Regular | 21pt | Secondary info |
| `rin.type.subheadline` | 15pt | Regular | 20pt | Metadata |
| `rin.type.footnote` | 13pt | Regular | 18pt | Timestamps, captions |
| `rin.type.caption` | 12pt | Regular | 16pt | Badges, tiny labels |

### 3.2 Dynamic Type Support

- All text uses `Font.system` with corresponding `TextStyle`.
- Layouts accommodate up to `AX5` accessibility size.
- Fixed-size elements (score ring, badges) use minimum 11pt.

---

## 4) Spacing

### 4.1 Spacing Scale

| Token | Value | Usage |
|-------|-------|-------|
| `rin.space.xs` | 4pt | Inline element gaps |
| `rin.space.sm` | 8pt | Tight padding, badge margin |
| `rin.space.md` | 12pt | Standard internal padding |
| `rin.space.base` | 16pt | Standard margin, section padding |
| `rin.space.lg` | 24pt | Section gaps |
| `rin.space.xl` | 32pt | Screen top/bottom padding |
| `rin.space.2xl` | 48pt | Major section dividers |

### 4.2 Component Spacing

| Component | Internal padding | External margin |
|-----------|-----------------|-----------------|
| Card | `base` (16pt) | `sm` (8pt) vertical |
| List row | `base` horizontal, `md` vertical | 0 |
| Button | `md` vertical, `lg` horizontal | — |
| Section header | `base` horizontal, `lg` top | — |
| Screen | `base` horizontal, `xl` top | — |

---

## 5) Corner Radius

| Token | Value | Usage |
|-------|-------|-------|
| `rin.radius.sm` | 4pt | Small badges |
| `rin.radius.md` | 8pt | Input fields, small cards |
| `rin.radius.lg` | 12pt | Cards, modals |
| `rin.radius.xl` | 16pt | Large cards, sheets |
| `rin.radius.full` | Capsule | Buttons, pills, avatars |

---

## 6) Component Inventory

### 6.1 Core Components (RinUI)

| Component | Variants | Used in |
|-----------|----------|---------|
| `AvatarView` | Sizes: xs(24), sm(32), md(40), lg(56), xl(80). With/without badge. | Contact list, profile, circles |
| `ScoreBadge` | Mini (inline), compact (stats row), large (score tab) | Score tab, profile, contact detail |
| `ComponentBar` | Standard, interactive (tappable) | Score tab |
| `CircleDot` | Single dot, dot row (multi-circle) | Contact list, circle indicators |
| `AccessStateToggle` | Allow(✓), Don't Allow(✗), Ask(?) | Access matrix |
| `CardView` | Standard, highlighted, interactive | Dedup cards, shadow picker |
| `SectionHeader` | With/without action button | List sections |
| `EmptyStateView` | Icon + title + subtitle + optional CTA | Empty lists, no results |
| `StatusBanner` | Info, warning, error, offline | Global status |
| `DedupCard` | Confidence tier badge, evidence list, action buttons | Home tab dedup section |
| `ProfileCard` | Full (picker), compact (list) | Shadow picker, profile list |
| `SparklineView` | 30-point line chart, tappable | Score tab |
| `SearchBar` | Standard, with filter | Home tab, member picker |
| `PrimaryButton` | Standard, loading, disabled | Forms, actions |
| `SecondaryButton` | Standard, destructive | Forms, secondary actions |
| `TabBadge` | Numeric, dot | Tab bar |
| `EnrichmentBadge` | Inline indicator | Contact detail |

### 6.2 Component States

Every interactive component supports:
- Default
- Pressed/highlighted
- Disabled
- Loading
- Error (where applicable)

---

## 7) Iconography

- Use SF Symbols exclusively (no custom icon sets).
- Consistent weight: `.medium` for navigation, `.regular` for content.
- Tab icons:

| Tab | SF Symbol | Filled variant |
|-----|-----------|----------------|
| Home | `person.crop.rectangle.stack` | `person.crop.rectangle.stack.fill` |
| Circles | `circle.grid.2x2` | `circle.grid.2x2.fill` |
| Score | `chart.bar.xaxis` | `chart.bar.xaxis` (no fill variant, use color) |
| Profile | `person.circle` | `person.circle.fill` |

---

## 8) Motion

| Animation | Duration | Curve | Usage |
|-----------|----------|-------|-------|
| Navigation push | 350ms | `.spring(response: 0.35)` | System default |
| Sheet present | 300ms | `.spring(response: 0.3)` | Modal sheets |
| Card deck fan | 300ms | `.spring(response: 0.3, dampingFraction: 0.8)` | Shadow picker |
| Score ring fill | 800ms | `.easeOut` | Score first load |
| Badge appear | 200ms | `.spring(response: 0.2)` | Tab badges, indicators |
| Dedup card dismiss | 250ms | `.easeInOut` | Swipe to dismiss |

---

## 9) Dark Mode

- All tokens have light/dark variants (see §2.2).
- Use `@Environment(\.colorScheme)` for conditional styling.
- System automatic switching (no manual toggle in v1).
- Brand colors remain constant across modes.
- Score colors remain constant across modes.
- Test all screens in both modes before release.

---

## 10) Open Decisions

1. Whether to use Apple's Liquid Glass effects (iOS 26+) or keep flat design for broader iOS 16+ support.
2. Whether to create a dedicated icon set for score components or use SF Symbols with color.
3. Whether the brand primary color should be more distinctive than standard blue.
4. Whether to support custom themes or tints in a future version.
