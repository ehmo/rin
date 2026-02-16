# On-Premises / Hybrid Reference Architecture V1

## 1) Purpose

Define a reference architecture for deploying Rin on-premises or in a hybrid configuration using K3s (lightweight Kubernetes). This document covers topology, component layout, networking, storage, high availability, backups, monitoring, security, migration paths, and resource requirements.

Target audience: operators deploying Rin outside the primary Hetzner Cloud stack -- whether for data sovereignty, air-gapped environments, self-hosted community instances, or cost optimization on owned hardware.

Companion docs:
- `docs/architecture/CLOUD_PROVIDER_STRATEGY_V1.md` (primary cloud stack)
- `docs/architecture/SERVICE_IMPLEMENTATION_BLUEPRINT_V1.md` (service boundaries)
- `docs/architecture/BACKEND_MIGRATION_GUIDE_V1.md` (monolith -> distributed stages)
- `docs/architecture/SECRETS_CONFIG_MANAGEMENT_V1.md` (secret lifecycle)
- `docs/architecture/SYSTEM_ARCHITECTURE_DB_FIRST_V2.md` (system architecture)

---

## 2) Why K3s

K3s sits at the sweet spot between Docker Compose (insufficient for HA/redundancy) and full K8s (excessive operational overhead for solo/small-team deployments).

| Option | Pros | Cons | Verdict |
|--------|------|------|---------|
| **Docker Compose** | Simplest setup, familiar | No HA, no rolling updates, manual scaling, no built-in health management | Dev/test only |
| **K3s** | Single binary, built-in Traefik, HA with embedded etcd, lightweight (~512MB RAM overhead), CNCF certified K8s | Still Kubernetes (learning curve exists) | **Production on-prem** |
| **Full K8s (kubeadm/RKE2)** | Full ecosystem, enterprise support | Heavy control plane (2-4GB RAM), complex etcd management, overkill at this scale | Only if mandated by policy |

Decision: K3s for on-prem production. Docker Compose as a development/testing fallback (Section 14).

---

## 3) Deployment Topology

### 3.1 Minimum Production Cluster (2 Nodes)

```
                    Internet
                       |
                  [Firewall/Router]
                       |
              +--------+--------+
              |                 |
        +-----+------+   +-----+------+
        |  Node 1    |   |  Node 2    |
        |  (server)  |   |  (server)  |
        |            |   |            |
        | K3s server |   | K3s server |
        | etcd       |   | etcd       |
        | Traefik    |   | Traefik    |
        | API pod    |   | API pod    |
        | Worker pod |   | Worker pod |
        | PG primary |   | PG replica |
        | NATS node  |   | NATS node  |
        | Monitoring |   |            |
        +------------+   +------------+
              |                 |
        [Shared/local storage]
```

Both nodes run as K3s servers with embedded etcd for HA. If one node dies, the other continues serving traffic. This is the minimum viable production topology.

Limitation: 2-node etcd is not quorum-safe. If one node fails, the surviving node can serve but cannot elect a new leader if both restart simultaneously. For true HA, use 3 nodes.

### 3.2 Recommended Production Cluster (3 Nodes)

```
                       Internet
                          |
                   [Load Balancer / VIP]
                          |
          +---------------+---------------+
          |               |               |
    +-----+------+  +----+-------+  +----+-------+
    |  Node 1    |  |  Node 2    |  |  Node 3    |
    |  server    |  |  server    |  |  server    |
    |            |  |            |  |            |
    | K3s server |  | K3s server |  | K3s server |
    | etcd       |  | etcd       |  | etcd       |
    | API pod    |  | API pod    |  | API pod    |
    | NATS node  |  | NATS node  |  | NATS node  |
    +------------+  +------------+  +------------+
          |               |               |
    [PG primary]    [PG replica]    [PG replica]
    [Workers]       [Score worker]  [Monitoring]
```

3-node etcd provides proper quorum (tolerates 1 node failure). PostgreSQL runs primary on one node with streaming replicas on the others.

### 3.3 Hybrid Topology (On-Prem Compute + Cloud Database)

For operators who want on-prem compute but managed database:

```
    On-Premises                          Cloud
    +-----------------+                  +------------------+
    | K3s Cluster     |   TLS/WireGuard  | Managed Postgres |
    | (2-3 nodes)     | <--------------> | (Neon/Ubicloud)  |
    |                 |                  +------------------+
    | API + Workers   |
    | NATS JetStream  |   TLS            +------------------+
    | Redis (cache)   | <--------------> | Object Storage   |
    | Monitoring      |                  | (S3-compatible)  |
    +-----------------+                  +------------------+
```

This hybrid model eliminates the hardest operational burden (database management) while keeping compute on-prem.

### 3.4 Node Roles

All nodes in K3s run as `server` (control plane + workload). K3s supports `agent`-only nodes, but at 2-3 node scale, every node should be a server for redundancy. Add agent-only nodes when scaling beyond 3 nodes for workload-only capacity.

```bash
# Node 1 (initial server)
curl -sfL https://get.k3s.io | sh -s - server \
  --cluster-init \
  --tls-san=<load-balancer-ip> \
  --disable=servicelb \
  --write-kubeconfig-mode=644

# Node 2, 3 (join as servers)
curl -sfL https://get.k3s.io | sh -s - server \
  --server https://<node1-ip>:6443 \
  --token <node-token> \
  --tls-san=<load-balancer-ip> \
  --disable=servicelb
```

Flag rationale:
- `--cluster-init`: enables embedded etcd (required for multi-server HA).
- `--tls-san`: adds the load balancer IP to the API server certificate.
- `--disable=servicelb`: use MetalLB or external LB instead of K3s's built-in ServiceLB (more control over IP allocation).

---

## 4) Component Layout

### 4.1 Namespace Organization

```
rin-system/          # Core application workloads
  ├── rin-api        # Go monolith (ConnectRPC)
  ├── rin-worker     # Outbox publisher + core consumers
  ├── rin-score      # Score/lake orchestration worker
  ├── nats           # NATS JetStream cluster
  └── redis          # Cache (optional, per Cloud Provider Strategy)

rin-data/            # Stateful data services
  ├── postgresql     # Primary + replicas (if self-managed)
  └── backups        # Backup CronJobs

rin-monitoring/      # Observability stack
  ├── prometheus     # Metrics collection (or VictoriaMetrics)
  ├── grafana        # Dashboards
  └── alertmanager   # Alert routing

kube-system/         # K3s system components (Traefik, CoreDNS, etc.)
```

