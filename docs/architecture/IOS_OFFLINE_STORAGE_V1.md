# iOS Local Storage and Offline Behavior V1

## 1) Purpose

Define the local storage strategy, caching model, and offline behavior for the iOS app. Read-only cache for offline viewing; mutations require connectivity.

Companion docs:
- `docs/architecture/IOS_APP_ARCHITECTURE_V1.md` (module structure)
- `docs/architecture/IOS_API_CLIENT_V1.md` (API client and offline queue)

---

## 2) Storage Technologies

| Technology | Use case | Data type |
|-----------|----------|-----------|
| **SwiftData** | Contact cache, circle membership, score history, dedup queue, mutation queue | Structured domain data |
| **UserDefaults** | Preferences, feature flags, last sync timestamp, onboarding completion | Simple key-value |
| **Keychain** | Auth tokens, encryption keys | Sensitive credentials |
| **FileManager** | Profile photos cache, exported data | Binary files |

---

## 3) SwiftData Models

### 3.1 Contact Cache

```
CachedContact
├── id: String (server contact ID)
├── displayName: String
├── phones: [CachedPhone]
├── emails: [CachedEmail]
├── photoURL: String?
├── photoData: Data? (thumbnail cache)
├── circles: [String] (circle IDs)
├── profileClass: String
├── enrichmentBadges: [String]
├── lastSyncedAt: Date
├── isStale: Bool (computed: lastSyncedAt > 24h ago)
```

### 3.2 Circle Cache

```
CachedCircle
├── id: String (server circle ID)
├── name: String
├── emoji: String?
├── color: String (hex)
├── type: String (mandatory/prepopulated/custom)
├── memberCount: Int
├── accessPolicies: [CachedAccessPolicy]
├── lastSyncedAt: Date
```

### 3.3 Score Cache

```
CachedScore
├── value: Int (0-100)
├── quality: Double (0-1)
├── position: Double (0-1)
├── stability: Double (0-1)
├── trust: Double (0-1)
├── formulaVersion: String
├── computedAt: Date
├── history: [CachedScorePoint] (last 30 days)
```

### 3.4 Dedup Queue

```
CachedDedupSuggestion
├── id: String
├── contactA_id: String
├── contactB_id: String
├── confidence: Double
├── tier: String (auto/review/low)
├── matchEvidence: [String]
├── status: String (pending/resolved/dismissed)
├── resolvedAt: Date?
```

---

## 4) Caching Strategy

### 4.1 Cache Lifecycle

```
App launch
    ↓
Load cached data from SwiftData (instant)
    ↓
Display cached data to user
    ↓
Background: fetch fresh data from API
    ↓
Merge API response into SwiftData cache
    ↓
UI updates reactively via @Query / observation
```

### 4.2 Cache Freshness

| Data type | Freshness window | Stale indicator |
|-----------|-----------------|-----------------|
| Contacts list | 24 hours | None (stale fetch happens silently) |
| Contact detail | 1 hour | "Last updated X ago" if >24h |
| Circles | 24 hours | None |
| Score | 24 hours | "Estimated" label if >24h |
| Dedup suggestions | Real-time (sync-triggered) | None |
| Profile | 1 hour | None |

### 4.3 Cache Invalidation

Cache invalidated (re-fetch triggered) when:
- Contact sync detects changes (`CNContactStoreDidChangeNotification`).
- User performs a mutation (create, update, delete).
- Push notification indicates server-side change.
- App returns from background after >1 hour.
- User triggers manual pull-to-refresh.

---

## 5) Offline Behavior

### 5.1 What Works Offline

| Feature | Offline behavior |
|---------|-----------------|
| View contact list | Cached data displayed |
| View contact detail | Cached data displayed |
| View circles and members | Cached data displayed |
| View Rin Score | Cached score with "Last updated" timestamp |
| View score history | Cached 30-day sparkline |
| Search contacts | Local search over cached contacts |
| View profile | Cached profile data |

