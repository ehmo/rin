# iOS Search and Discovery Screen Spec V1

## 1) Purpose

Screen-level specification for search and discovery features across the app. Covers contact search, global search, and discovery surfaces.

Companion docs:
- `docs/architecture/SEARCH_RELEVANCE_STRATEGY_V1.md` (search backend)
- `docs/product/CONTACTS_IMPORT_SYNC_UX_V1.md` (contact list context)
- `docs/architecture/IOS_NAVIGATION_STATE_V1.md` (navigation model)

---

## 2) Search Entry Points

| Entry point | Location | Scope |
|------------|----------|-------|
| Home tab search bar | Top of contact list | All contacts (local + server) |
| Circles member search | Circle detail → Add Members | All contacts filtered |
| Global search | Spotlight / in-app search icon | Contacts + profiles + circles |

---

## 3) Screens

### S1: Contact Search (Home Tab)

**Layout:**
- Persistent search bar at top of contact list.
- Tap to activate: keyboard appears, list filters in real-time.
- Search input with clear button and cancel.
- Results grouped by match quality:
  - Exact matches (name, phone, email).
  - Fuzzy matches (partial name, nickname).
  - Enriched field matches (company, title from enrichment data).
- Each result row: photo + name + match context (e.g., "Phone: +1-555...").
- Empty state: "No contacts match '[query]'"
- Suggestion state (before typing): recent searches + suggested contacts.

**Search behavior:**
- Local-first: searches SwiftData cache immediately (0-latency).
- If query length >= 3: also triggers server search for enriched data.
- Results merge: local results shown instantly, server results append.
- Debounce: 300ms after last keystroke before server query.

**States:**
- Idle (search bar collapsed in list header).
- Active (keyboard up, ready for input).
- Typing (results filtering in real-time).
- Loading server results (subtle spinner next to search bar).
- Results displayed.
- No results.

**Transitions:**
- Tap result → Contact Detail.
- Tap cancel → dismiss search, restore full list.

---

### S2: Circle Member Search

**Layout:**
- Search bar within Member Picker (C4 from Profile/Circle spec).
- Searches only user's contacts (not global).
- Results show circle membership status (checkmark if already in circle).
- Multi-select enabled.

**Search behavior:**
- Local-only (SwiftData cache). No server call.
- Filters by display name, phone number, email.
- Instant results (no debounce needed for local search).

---

### S3: Global Search (Future v1.1+)

**Layout:**
- Accessible via Spotlight integration or dedicated search screen.
- Searches across: contacts, circles, profiles, settings.
- Results segmented by type.

**v1 scope:** Local contact search only (S1). Global search deferred.

---

## 4) Search Result Components

### 4.1 Contact Search Result Row

```
┌────────────────────────────────────┐
│ [Photo] Name                       │
│         Match context (grey)       │
│         Circle badges (tiny dots)  │
│                        [arrow >]   │
└────────────────────────────────────┘
```

- Photo: 40pt circle thumbnail.
- Name: primary display name, bold matched substring.
- Match context: what matched (phone number, email, company name).
- Circle badges: colored dots for circles this contact belongs to.

### 4.2 No Results State

```
┌────────────────────────────────────┐
│                                    │
│        🔍                          │
│   No contacts found                │
│   Try a different search term      │
│                                    │
│   [Add Contact Manually]           │
│                                    │
└────────────────────────────────────┘
```

### 4.3 Recent Searches

- Last 5 search queries stored locally.
- Shown when search is activated before typing.
- Tap to re-execute search.
- "Clear recent" button.

---

## 5) Search Implementation

### 5.1 Local Search (SwiftData)

```swift
// Simplified query
@Query(filter: #Predicate<CachedContact> { contact in
    contact.displayName.localizedStandardContains(searchText) ||
    contact.phones.contains { $0.number.contains(searchText) } ||
    contact.emails.contains { $0.address.contains(searchText) }
}, sort: \.displayName)
var searchResults: [CachedContact]
```

### 5.2 Server Search (PostgreSQL FTS)

- Endpoint: `SearchService.SearchContacts(query, limit, offset)`.
- Server uses `pg_trgm` for fuzzy matching + `tsvector` for full-text.
- Returns relevance-scored results.
- Client merges server results below local results (deduplicated by contact ID).

### 5.3 Search Ranking

Local results ordered by:
1. Exact name match (highest).
2. Name starts with query.
3. Name contains query.
4. Phone/email match.
5. Enriched field match (lowest).

Server results ordered by PostgreSQL relevance score.

---

## 6) Discovery Surfaces

### 6.1 Home Tab Smart Sections

The Home tab contact list includes discovery sections (defined in CONTACTS_IMPORT_SYNC_UX_V1.md):

| Section | Content | Trigger |
|---------|---------|---------|
| Dedup Review | Pending merge suggestions with confidence | After import/sync |
| Recently Added | Contacts added in last 7 days | After sync |
| Enriched | Contacts with new enrichment data | After enrichment update |
| Suggested Circles | Contacts that might belong to a circle | After circle creation |

### 6.2 Enrichment Discovery Cards

When a contact has new enrichment data:
```
┌────────────────────────────────────┐
│ ✨ New info for John Smith         │
│ Company: Acme Corp (enriched)      │
│ Title: VP Engineering (enriched)   │
│                                    │
│ [View Contact]     [Dismiss]       │
└────────────────────────────────────┘
```

---

## 7) Accessibility

- Search bar: VoiceOver label "Search contacts".
- Results: VoiceOver reads "Contact name, matched by [context]".
- No results: VoiceOver announces "No contacts found for [query]".
- Filter buttons: labeled descriptively.

---

## 8) Open Decisions

1. Whether to implement voice search ("Hey Siri, find John in Rin").
2. Whether search should support advanced operators (e.g., "circle:family" filter).
3. Whether to show a "People You May Know" section based on graph analysis.
4. Whether to index contact notes/tags for search in v1.