### 4.2 Pod Specifications

#### API Server (rin-api)

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: rin-api
  namespace: rin-system
spec:
  replicas: 2                    # One per node minimum
  strategy:
    type: RollingUpdate
    rollingUpdate:
      maxUnavailable: 1
      maxSurge: 1
  template:
    spec:
      affinity:
        podAntiAffinity:         # Spread across nodes
          preferredDuringSchedulingIgnoredDuringExecution:
          - weight: 100
            podAffinityTerm:
              topologyKey: kubernetes.io/hostname
      containers:
      - name: rin-api
        image: ghcr.io/rin/server:latest
        command: ["/app/api"]
        ports:
        - containerPort: 8080    # HTTP (ConnectRPC)
          name: http
        - containerPort: 9090    # Metrics
          name: metrics
        resources:
          requests:
            cpu: 250m
            memory: 256Mi
          limits:
            cpu: "2"
            memory: 1Gi
        livenessProbe:
          httpGet:
            path: /healthz
            port: 8080
          initialDelaySeconds: 5
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /readyz
            port: 8080
          initialDelaySeconds: 5
          periodSeconds: 5
        env:
        - name: DATABASE_URL
          valueFrom:
            secretKeyRef:
              name: rin-db-credentials
              key: url
        - name: NATS_URL
          value: "nats://nats.rin-system.svc.cluster.local:4222"
```

#### Worker (rin-worker)

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: rin-worker
  namespace: rin-system
spec:
  replicas: 1                    # Single instance (NATS consumer groups handle dedup)
  template:
    spec:
      containers:
      - name: rin-worker
        image: ghcr.io/rin/server:latest
        command: ["/app/worker"]
        resources:
          requests:
            cpu: 250m
            memory: 256Mi
          limits:
            cpu: "1"
            memory: 512Mi
        env:
        - name: DATABASE_URL
          valueFrom:
            secretKeyRef:
              name: rin-db-credentials
              key: url
        - name: NATS_URL
          value: "nats://nats.rin-system.svc.cluster.local:4222"
```

#### Score Worker (rin-score-worker)

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: rin-score-worker
  namespace: rin-system
spec:
  replicas: 1
  template:
    spec:
      containers:
      - name: rin-score-worker
        image: ghcr.io/rin/server:latest
        command: ["/app/score-worker"]
        resources:
          requests:
            cpu: 500m
            memory: 512Mi
          limits:
            cpu: "2"
            memory: 2Gi       # Score computation is memory-intensive
```

#### NATS JetStream

```yaml
apiVersion: apps/v1
kind: StatefulSet
metadata:
  name: nats
  namespace: rin-system
spec:
  replicas: 3                   # Match cluster node count
  serviceName: nats
  template:
    spec:
      affinity:
        podAntiAffinity:
          requiredDuringSchedulingIgnoredDuringExecution:
          - topologyKey: kubernetes.io/hostname
      containers:
      - name: nats
        image: nats:2.10-alpine
        args:
        - "--config=/etc/nats/nats.conf"
        - "--name=$(POD_NAME)"
        ports:
        - containerPort: 4222
          name: client
        - containerPort: 6222
          name: cluster
        - containerPort: 8222
          name: monitor
        volumeMounts:
        - name: data
          mountPath: /data/jetstream
        - name: config
          mountPath: /etc/nats
        resources:
          requests:
            cpu: 100m
            memory: 128Mi
          limits:
            cpu: 500m
            memory: 512Mi
  volumeClaimTemplates:
  - metadata:
      name: data
    spec:
      accessModes: [ReadWriteOnce]
      storageClassName: local-path   # or longhorn
      resources:
        requests:
          storage: 10Gi
```

### 4.3 Services

```yaml
# API service (ClusterIP, exposed via Traefik Ingress)
apiVersion: v1
kind: Service
metadata:
  name: rin-api
  namespace: rin-system
spec:
  type: ClusterIP
  ports:
  - port: 8080
    targetPort: http
    name: http
  - port: 9090
    targetPort: metrics
    name: metrics
  selector:
    app: rin-api
---
# NATS headless service (for StatefulSet DNS)
apiVersion: v1
kind: Service
metadata:
  name: nats
  namespace: rin-system
spec:
  clusterIP: None
  ports:
  - port: 4222
    name: client
  - port: 6222
    name: cluster
  selector:
    app: nats
```

---

## 5) Networking

### 5.1 Ingress (Traefik)

K3s ships with Traefik as the default ingress controller. Use it for TLS termination and routing.

```yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: rin-api-ingress
  namespace: rin-system
  annotations:
    traefik.ingress.kubernetes.io/router.tls: "true"
    traefik.ingress.kubernetes.io/router.tls.certresolver: letsencrypt
    traefik.ingress.kubernetes.io/router.middlewares: rin-system-rate-limit@kubernetescrd
spec:
  tls:
  - hosts:
    - api.rin.example.com
    secretName: rin-api-tls
  rules:
  - host: api.rin.example.com
    http:
      paths:
      - path: /
        pathType: Prefix
        backend:
          service:
            name: rin-api
            port:
              number: 8080
---
# Grafana ingress (separate subdomain)
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: grafana-ingress
  namespace: rin-monitoring
  annotations:
    traefik.ingress.kubernetes.io/router.tls: "true"
spec:
  tls:
  - hosts:
    - monitor.rin.example.com
    secretName: grafana-tls
  rules:
  - host: monitor.rin.example.com
    http:
      paths:
      - path: /
        pathType: Prefix
        backend:
          service:
            name: grafana
            port:
              number: 3000
```

### 5.2 TLS Termination

Two options:

**Option A: Traefik + Let's Encrypt (recommended for internet-facing)**

Configure Traefik's built-in ACME resolver via K3s HelmChartConfig:

```yaml
apiVersion: helm.cattle.io/v1
kind: HelmChartConfig
metadata:
  name: traefik
  namespace: kube-system
spec:
  valuesContent: |-
    additionalArguments:
      - "--certificatesresolvers.letsencrypt.acme.email=ops@rin.example.com"
      - "--certificatesresolvers.letsencrypt.acme.storage=/data/acme.json"
      - "--certificatesresolvers.letsencrypt.acme.httpchallenge.entrypoint=web"
    persistence:
      enabled: true
      size: 128Mi
