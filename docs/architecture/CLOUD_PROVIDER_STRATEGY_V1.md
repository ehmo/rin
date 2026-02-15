# Cloud Provider Strategy V1

## 1) Purpose

Define the cloud provider selection, deployment topology, and portability strategy for Rin. Optimized for indie/solo founder economics with strong data sovereignty.

Companion docs:
- `docs/architecture/SYSTEM_ARCHITECTURE_DB_FIRST_V2.md` (workload requirements)
- `docs/architecture/BACKEND_MIGRATION_GUIDE_V1.md` (scaling stages)

---

## 2) Provider Selection

### 2.1 Primary Stack

| Component | Provider | Service | Rationale |
|-----------|----------|---------|-----------|
| **Edge/CDN** | Cloudflare | CDN, DNS, DDoS protection | Free tier excellent. Global edge. |
| **Compute** | Hetzner Cloud | Cloud VMs (CPX/CAX series) | Best price/performance in EU. ARM available. |
| **Managed Postgres** | Ubicloud or Neon | Managed PostgreSQL | Zero-ops DB. Ubicloud runs on Hetzner hardware. |
| **Object Storage** | Hetzner | Object Storage (S3-compatible) | WAL-G backups, media, Iceberg tables. |
| **NATS JetStream** | Self-hosted on Hetzner | NATS cluster | Simple to operate, lightweight. |
| **Container Runtime** | Hetzner | Docker on VMs (or k3s) | Simple deployment. No Kubernetes complexity. |

### 2.2 Cost Comparison (Estimated Monthly at v1 Scale)

| Provider combo | Compute | Database | Storage | Total |
|---------------|---------|----------|---------|-------|
| **Hetzner + Ubicloud** | €20 (CPX31) | €15 (managed PG) | €5 | **~€40/mo** |
| AWS (ECS + RDS) | $50 (t3.medium) | $50 (db.t3.micro) | $5 | ~$105/mo |
| GCP (Cloud Run + SQL) | $40 | $45 | $5 | ~$90/mo |
| Fly.io + Neon | $30 | $19 (Launch plan) | $5 | ~$54/mo |

### 2.3 Why Not Hyperscalers

- **Cost**: 2-3x more expensive for equivalent resources.
- **Complexity**: IAM, VPC, security groups — overkill for solo founder.
- **Lock-in**: Proprietary services (Lambda, DynamoDB) create switching costs.
- **Data sovereignty**: Hetzner has EU-only data centers (GDPR-friendly).

---

## 3) Deployment Topology

### 3.1 Stage A (Monolith, 0-1,000 Users)

```
Cloudflare (CDN/DNS/DDoS)
    ↓
Hetzner Cloud VM (CPX31: 4 vCPU, 8 GB RAM)
├── Go monolith (Docker)
├── NATS JetStream (Docker)
└── Redis (optional, for caching)
    ↓
Managed PostgreSQL (Ubicloud/Neon)
    ↓
Hetzner Object Storage (backups, media)
```

Single VM. Simple. ~€40/month.

### 3.2 Stage B (Workers Split, 1,000-10,000 Users)

```
Cloudflare (CDN/DNS/DDoS)
    ↓
Hetzner Cloud VMs
├── VM 1: API monolith (CPX31)
├── VM 2: Workers (Score, Search, Dispute) (CPX21)
└── VM 3: NATS cluster node (CPX11)
    ↓
Managed PostgreSQL (scaled up)
    ↓
Hetzner Object Storage
```

3 VMs. Workers isolated. ~€80/month.

### 3.3 Stage C (Service Split, 10,000+ Users)

```
Cloudflare (CDN/DNS/Load balancing)
    ↓
Hetzner Cloud VMs (or k3s cluster)
├── API Gateway/BFF (2x CPX21)
├── Identity Service (CPX11)
├── Contacts Service (CPX21)
├── Circles Service (CPX11)
├── Security Service (CPX11)
├── Workers (CPX21)
└── NATS cluster (3x CPX11)
    ↓
Managed PostgreSQL (HA configuration)
    ↓
Hetzner Object Storage
```

10+ VMs or k3s cluster. ~€200-400/month.

---

## 4) Portability Strategy

### 4.1 Portability Principles

1. **No proprietary services**: Every component has an open-source equivalent.
2. **Docker everywhere**: All services containerized with Dockerfile.
3. **Standard protocols**: PostgreSQL (SQL), NATS (NATS protocol), S3 (S3-compatible API).
4. **Infrastructure as code**: Terraform/OpenTofu for provisioning.
5. **DNS via Cloudflare**: Can point anywhere. Not tied to compute provider.

### 4.2 Portability Matrix