### 5.2 What Requires Connectivity

| Feature | Offline behavior |
|---------|-----------------|
| Import contacts | Queued, resumes when online |
| Edit contact/circle | Queued in mutation queue |
| Resolve dedup suggestion | Queued in mutation queue |
| Change access policies | Queued in mutation queue |
| Create/delete circle | Queued in mutation queue |
| View enrichment data | Show cached if available, "Offline" badge if not |
| Subscribe to premium | Blocked — show "Connect to purchase" |
| File dispute | Queued in mutation queue |
| Switch shadow profile | Cached profiles available, mutations queued |

### 5.3 Offline UI Indicators

- **Global**: Subtle offline banner at top of screen when no connectivity.
- **Per-action**: "Will sync when online" toast after queued mutation.
- **Score**: "Last updated X ago" when score is stale.
- **No modals or blocking dialogs** for offline state — app remains usable.

---

## 6) Sync Architecture

### 6.1 Full Sync

On first launch or after extended offline period:
1. Fetch all contacts (paginated).
2. Fetch all circles.
3. Fetch current score.
4. Fetch pending dedup suggestions.
5. Store everything in SwiftData.

### 6.2 Incremental Sync

After initial sync:
1. `CNContactStoreDidChangeNotification` triggers diff detection.
2. Changed contacts sent to server.
3. Server returns updated data (new enrichments, dedup suggestions, score impact).
4. SwiftData cache updated.

### 6.3 Background Sync

- `BGAppRefreshTask` scheduled daily as fallback.
- Fetches: score update, new dedup suggestions, circle changes, enrichment updates.
- Budget: <30 seconds of background processing time.
- No user-visible UI during background sync.

---

## 7) Storage Limits

### 7.1 Size Estimates

| Data type | Per-user estimate | 10K contacts |
|-----------|------------------|--------------|
| Contact records | ~500 bytes each | ~5 MB |
| Circle records | ~200 bytes each | ~1 KB (5 circles) |
| Score history | ~50 bytes/day | ~1.5 KB (30 days) |
| Dedup suggestions | ~300 bytes each | ~30 KB (100 pending) |
| Profile photos (thumbnails) | ~10 KB each | ~100 MB (10K thumbnails) |
| **Total (excluding photos)** | — | **~5 MB** |
| **Total (with photos)** | — | **~105 MB** |

### 7.2 Photo Cache Policy

- Cache contact photo thumbnails (100x100) locally.
- Full-size photos fetched on demand (not cached).
- LRU eviction when photo cache exceeds 200 MB.
- Photos purged on account deletion.

---

## 8) Data Migration

### 8.1 SwiftData Schema Versioning

- Use SwiftData's `VersionedSchema` and `SchemaMigrationPlan`.
- Each app version can define a new schema version.
- Lightweight migrations (add field, rename) handled automatically.
- Heavy migrations (data transformation) via custom `MigrationStage`.

### 8.2 Migration Testing

- Test migrations from every previous schema version to current.
- Include in CI pipeline with fixture databases.

---

## 9) Security

### 9.1 Data at Rest

- SwiftData database stored in app sandbox (protected by iOS data protection).
- Keychain items tagged with `kSecAttrAccessibleAfterFirstUnlock`.
- No sensitive data in UserDefaults (only preferences).
- Photo cache in app's Caches directory (system can evict).

### 9.2 Account Deletion

On account deletion:
1. Clear SwiftData database.
2. Clear Keychain entries.
3. Clear UserDefaults.
4. Clear photo cache.
5. Clear mutation queue.
6. Reset app to onboarding state.

---

## 10) Open Decisions

1. Whether SwiftData is stable enough for production or Core Data should be used as fallback.
2. Whether to implement a contact photo prefetch strategy (preload thumbnails for visible contacts).
3. Whether offline search should use SwiftData queries or an in-memory index (performance tradeoff).
4. Maximum offline duration before forcing a full re-sync vs incremental catch-up.