```

**Option B: cert-manager + internal CA (air-gapped or private networks)**

Deploy cert-manager and use a self-signed or internal CA:

```bash
kubectl apply -f https://github.com/cert-manager/cert-manager/releases/download/v1.14.0/cert-manager.yaml
```

### 5.3 Internal Service Communication

```
+----------+     ConnectRPC (HTTP/2)     +----------+
| iOS App  | --------------------------> | rin-api   |
+----------+     via Traefik Ingress     +----------+
                                              |
                            NATS protocol     |  SQL (port 5432)
                         +--------------------+--------------------+
                         |                                         |
                   +----------+                             +------------+
                   |   NATS   |                             | PostgreSQL |
                   +----------+                             +------------+
                         |
              +----------+----------+
              |                     |
        +----------+         +----------+
        | worker   |         | score    |
        +----------+         +----------+
```

All internal communication uses ClusterIP services. No pod-to-pod direct IP communication. DNS resolution via CoreDNS (included in K3s).

Service discovery pattern:
- `nats.rin-system.svc.cluster.local:4222` -- NATS
- `postgresql.rin-data.svc.cluster.local:5432` -- PostgreSQL
- `rin-api.rin-system.svc.cluster.local:8080` -- API (internal)
- `redis.rin-system.svc.cluster.local:6379` -- Redis (if used)

### 5.4 Network Policies

Restrict traffic to only necessary paths:

```yaml
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: rin-api-policy
  namespace: rin-system
spec:
  podSelector:
    matchLabels:
      app: rin-api
  policyTypes:
  - Ingress
  - Egress
  ingress:
  - from:
    - namespaceSelector:
        matchLabels:
          kubernetes.io/metadata.name: kube-system    # Traefik
    ports:
    - port: 8080
  - from:
    - namespaceSelector:
        matchLabels:
          kubernetes.io/metadata.name: rin-monitoring  # Prometheus scrape
    ports:
    - port: 9090
  egress:
  - to:
    - namespaceSelector:
        matchLabels:
          kubernetes.io/metadata.name: rin-system      # NATS, Redis
    - namespaceSelector:
        matchLabels:
          kubernetes.io/metadata.name: rin-data         # PostgreSQL
  - to:                                                 # DNS
    - namespaceSelector: {}
    ports:
    - port: 53
      protocol: UDP
    - port: 53
      protocol: TCP
```

Note: K3s uses Flannel CNI by default, which does not enforce NetworkPolicies. To enable enforcement, install Calico or Cilium as the CNI:

```bash
# Install K3s with Calico instead of Flannel
curl -sfL https://get.k3s.io | sh -s - server \
  --cluster-init \
  --flannel-backend=none \
  --disable-network-policy
# Then install Calico
kubectl apply -f https://raw.githubusercontent.com/projectcalico/calico/v3.27.0/manifests/calico.yaml
```

### 5.5 DNS Configuration

For on-prem deployments without Cloudflare:

1. Point `api.rin.example.com` to the load balancer / VIP in front of K3s nodes.
2. If no external load balancer, use MetalLB to assign a virtual IP:

```yaml
apiVersion: metallb.io/v1beta1
kind: IPAddressPool
metadata:
  name: rin-pool
  namespace: metallb-system
spec:
  addresses:
  - 192.168.1.240-192.168.1.250
---
apiVersion: metallb.io/v1beta1
kind: L2Advertisement
metadata:
  name: rin-l2
  namespace: metallb-system
```

---

## 6) Storage

### 6.1 Storage Classes

K3s includes `local-path-provisioner` by default. For production, choose based on requirements:

| Storage Class | Use Case | HA | Performance | Complexity |
|---------------|----------|-----|-------------|------------|
| **local-path** (default) | Dev, single-node | No replication | Best (local disk) | Zero |
| **Longhorn** | Production multi-node | Replicated across nodes | Good | Low-medium |
| **OpenEBS (Mayastor)** | High-performance production | Replicated, NVMe-optimized | Excellent | Medium |
| **NFS** | Shared storage (if available) | Depends on NFS server | Moderate | Low |

Recommendation: **Longhorn** for production on-prem. It is CNCF-graduated, lightweight, and provides cross-node replication with backup integration.

```bash
# Install Longhorn
kubectl apply -f https://raw.githubusercontent.com/longhorn/longhorn/v1.6.0/deploy/longhorn.yaml
```

### 6.2 Persistent Volume Layout

| Component | Volume Size | Storage Class | Access Mode | Backup |
|-----------|------------|---------------|-------------|--------|
| PostgreSQL data | 50Gi (start) | longhorn | ReadWriteOnce | pgBackRest + Longhorn snapshots |
| PostgreSQL WAL | 20Gi | longhorn | ReadWriteOnce | Continuous archival |
| NATS JetStream | 10Gi per node | longhorn | ReadWriteOnce | Stream replication handles HA |
| Redis (if used) | 2Gi | local-path | ReadWriteOnce | Not backed up (cache only) |
| Prometheus data | 20Gi | longhorn | ReadWriteOnce | Retention-based (15d default) |
| Grafana data | 1Gi | longhorn | ReadWriteOnce | Dashboard configs in git |

### 6.3 PostgreSQL Storage Configuration

```yaml
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: pg-data
  namespace: rin-data
spec:
  accessModes: [ReadWriteOnce]
  storageClassName: longhorn
  resources:
    requests:
      storage: 50Gi
---
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: pg-wal
  namespace: rin-data
spec:
  accessModes: [ReadWriteOnce]
  storageClassName: longhorn
  resources:
    requests:
      storage: 20Gi
```

Separate WAL from data for performance: WAL writes are sequential and benefit from dedicated I/O.

---

## 7) PostgreSQL Deployment

### 7.1 Option A: CloudNativePG Operator (Recommended)

CloudNativePG is the recommended PostgreSQL operator for Kubernetes. It handles replication, failover, backups, and monitoring with minimal configuration.

```bash
kubectl apply --server-side -f \
  https://raw.githubusercontent.com/cloudnative-pg/cloudnative-pg/release-1.22/releases/cnpg-1.22.0.yaml
```

Cluster definition:

```yaml
apiVersion: postgresql.cnpg.io/v1
kind: Cluster
metadata:
  name: rin-pg
  namespace: rin-data
