# iOS Profile and Circle Management Screen Spec V1

## 1) Purpose

Screen-level specification for the Profile tab and Circles tab. Defines every screen, component, state, and transition for profile management, shadow profile switching, and circle management.

Companion docs:
- `docs/product/CIRCLE_MANAGEMENT_UX_V1.md` (circle behavior)
- `docs/product/SHADOW_PROFILE_UX_V1.md` (shadow profile behavior)
- `docs/architecture/IOS_NAVIGATION_STATE_V1.md` (navigation model)

---

## 2) Profile Tab Screens

### P1: Profile Home

**Layout:**
- Header: Active profile card (name, photo, username, profile type badge).
- Long-press avatar → card deck picker (shadow profile switcher).
- Stats row: contacts count | circles count | Rin Score mini.
- Section: "Your Profiles" — list of all profiles (primary + shadows).
- Section: "Quick Actions" — Edit Profile, Privacy Settings, Security Inbox, Settings.
- Section: "Account" — Premium status, Help, About Rin.

**States:**
- Default: primary profile active.
- Shadow active: header shows shadow profile, subtle "Viewing as [Shadow Name]" indicator.
- Premium badge if subscribed.

**Transitions:**
- Tap profile card → P2 (Profile Detail).
- Long-press avatar → P3 (Card Deck Picker).
- Tap any profile in list → P2 for that profile.
- Tap "Create New Profile" → P4 (Shadow Creation).
- Tap Security Inbox → Security Inbox screen (RinSecurity).
- Tap Settings → Settings screen (RinSettings).

---

### P2: Profile Detail / Edit

**Layout:**
- Large profile photo with edit overlay.
- Editable fields: Display name, username, bio, phone (read-only), email.
- Per-field visibility indicators (which circles can see each field).
- "Access Controls" button → P5 (Field-Level Access Matrix).
- If shadow profile: type badge (Professional/Personal/Anonymous).
- If shadow profile: "Reveal Identity" action (irreversible, with confirmation).
- Delete Profile button (for shadow profiles only).

**States:**
- View mode (default).
- Edit mode (tap Edit button).
- Saving (spinner on save button).
- Unsaved changes warning on back navigation.

---

### P3: Card Deck Picker (Shadow Profile Switcher)

**Layout:**
- Full-screen overlay with translucent background.
- Horizontal scrolling card deck ("pokemon card" style).
- Each card: profile photo, name, type badge, last-active indicator.
- Primary profile card always first (slightly larger).
- "+" card at end to create new shadow.
- Swipe to browse, tap to select and switch.

**States:**
- Browsing (swipe through cards).
- Switching (brief loading indicator on selected card).
- Switched (dismiss overlay, app reflects new active profile).

**Animation:**
- Cards fan out from avatar position.
- Selected card scales up and center-aligns before dismissal.
- 300ms spring animation.

---

### P4: Shadow Profile Creation

**Layout:**
- Screen 1: Choose type (Professional / Personal / Anonymous) with description cards.
- Screen 2: Set display name and photo.
- Screen 3: Configure initial circle assignments (which circles this shadow uses).
- Screen 4: Review and create.

**States:**
- Step indicator at top (4 steps).
- Back button returns to previous step.
- "Create" button on step 4 triggers creation.
- Success: auto-switch to new shadow, return to Profile Home.

---

### P5: Field-Level Access Matrix

**Layout:**
- Grid/table view.
- Rows: each field (name, phone, email, photo, bio, etc.).
- Columns: each circle (Contacts, Public, Family, Friends, Colleagues, custom).
- Cells: three-state toggle (Allow ✓ / Don't Allow ✗ / Ask ?).
- Tap cell to cycle through states.
- Bulk actions at top: "Allow All for Circle" / "Reset to Defaults".

**States:**
- Default state matches circle defaults from CIRCLE_MANAGEMENT_UX_V1.md.
- Modified cells highlighted with unsaved indicator.
- Save button applies all changes at once.

---

## 3) Circles Tab Screens

### C1: Circles Home

**Layout:**
- Header: "Circles" title.
- Mandatory circles section (Contacts, Public) — non-deletable, subtle lock icon.
- Prepopulated circles section (Family, Friends, Colleagues).
- Custom circles section (user-created).
- Each circle row: emoji + name + member count + color dot.
- "+" button in navigation bar → C3 (Create Circle).
- Smart merge suggestion banner (if applicable) → "2 circles look similar".

**States:**
- Default: all circles listed.
- Empty custom section: "Create your first circle" CTA.
- Merge suggestion visible: dismissible banner.

**Transitions:**
- Tap circle → C2 (Circle Detail).
- Tap "+" → C3 (Create Circle).
- Swipe left on custom circle → Delete option (with confirmation).

---

### C2: Circle Detail

**Layout:**
- Header: circle emoji + name + color (editable for custom circles).
- Member count and "Add Members" button.
- Member list with search/filter.
- "Access Policies" section showing field-level access summary.
- Tap any policy row → P5 (Field-Level Access Matrix, filtered to this circle).
- Pending access requests section (Ask flow requests from contacts).

**States:**
- View mode (default).
- Editing (for custom circles: name, emoji, color).
- Members loading.
- Empty circle: "Add your first member" CTA.

**Transitions:**
- Tap member → Contact Detail (RinContacts).
- Tap "Add Members" → C4 (Member Picker).
- Tap access request → C5 (Access Request Detail).

---

### C3: Create Circle

**Layout:**
- Name field (required).
- Emoji picker.
- Color picker (predefined palette).
- "Add Members" optional step → C4 (Member Picker).
- "Create" button.

**States:**
- Empty form.
- Valid (name entered).
- Creating (spinner).
- Success → navigate to C2 (new circle detail).

---

### C4: Member Picker

**Layout:**
- Search bar at top.
- Segmented control: All Contacts / By Circle.
- Contact list with checkboxes.
- Already-in-circle contacts shown with checkmark (non-removable from this view).
- Selected count at bottom with "Done" button.

**States:**
- Browsing.
- Searching (filtered list).
- Selecting (checkbox toggling).

---

### C5: Access Request Detail (Ask Flow)

**Layout:**
- Requester info: name, photo, relationship context.
- Requested field: what they want access to.
- Request reason (if provided).
- Two buttons: "Allow" / "Don't Allow".
- Optional: "Allow for all fields" toggle.

**States:**
- Pending (default).
- Approved (brief confirmation, then dismiss).
- Denied (brief confirmation, then dismiss).

---

## 4) Profile Tab Navigation Map

```
P1 Profile Home
├── P2 Profile Detail/Edit
│   └── P5 Field-Level Access Matrix
├── P3 Card Deck Picker
│   └── P4 Shadow Profile Creation
├── Security Inbox (RinSecurity)
└── Settings (RinSettings)
    └── Premium (RinPremium)
```

## 5) Circles Tab Navigation Map

```
C1 Circles Home
├── C2 Circle Detail
│   ├── P5 Field-Level Access Matrix (filtered)
│   ├── C4 Member Picker
│   ├── C5 Access Request Detail
│   └── Contact Detail (RinContacts)
└── C3 Create Circle
    └── C4 Member Picker
```

---

## 6) Open Decisions

1. Whether the card deck picker should support reordering profiles (drag to set preferred order).
2. Whether circle deletion should offer "Move members to another circle" or just remove membership.
3. Whether to show a circle's access policy summary as icons (✓/✗/?) or text on the Circles Home row.
4. Whether the member picker should support bulk selection (e.g., "add all Family contacts").
