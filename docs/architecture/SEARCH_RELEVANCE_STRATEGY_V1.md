# Search Relevance and Indexing Strategy V1

## 1) Purpose

Define the search architecture for contacts and profiles using PostgreSQL full-text search. No external search engine in v1.

Companion docs:
- `docs/architecture/SYSTEM_ARCHITECTURE_DB_FIRST_V2.md` (database design)
- `docs/product/IOS_SEARCH_DISCOVERY_SCREEN_SPEC_V1.md` (search UX)

---

## 2) Search Engine: PostgreSQL

### 2.1 Why PostgreSQL FTS

- Zero additional infrastructure (already running Postgres).
- `pg_trgm` extension: fuzzy matching, typo tolerance, similarity scoring.
- `tsvector`/`tsquery`: full-text search with relevance ranking.
- Handles 100K contacts per user easily at v1 scale.
- GIN/GiST indexes for sub-millisecond search.

### 2.2 When to Reconsider

Migrate to dedicated search (Typesense/Meilisearch) when:
- Search query volume exceeds 1,000 QPS sustained.
- Complex search features needed (facets, geo-search, multi-language stemming).
- Search index freshness requirement drops below 1 second.

---

## 3) Indexing Strategy

### 3.1 Searchable Fields

| Field | Source | Weight | Index type |
|-------|--------|--------|-----------|
| Display name | Contact record | A (highest) | tsvector + trigram |
| Phone number | Contact record | B | trigram (prefix match) |
| Email address | Contact record | B | trigram |
| Company name | Enrichment data | C | tsvector |
| Job title | Enrichment data | C | tsvector |
| Circle names | Circle membership | D (lowest) | tsvector |
| Username | Profile record | B | trigram (exact + prefix) |

### 3.2 tsvector Column

Materialized search vector combining weighted fields:

```sql
ALTER TABLE contacts ADD COLUMN search_vector tsvector
  GENERATED ALWAYS AS (
    setweight(to_tsvector('simple', coalesce(display_name, '')), 'A') ||
    setweight(to_tsvector('simple', coalesce(company_name, '')), 'C') ||
    setweight(to_tsvector('simple', coalesce(job_title, '')), 'C')
  ) STORED;

CREATE INDEX idx_contacts_search ON contacts USING GIN (search_vector);
```

### 3.3 Trigram Index

For fuzzy name matching and phone prefix search:

```sql
CREATE EXTENSION IF NOT EXISTS pg_trgm;
CREATE INDEX idx_contacts_name_trgm ON contacts USING GIN (display_name gin_trgm_ops);
CREATE INDEX idx_contacts_phone_trgm ON contacts USING GIN (phone_normalized gin_trgm_ops);
CREATE INDEX idx_contacts_email_trgm ON contacts USING GIN (email gin_trgm_ops);
```

---

## 4) Search Query Strategy

### 4.1 Query Flow

```
User types "jon sm"
    ↓
Client: local SwiftData search (instant)
    ↓ (if query >= 3 chars, debounce 300ms)
Client: RPC SearchContacts(query="jon sm", limit=20)
    ↓
Server: parallel queries
    ├── Full-text: ts_rank(search_vector, plainto_tsquery('simple', 'jon sm'))
    ├── Trigram: similarity(display_name, 'jon sm')
    └── Phone prefix: phone_normalized LIKE '555%' (if numeric input)
    ↓
Server: merge results, deduplicate, rank by combined score
    ↓
Client: merge server results with local results (dedup by ID)
```

### 4.2 Combined Ranking

```sql
SELECT *,
  ts_rank(search_vector, plainto_tsquery('simple', $1)) * 2 AS fts_score,
  similarity(display_name, $1) AS trgm_score,
  (ts_rank(search_vector, plainto_tsquery('simple', $1)) * 2 + similarity(display_name, $1)) AS combined_score
FROM contacts
WHERE
  search_vector @@ plainto_tsquery('simple', $1)
  OR similarity(display_name, $1) > 0.3
  OR phone_normalized LIKE $2  -- phone prefix if numeric
ORDER BY combined_score DESC
LIMIT 20;
```

### 4.3 Search by Profile Class

| Profile class | Searchable by | Additional rules |
|---------------|--------------|-----------------|
| Personal | Owner only (their contacts) | Default scope |
| Shadow (Professional) | Discoverable if set to public | Separate search index |
| Shadow (Personal) | Owner only | Never in public search |
| Shadow (Anonymous) | Not searchable | Excluded from all indexes |
| Business (v2) | Public search | Separate business index |

---

## 5) Performance Targets

| Metric | Target | Measured at |
|--------|--------|-------------|
| Search latency (p50) | <50ms | Server-side |
| Search latency (p95) | <200ms | Server-side |
| Trigram match threshold | >0.3 similarity | Balances recall vs precision |
| Max results per query | 20 | Paginated if more needed |
| Index update lag | <5 seconds | After contact change |

---

## 6) Index Maintenance

- `search_vector` is `GENERATED ALWAYS AS ... STORED` — auto-updated on row changes.
- Trigram indexes auto-maintained by PostgreSQL.
- `VACUUM` and `REINDEX` scheduled weekly during low-traffic window.
- Monitor index size and bloat via `pg_stat_user_indexes`.

---

## 7) Open Decisions

1. Whether to use `simple` or language-specific text search configuration (e.g., `english`) for stemming.
2. Whether to implement search suggestion/autocomplete (prefix-based) as a separate lightweight endpoint.
3. Whether to log search queries for relevance tuning or treat them as sensitive data.
4. Whether contacts search should span across shadow profiles or be scoped to active profile.