spec:
  instances: 3                          # 1 primary + 2 replicas
  primaryUpdateStrategy: unsupervised   # Automatic failover

  postgresql:
    parameters:
      max_connections: "200"
      shared_buffers: "1GB"
      effective_cache_size: "3GB"
      work_mem: "16MB"
      maintenance_work_mem: "256MB"
      wal_level: "replica"
      max_wal_senders: "10"
      max_replication_slots: "10"
      hot_standby: "on"

  storage:
    size: 50Gi
    storageClass: longhorn

  walStorage:
    size: 20Gi
    storageClass: longhorn

  backup:
    barmanObjectStore:
      destinationPath: "s3://rin-backups/pg/"
      endpointURL: "https://s3.example.com"   # MinIO or S3-compatible
      s3Credentials:
        accessKeyId:
          name: backup-creds
          key: ACCESS_KEY_ID
        secretAccessKey:
          name: backup-creds
          key: ACCESS_SECRET_KEY
      wal:
        compression: gzip
      data:
        compression: gzip
    retentionPolicy: "30d"

  monitoring:
    enablePodMonitor: true               # For Prometheus scraping

  resources:
    requests:
      cpu: 500m
      memory: 1Gi
    limits:
      cpu: "2"
      memory: 4Gi

  affinity:
    topologyKey: kubernetes.io/hostname  # Spread replicas across nodes
```

### 7.2 Option B: Patroni (Manual Setup)

For operators who prefer Patroni over an operator-based approach:

```yaml
apiVersion: apps/v1
kind: StatefulSet
metadata:
  name: patroni
  namespace: rin-data
spec:
  replicas: 3
  serviceName: patroni
  template:
    spec:
      containers:
      - name: patroni
        image: registry.opensource.zalan.do/acid/spilo-16:3.2-p1
        env:
        - name: PATRONI_KUBERNETES_NAMESPACE
          valueFrom:
            fieldRef:
              fieldPath: metadata.namespace
        - name: PATRONI_KUBERNETES_USE_ENDPOINTS
          value: "true"
        - name: PATRONI_SUPERUSER_PASSWORD
          valueFrom:
            secretKeyRef:
              name: pg-credentials
              key: superuser-password
        ports:
        - containerPort: 5432
          name: postgresql
        - containerPort: 8008
          name: patroni
        volumeMounts:
        - name: pgdata
          mountPath: /home/postgres/pgdata
  volumeClaimTemplates:
  - metadata:
      name: pgdata
    spec:
      accessModes: [ReadWriteOnce]
      storageClassName: longhorn
      resources:
        requests:
          storage: 50Gi
```

Decision rationale: CloudNativePG is preferred because it is purpose-built for Kubernetes, handles PVC management, integrates with Prometheus via PodMonitor, and has built-in Barman backup support. Patroni is the fallback if the operator model is undesirable.

---

## 8) High Availability

### 8.1 K3s Control Plane HA

With 3 server nodes and embedded etcd:
- Quorum requires 2 of 3 nodes alive.
- API server runs on every server node -- any node can serve kubectl requests.
- Traefik runs as a DaemonSet on all server nodes -- any node can handle ingress.
- etcd snapshots are taken automatically every 12 hours (configurable via `--etcd-snapshot-schedule-cron`).

Failure scenarios:

| Failure | Impact | Recovery |
|---------|--------|----------|
| 1 node down | No user impact. Pods reschedule. PG failover to replica. | Auto-recovery when node returns. |
| 2 nodes down | etcd loses quorum. Cluster read-only. | Restore from etcd snapshot or rejoin nodes. |
| All nodes down | Full outage. | Restore from backup. See Section 9. |
| Network partition (1 vs 2) | Minority side loses etcd quorum. Majority continues. | Heals on reconnection. |

### 8.2 PostgreSQL HA (via CloudNativePG)

- Synchronous replication with automatic failover.
- Failover time: 5-30 seconds (depends on detection interval).
- Read replicas can serve read-only queries to reduce primary load.
- WAL archiving provides point-in-time recovery.

Application connection strategy:

```yaml
# Primary (read-write)
DATABASE_URL: "postgresql://rin:password@rin-pg-rw.rin-data.svc.cluster.local:5432/rin"

# Read replicas (read-only queries)
DATABASE_URL_RO: "postgresql://rin:password@rin-pg-ro.rin-data.svc.cluster.local:5432/rin"
```

CloudNativePG creates `-rw` (primary) and `-ro` (replicas) services automatically.

### 8.3 NATS JetStream HA

With 3 NATS nodes and `replicas: 3` on streams:
- Any single NATS node can fail without message loss.
- Clients auto-reconnect to surviving nodes.
- JetStream stream data replicated across all 3 nodes.

```
# nats.conf (key settings)
jetstream {
  store_dir: /data/jetstream
  max_mem: 256MB
  max_file: 10GB
}
cluster {
  name: rin-nats
  routes: [
    nats-route://nats-0.nats.rin-system.svc.cluster.local:6222
    nats-route://nats-1.nats.rin-system.svc.cluster.local:6222
    nats-route://nats-2.nats.rin-system.svc.cluster.local:6222
  ]
}
```

### 8.4 Application HA

The Go monolith (rin-api) runs 2+ replicas with pod anti-affinity:
- Rolling updates with zero downtime (`maxUnavailable: 1`).
- Health checks ensure traffic routes only to healthy pods.
- NATS consumer groups ensure workers process each event exactly once across replicas.

---

## 9) Backup and Recovery

### 9.1 Backup Strategy Overview

```
+-------------------+     +---------------------+     +------------------+
| PostgreSQL        |     | Object Store        |     | Off-site         |
| (CloudNativePG)   | --> | (MinIO / S3)        | --> | (rsync / rclone) |
|                   |     |                     |     |                  |
| - WAL archiving   |     | - WAL segments      |     | - Daily sync     |
| - Base backups    |     | - Base backups      |     | - Encrypted      |
| - 30d retention   |     | - etcd snapshots    |     | - Remote site    |
+-------------------+     +---------------------+     +------------------+
```

### 9.2 PostgreSQL Backups

**With CloudNativePG (automated):**

CloudNativePG handles backups via Barman. Configure in the Cluster spec (shown in Section 7.1).

Schedule regular base backups:

```yaml
apiVersion: postgresql.cnpg.io/v1
kind: ScheduledBackup
metadata:
  name: rin-pg-daily
  namespace: rin-data
spec:
  schedule: "0 2 * * *"          # Daily at 02:00
  backupOwnerReference: self
  cluster:
    name: rin-pg
  method: barmanObjectStore