| Component | Portable to | Migration effort |
|-----------|------------|-----------------|
| Go services (Docker) | Any cloud with Docker/k8s | Hours (re-deploy containers) |
| PostgreSQL | Any Postgres provider | Hours (pg_dump/restore or replication) |
| NATS JetStream | Any server | Hours (re-deploy, replay from streams) |
| Object Storage | Any S3-compatible | Days (rclone sync) |
| Cloudflare DNS | — | Change target IPs |
| Terraform configs | Any provider | Days (rewrite provider blocks) |

### 4.3 Exit Scenarios

| Scenario | Target | Effort |
|----------|--------|--------|
| Hetzner outage | Migrate to OVH/Vultr (similar EU hosting) | 1-2 days |
| Need US presence | Add Fly.io or AWS region for US traffic | 1 day |
| Acquisition/scale | Migrate to AWS/GCP for enterprise features | 1-2 weeks |
| Cost reduction | Migrate to dedicated servers (Hetzner bare metal) | 2-3 days |

---

## 5) Ubicloud Integration

### 5.1 What is Ubicloud

Open-source alternative to AWS that runs on Hetzner's bare metal servers. Provides:
- Managed PostgreSQL (with HA, automated backups).
- Virtual machines.
- Managed Kubernetes (future).
- S3-compatible storage.

### 5.2 Why Ubicloud for Rin

- Runs on Hetzner hardware = same pricing + managed services.
- Open source = no vendor lock-in to Ubicloud itself.
- Managed Postgres eliminates DB ops (backups, failover, monitoring).
- EU data residency guaranteed.

### 5.3 Fallback if Ubicloud

If Ubicloud doesn't meet needs:
- **Neon**: Managed Postgres with serverless scaling. Branching for dev/staging.
- **Supabase**: Managed Postgres + auth + storage. More features but more coupling.
- **Self-managed**: PostgreSQL on Hetzner VM with WAL-G backups. More ops work.

---

## 6) Networking and Security

### 6.1 Network Architecture

- All VMs in Hetzner private network (no public IPs for backend services).
- Only API gateway has public IP (behind Cloudflare proxy).
- Managed Postgres accessible only from private network.
- NATS accessible only from private network.

### 6.2 Cloudflare Services Used

| Service | Tier | Purpose |
|---------|------|---------|
| DNS | Free | Domain management |
| CDN | Free | Static asset caching, DDoS |
| SSL/TLS | Free | Edge TLS termination |
| WAF | Pro ($20/mo) | Web application firewall (add when needed) |
| Rate Limiting | Free (basic) | API rate limiting at edge |
| Workers | Free (100K/day) | Edge logic if needed |

### 6.3 Firewall Rules

- Hetzner Cloud Firewall: allow only Cloudflare IPs → API gateway.
- Private network: allow all internal traffic.
- SSH: key-only, from specific IPs.
- Managed DB: private network access only.

---

## 7) Backup Strategy

### 7.1 Database Backups (Managed Postgres)

Handled by provider (Ubicloud/Neon):
- Continuous WAL archiving.
- Point-in-time recovery.
- Automated daily snapshots.
- Cross-region replication (if offered).

### 7.2 Application Backups

| What | Method | Frequency | Retention |
|------|--------|-----------|-----------|
| Docker images | Container registry (GHCR or Hetzner registry) | Every deploy | 30 days |
| Configuration | Git (encrypted with SOPS/age) | Every change | Indefinite |
| Object storage | Hetzner versioned buckets | Continuous | 30 days |
| NATS streams | JetStream file storage with replication | Continuous | Per-stream config |

### 7.3 Restore Drills

- **Monthly**: Test database restore from backup to staging.
- **Quarterly**: Full disaster recovery drill (provision from scratch, restore data).
- **Document**: Restore procedure and time-to-recovery for each component.

---

## 8) Monitoring

### 8.1 Minimal Monitoring Stack (v1)

| Tool | Purpose | Cost |
|------|---------|------|
| Sentry | Crash reporting, error tracking | Free tier (5K events/mo) |
| Hetzner Cloud Console | VM metrics (CPU, memory, disk, network) | Free |
| PostgreSQL provider dashboard | DB metrics, slow queries | Included |
| UptimeRobot or Betteruptime | API health check | Free tier |

### 8.2 What to Monitor

| Signal | Alert threshold | Check method |
|--------|----------------|-------------|
| API health | Down >1 minute | UptimeRobot HTTP check |
| VM CPU | >80% for >10 minutes | Hetzner alerts |
| VM disk | >85% capacity | Hetzner alerts |
| DB connections | >80% pool capacity | Provider dashboard |
| Sentry error rate | >10 errors/minute | Sentry alert rules |

---

## 9) Open Decisions

1. Whether to start with Ubicloud managed Postgres or Neon (serverless, branching for dev environments).
2. Whether to use k3s from the start (lightweight Kubernetes) or plain Docker Compose.
3. Whether to add a second Hetzner region for geographic redundancy.
4. Whether Cloudflare Workers should handle any API logic (rate limiting, auth verification) at the edge.
5. Whether to use Hetzner's managed load balancer or Cloudflare load balancing.