```

**Without operator (pgBackRest):**

```yaml
apiVersion: batch/v1
kind: CronJob
metadata:
  name: pg-backup
  namespace: rin-data
spec:
  schedule: "0 2 * * *"
  jobTemplate:
    spec:
      template:
        spec:
          containers:
          - name: pgbackrest
            image: pgbackrest/pgbackrest:latest
            command:
            - pgbackrest
            - --stanza=rin
            - --type=full
            - backup
            env:
            - name: PGBACKREST_REPO1_S3_ENDPOINT
              value: "s3.example.com"
            - name: PGBACKREST_REPO1_S3_BUCKET
              value: "rin-backups"
          restartPolicy: OnFailure
```

### 9.3 K3s etcd Snapshots

K3s automatically snapshots etcd. Configure retention:

```bash
# In /etc/rancher/k3s/config.yaml on each server node
etcd-snapshot-schedule-cron: "0 */6 * * *"   # Every 6 hours
etcd-snapshot-retention: 10                   # Keep 10 snapshots
etcd-snapshot-dir: /var/lib/rancher/k3s/server/db/snapshots
```

Copy snapshots off-node:

```yaml
apiVersion: batch/v1
kind: CronJob
metadata:
  name: etcd-snapshot-sync
  namespace: kube-system
spec:
  schedule: "30 */6 * * *"       # 30 minutes after snapshot
  jobTemplate:
    spec:
      template:
        spec:
          hostNetwork: true
          containers:
          - name: rclone
            image: rclone/rclone:latest
            command:
            - rclone
            - sync
            - /snapshots/
            - s3:rin-backups/etcd/
            volumeMounts:
            - name: snapshots
              mountPath: /snapshots
              readOnly: true
          volumes:
          - name: snapshots
            hostPath:
              path: /var/lib/rancher/k3s/server/db/snapshots
          restartPolicy: OnFailure
```

### 9.4 Off-Site Backup

For disaster recovery, sync backups to a remote location:

```bash
# Daily off-site sync via rclone (run as CronJob or external cron)
rclone sync \
  s3:rin-backups/ \
  offsite:rin-dr-backups/ \
  --transfers=4 \
  --checkers=8 \
  --s3-upload-concurrency=4
```

Off-site target options:
- Another physical location with MinIO.
- Cloud object storage (Hetzner, Backblaze B2, Wasabi).
- Encrypted USB drives rotated off-site (small deployments).

### 9.5 Recovery Procedures

**PostgreSQL full restore:**

```bash
# With CloudNativePG -- create a new cluster from backup
kubectl apply -f - <<EOF
apiVersion: postgresql.cnpg.io/v1
kind: Cluster
metadata:
  name: rin-pg-restored
  namespace: rin-data
spec:
  instances: 3
  bootstrap:
    recovery:
      source: rin-pg-backup
      recoveryTarget:
        targetTime: "2026-02-14T12:00:00Z"    # Point-in-time
  externalClusters:
  - name: rin-pg-backup
    barmanObjectStore:
      destinationPath: "s3://rin-backups/pg/"
      endpointURL: "https://s3.example.com"
      s3Credentials:
        accessKeyId:
          name: backup-creds
          key: ACCESS_KEY_ID
        secretAccessKey:
          name: backup-creds
          key: ACCESS_SECRET_KEY
EOF
```

**K3s cluster restore from etcd snapshot:**

```bash
# On a fresh node
k3s server \
  --cluster-reset \
  --cluster-reset-restore-path=/path/to/snapshot-file
```

**Full disaster recovery procedure:**

1. Provision new nodes (bare metal or VM).
2. Install K3s on first node, restore from etcd snapshot.
3. Join remaining nodes.
4. Restore PostgreSQL from object store backup (CloudNativePG recovery bootstrap).
5. NATS JetStream recovers from replicated stream data (or replay from PostgreSQL outbox if streams lost).
6. Verify application health.
7. Update DNS to point to new cluster.

Estimated RTO: 1-2 hours (depending on data volume and network speed).

---

## 10) Monitoring

### 10.1 Stack Selection

Two options based on resource constraints:

| Stack | RAM Overhead | Disk | Best For |
|-------|-------------|------|----------|
| **Prometheus + Grafana** | ~500MB-1GB | 20Gi | Standard K8s monitoring, wide ecosystem |
| **VictoriaMetrics + Grafana** | ~200-400MB | 15Gi | Resource-constrained nodes, long retention |

Recommendation: Start with **VictoriaMetrics** (single-node mode) for lower resource usage. Switch to Prometheus if you need the broader ecosystem.

### 10.2 Deployment

```bash
# Option A: kube-prometheus-stack (Prometheus + Grafana + Alertmanager)
helm repo add prometheus-community https://prometheus-community.github.io/helm-charts
helm install monitoring prometheus-community/kube-prometheus-stack \
  --namespace rin-monitoring --create-namespace \
  --set prometheus.prometheusSpec.retention=15d \
  --set prometheus.prometheusSpec.resources.requests.memory=256Mi \
  --set prometheus.prometheusSpec.resources.limits.memory=512Mi \
  --set grafana.resources.requests.memory=128Mi \
  --set grafana.resources.limits.memory=256Mi

# Option B: VictoriaMetrics + Grafana
helm repo add vm https://victoriametrics.github.io/helm-charts/
helm install vm vm/victoria-metrics-single \
  --namespace rin-monitoring --create-namespace \
  --set server.resources.requests.memory=128Mi \
  --set server.resources.limits.memory=256Mi
```

### 10.3 Application Metrics

The Go monolith exposes Prometheus-format metrics on `:9090/metrics`. Key metrics to track:

| Metric | Type | Alert Threshold |
|--------|------|-----------------|
| `rin_api_request_duration_seconds` | Histogram | p95 > 500ms |
| `rin_api_request_total` | Counter | Error rate > 5% |
| `rin_db_pool_active_connections` | Gauge | > 80% of pool |
| `rin_db_query_duration_seconds` | Histogram | p95 > 200ms |
| `rin_nats_consumer_lag` | Gauge | > 1000 messages |
| `rin_worker_batch_duration_seconds` | Histogram | > 30 minutes (score) |
| `rin_outbox_pending_events` | Gauge | > 500 for > 5 minutes |

### 10.4 Alerting

```yaml
apiVersion: monitoring.coreos.com/v1
kind: PrometheusRule
metadata:
  name: rin-alerts
  namespace: rin-monitoring
spec:
  groups:
  - name: rin.rules
    rules:
    - alert: RinAPIHighLatency
      expr: histogram_quantile(0.95, rate(rin_api_request_duration_seconds_bucket[5m])) > 0.5
      for: 5m
      labels:
        severity: warning
      annotations:
        summary: "API p95 latency > 500ms"

    - alert: RinAPIHighErrorRate
      expr: rate(rin_api_request_total{code=~"5.."}[5m]) / rate(rin_api_request_total[5m]) > 0.05
      for: 5m
      labels:
        severity: critical
      annotations:
        summary: "API error rate > 5%"

    - alert: RinPostgresDown
      expr: cnpg_collector_up == 0
      for: 1m
      labels:
        severity: critical
      annotations:
        summary: "PostgreSQL cluster unreachable"

    - alert: RinNATSConsumerLag
      expr: rin_nats_consumer_lag > 1000
      for: 10m
      labels:
        severity: warning
      annotations:
        summary: "NATS consumer lag > 1000 messages"

    - alert: RinNodeDiskPressure
      expr: (node_filesystem_avail_bytes{mountpoint="/"} / node_filesystem_size_bytes{mountpoint="/"}) < 0.15
      for: 5m
      labels:
        severity: warning
      annotations:
        summary: "Node disk usage > 85%"
```

### 10.5 Dashboards

Pre-built Grafana dashboards to import:
- K3s cluster overview (node CPU, memory, disk, network).
- PostgreSQL (via CloudNativePG dashboard or pgMonitor).
- NATS JetStream (streams, consumers, lag).
- Rin application (request rate, latency, errors, outbox depth).

---

## 11) Security

### 11.1 Pod Security Standards

Enforce restricted Pod Security Standards at the namespace level:

```yaml
apiVersion: v1
kind: Namespace
metadata:
  name: rin-system
  labels:
    pod-security.kubernetes.io/enforce: restricted
    pod-security.kubernetes.io/audit: restricted
    pod-security.kubernetes.io/warn: restricted
```

This enforces:
- Non-root containers.
- Read-only root filesystem.
- No privilege escalation.
- Dropped capabilities.

Application pods must comply:

```yaml
securityContext:
  runAsNonRoot: true
  runAsUser: 1000
  runAsGroup: 1000
  fsGroup: 1000
  seccompProfile:
    type: RuntimeDefault
containers:
- name: rin-api
  securityContext:
    allowPrivilegeEscalation: false
    readOnlyRootFilesystem: true
    capabilities:
      drop: [ALL]
```

### 11.2 Secrets Management

**Option A: SOPS + age (consistent with cloud stack)**

Use the same SOPS/age workflow from `SECRETS_CONFIG_MANAGEMENT_V1.md`. Decrypt at deploy time and create Kubernetes secrets:

```bash
sops -d infra/environments/onprem/secrets.enc.yaml | \
  kubectl apply -f -
```

**Option B: Sealed Secrets (Kubernetes-native)**

For operators who prefer GitOps-native secret management:

```bash
# Install Sealed Secrets controller
helm repo add sealed-secrets https://bitnami-labs.github.io/sealed-secrets
helm install sealed-secrets sealed-secrets/sealed-secrets \
  --namespace kube-system

# Encrypt a secret
kubeseal --format yaml < secret.yaml > sealed-secret.yaml
# sealed-secret.yaml is safe to commit to git
kubectl apply -f sealed-secret.yaml
```

**Option C: External Secrets Operator (hybrid with cloud secret store)**

If using a cloud secret manager (Vault, AWS Secrets Manager) alongside on-prem:

```yaml
apiVersion: external-secrets.io/v1beta1
kind: ExternalSecret
metadata:
  name: rin-db-credentials
  namespace: rin-data
spec:
  refreshInterval: 1h
  secretStoreRef:
    name: vault-backend
    kind: ClusterSecretStore
  target:
    name: rin-db-credentials
  data:
  - secretKey: url
    remoteRef:
      key: rin/database
      property: connection_string
```

Decision: Use **SOPS + age** for consistency with the existing secret management strategy. Sealed Secrets is the recommended alternative if full GitOps workflow is desired.

### 11.3 TLS Everywhere

| Connection | TLS | Method |
|------------|-----|--------|
| Client -> Traefik | Yes | Let's Encrypt or internal CA |
| Traefik -> rin-api | Yes (optional) | In-cluster TLS or mTLS via service mesh |
| rin-api -> PostgreSQL | Yes | `sslmode=verify-full` in connection string |
| rin-api -> NATS | Yes | NATS TLS configuration |
| NATS cluster routes | Yes | Mutual TLS between NATS nodes |
| Prometheus -> targets | No (internal) | Cluster network only, no external exposure |

For internal mTLS without a service mesh, use cert-manager to issue per-service certificates:

```yaml
apiVersion: cert-manager.io/v1
kind: Certificate
metadata:
  name: rin-api-internal-tls
  namespace: rin-system
spec:
  secretName: rin-api-internal-tls
  issuerRef:
    name: internal-ca
    kind: ClusterIssuer
  dnsNames:
  - rin-api.rin-system.svc.cluster.local
```

### 11.4 Host-Level Security

Hardening checklist for each K3s node:
- SSH key-only authentication (no password login).
- Firewall: allow only K3s ports (6443, 10250), Traefik ports (80, 443), and inter-node traffic.
- Automatic security updates enabled (unattended-upgrades on Debian/Ubuntu, dnf-automatic on RHEL).
- CIS benchmark scan (use kube-bench: `docker run --rm aquasec/kube-bench`).
- Disable swap (K3s requirement and security best practice).
- AppArmor or SELinux enforcing mode.

---

## 12) Migration Paths

### 12.1 Hetzner Cloud -> On-Prem K3s

**Prerequisites:**
- On-prem K3s cluster provisioned and healthy.
- DNS TTL lowered to 60 seconds (24 hours before migration).
- Backup verification completed.

**Procedure:**

```
Phase 1: Parallel Deployment (Day 1)
├── Deploy application containers to K3s cluster.
├── Configure K3s services to point to existing cloud PostgreSQL.
├── Verify API functionality via direct K3s endpoint.
└── Duration: 2-4 hours.

Phase 2: Data Migration (Day 1-2)
├── If moving to self-managed PG:
│   ├── Set up CloudNativePG cluster on K3s.
│   ├── pg_basebackup from cloud PG to on-prem primary.
│   ├── Enable streaming replication from cloud -> on-prem.
│   ├── Verify replication lag < 1 second.
│   └── Duration: 2-8 hours (depending on data size).
├── If keeping managed PG (hybrid):
│   └── Skip this phase.
└── Migrate object storage (rclone sync).

Phase 3: Traffic Cutover (Day 2)
├── Set on-prem PG as primary (promote replica).
├── Update application config to use on-prem PG.
├── Update DNS to point to on-prem K3s.
├── Monitor for 2 hours.
└── Duration: 30 minutes.

Phase 4: Cleanup (Day 3-7)
├── Keep cloud environment running for 7 days (rollback window).
├── Monitor on-prem for stability.
├── Decommission cloud resources after confidence period.
└── Duration: 7 days.
```

**Rollback at any phase:**
- Phase 1-2: Stop K3s services, no user impact.
- Phase 3: Revert DNS to cloud endpoint (propagation: 1-5 minutes with low TTL).
- Phase 4: Re-enable cloud services, restore from cloud backup if needed.

### 12.2 On-Prem K3s -> Full Kubernetes (K8s)

K3s is CNCF-certified Kubernetes. Migration to full K8s is a cluster swap, not an application change.

**What changes:**

| Component | K3s | Full K8s | Migration effort |
|-----------|-----|----------|-----------------|
| Control plane | Embedded etcd, single binary | External etcd, multiple components | Cluster rebuild |
| CNI | Flannel (default) | Calico, Cilium, or any | Re-apply network policies |
| Ingress | Traefik (bundled) | Any (NGINX, Traefik, Istio) | Re-apply ingress configs |
| Storage | local-path / Longhorn | Any CSI driver | Re-create PVCs |
| Manifests | Standard K8s YAML | Standard K8s YAML | **No change** |

**Procedure:**
1. Provision full K8s cluster (kubeadm, RKE2, or managed K8s).
2. Install same addons (Longhorn/storage, CNI, cert-manager).
3. Apply identical manifests (namespaces, deployments, services, ingress).
4. Migrate data (PostgreSQL replication, NATS stream sync).
5. Cut over DNS.
6. Decommission K3s cluster.

Estimated effort: 1-2 days. No application code changes required.

### 12.3 K3s -> Managed Kubernetes

If moving to a managed K8s service (EKS, GKE, AKS, Hetzner K8s):

1. All application manifests apply unchanged.
2. Replace Longhorn with cloud-native storage class (EBS, Persistent Disk).
3. Replace CloudNativePG with managed database (RDS, Cloud SQL) if desired.
4. Replace MetalLB with cloud load balancer.
5. DNS update.

---

## 13) Resource Requirements

### 13.1 Minimum Hardware (Per Node)

| Tier | CPU | RAM | Storage | Nodes | Est. Monthly Cost* |
|------|-----|-----|---------|-------|-------------------|
| **Dev/Test** | 2 cores | 4 GB | 100 GB SSD | 1 | N/A (existing hardware) |
| **Minimum Production** | 4 cores | 8 GB | 200 GB SSD | 2 | ~$60-120 (colo) |
| **Recommended Production** | 4 cores | 16 GB | 500 GB NVMe | 3 | ~$150-300 (colo) |
| **Growth** (Stage B) | 8 cores | 32 GB | 1 TB NVMe | 3-5 | ~$300-600 (colo) |

*Colocation costs vary by provider and location. Dedicated server costs (Hetzner AX-series) run EUR 40-80/mo per node.

### 13.2 Resource Budget (3-Node Recommended Cluster)

```
Per Node: 4 CPU cores, 16 GB RAM, 500 GB NVMe

K3s overhead:          0.5 CPU,  512 MB RAM
Traefik:               0.1 CPU,  128 MB RAM
CoreDNS:               0.1 CPU,   64 MB RAM
Longhorn:              0.2 CPU,  256 MB RAM
                       -----------------------
System total:          0.9 CPU,  960 MB RAM

Available for workloads per node:
                       3.1 CPU, ~15 GB RAM

Workload distribution (across 3 nodes):

Node 1:
  rin-api (replica 1):   0.25-2.0 CPU,  256 MB-1 GB RAM
  rin-worker:            0.25-1.0 CPU,  256-512 MB RAM
  PostgreSQL primary:    0.5-2.0 CPU,   1-4 GB RAM
  NATS node 0:           0.1-0.5 CPU,   128-512 MB RAM

Node 2:
  rin-api (replica 2):   0.25-2.0 CPU,  256 MB-1 GB RAM
  rin-score-worker:      0.5-2.0 CPU,   512 MB-2 GB RAM
  PostgreSQL replica:    0.5-2.0 CPU,   1-4 GB RAM
  NATS node 1:           0.1-0.5 CPU,   128-512 MB RAM

Node 3:
  PostgreSQL replica:    0.5-2.0 CPU,   1-4 GB RAM
  NATS node 2:           0.1-0.5 CPU,   128-512 MB RAM
  Prometheus/VM:         0.2-0.5 CPU,   256-512 MB RAM
  Grafana:               0.1-0.2 CPU,   128-256 MB RAM
  Redis (optional):      0.1-0.5 CPU,   128-512 MB RAM
```

### 13.3 Storage Capacity Planning

| Data Type | Growth Rate (est.) | 1,000 Users | 10,000 Users |
|-----------|-------------------|-------------|--------------|
| PostgreSQL (OLTP) | ~1 GB/1K users | 1-2 GB | 10-20 GB |
| PostgreSQL WAL | 2-5x write amplification | 2-5 GB | 10-25 GB |
| NATS JetStream | ~100 MB/1K users | 100 MB | 1 GB |
| Backups (30d) | 3-5x primary data | 5-10 GB | 30-100 GB |
| Monitoring (15d) | ~50 MB/day | 750 MB | 2-5 GB |

Start with 500 GB NVMe per node. Monitor usage monthly and expand before 70% utilization.

---

## 14) Docker Compose Fallback (Development/Testing)

For local development, CI environments, or single-node testing, use Docker Compose instead of K3s.

```yaml
# docker-compose.yml
version: "3.9"

services:
  api:
    image: ghcr.io/rin/server:latest
    command: ["/app/api"]
    ports:
      - "8080:8080"
      - "9090:9090"
    environment:
      DATABASE_URL: "postgresql://rin:rin_dev@postgres:5432/rin?sslmode=disable"
      NATS_URL: "nats://nats:4222"
      ENVIRONMENT: development
      LOG_LEVEL: debug
    depends_on:
      postgres:
        condition: service_healthy
      nats:
        condition: service_started
    restart: unless-stopped

  worker:
    image: ghcr.io/rin/server:latest
    command: ["/app/worker"]
    environment:
      DATABASE_URL: "postgresql://rin:rin_dev@postgres:5432/rin?sslmode=disable"
      NATS_URL: "nats://nats:4222"
      ENVIRONMENT: development
    depends_on:
      postgres:
        condition: service_healthy
      nats:
        condition: service_started
    restart: unless-stopped

  score-worker:
    image: ghcr.io/rin/server:latest
    command: ["/app/score-worker"]
    environment:
      DATABASE_URL: "postgresql://rin:rin_dev@postgres:5432/rin?sslmode=disable"
      NATS_URL: "nats://nats:4222"
      ENVIRONMENT: development
    depends_on:
      postgres:
        condition: service_healthy
      nats:
        condition: service_started
    restart: unless-stopped

  postgres:
    image: postgres:16-alpine
    environment:
      POSTGRES_USER: rin
      POSTGRES_PASSWORD: rin_dev
      POSTGRES_DB: rin
    ports:
      - "5432:5432"
    volumes:
      - pg_data:/var/lib/postgresql/data
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U rin"]
      interval: 5s
      timeout: 5s
      retries: 5
    restart: unless-stopped

  nats:
    image: nats:2.10-alpine
    command: ["--jetstream", "--store_dir=/data"]
    ports:
      - "4222:4222"
      - "8222:8222"
    volumes:
      - nats_data:/data
    restart: unless-stopped

  # Optional: Redis for caching
  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data
    restart: unless-stopped

volumes:
  pg_data:
  nats_data:
  redis_data:
```

Usage:

```bash
# Start all services
docker compose up -d

# View logs
docker compose logs -f api

# Run database migrations
docker compose exec api /app/api migrate up

# Stop
docker compose down

# Stop and delete all data
docker compose down -v
```

Limitations of Docker Compose deployment:
- No HA (single node, single process per service).
- No automatic restarts on node reboot (requires systemd unit or similar).
- No rolling updates (downtime during container replacement).
- No built-in TLS (use a reverse proxy like Caddy or nginx in front).
- Not suitable for production workloads.

---

## 15) Deployment Checklist

### 15.1 Pre-Deployment

```
[ ] Hardware provisioned and OS installed (Ubuntu 22.04+ or Debian 12+)
[ ] Static IPs assigned to all nodes
[ ] SSH key-only access configured
[ ] Firewall rules applied (Section 11.4)
[ ] DNS records created (api.rin.example.com -> LB/VIP)
[ ] DNS TTL set to 60s during deployment
[ ] Object storage for backups provisioned (MinIO or S3-compatible)
[ ] SOPS age keys generated for on-prem environment
[ ] Secrets encrypted in infra/environments/onprem/secrets.enc.yaml
```

### 15.2 Cluster Setup

```
[ ] K3s installed on first server node (--cluster-init)
[ ] Remaining server nodes joined
[ ] kubectl access verified from operator machine
[ ] CNI with NetworkPolicy support installed (Calico/Cilium) if needed
[ ] Longhorn storage installed and verified
[ ] MetalLB installed (if no external LB)
[ ] cert-manager installed (if using internal CA)
```

### 15.3 Application Deployment

```
[ ] Namespaces created (rin-system, rin-data, rin-monitoring)
[ ] Pod Security Standards labels applied
[ ] Secrets created from SOPS-encrypted files
[ ] CloudNativePG operator installed
[ ] PostgreSQL cluster deployed and healthy
[ ] Database migrations run
[ ] NATS JetStream StatefulSet deployed
[ ] rin-api Deployment created (2+ replicas)
[ ] rin-worker Deployment created
[ ] rin-score-worker Deployment created
[ ] Ingress configured with TLS
[ ] Health checks passing on all pods
```

### 15.4 Post-Deployment

```
[ ] Monitoring stack deployed (Prometheus/VM + Grafana)
[ ] Alert rules configured and tested
[ ] Backup CronJobs running (PostgreSQL + etcd)
[ ] Backup restore tested successfully
[ ] Load test passed (simulate expected traffic)
[ ] DNS updated to production records
[ ] DNS TTL restored to normal (300-3600s)
[ ] Runbook updated with on-prem-specific procedures
```

---

## 16) Open Decisions

1. Whether to use CloudNativePG or Patroni for PostgreSQL HA (this doc recommends CloudNativePG).
2. Whether to deploy MinIO on-cluster for backup object storage or use an external S3-compatible service.
3. Whether to install a service mesh (Linkerd) for mTLS between services or use cert-manager-issued certificates.
4. Whether to use Flannel (default, simpler) or Calico/Cilium (NetworkPolicy enforcement) as CNI.
5. Whether the on-prem deployment should support Cloudflare Tunnel for edge termination without public IP exposure.
6. Whether to include Spark infrastructure on the K3s cluster for graph compute or offload to a separate batch processing system.

---

## 17) Appendix: Quick Reference Commands

```bash
# K3s cluster status
kubectl get nodes -o wide
kubectl top nodes

# Application status
kubectl -n rin-system get pods
kubectl -n rin-data get pods

# PostgreSQL status (CloudNativePG)
kubectl -n rin-data get cluster rin-pg
kubectl -n rin-data cnpg status rin-pg

# NATS status
kubectl -n rin-system exec -it nats-0 -- nats server report jetstream

# View logs
kubectl -n rin-system logs -f deployment/rin-api
kubectl -n rin-system logs -f deployment/rin-worker

# Manual backup trigger
kubectl -n rin-data create -f - <<EOF
apiVersion: postgresql.cnpg.io/v1
kind: Backup
metadata:
  name: manual-backup-$(date +%Y%m%d%H%M)
spec:
  method: barmanObjectStore
  cluster:
    name: rin-pg
EOF

# K3s etcd snapshot (manual)
k3s etcd-snapshot save --name manual-snapshot

# Scale API replicas
kubectl -n rin-system scale deployment/rin-api --replicas=3

# Rolling restart (zero-downtime)
kubectl -n rin-system rollout restart deployment/rin-api
kubectl -n rin-system rollout status deployment/rin-api
```
