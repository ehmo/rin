# Secrets, Config, and Key Management V1

## 1) Purpose

Define the secret lifecycle, environment config separation, and key management model for v1 operations.

Companion docs:
- `docs/plan/outlines/03_DEPLOYMENT_TOPOLOGY_OUTLINE_V1.md` (§7 secrets baseline)
- `docs/operations/SYSTEM_RUNBOOK_V1.md` (operational procedures)
- `docs/architecture/MONOREPO_CONVENTIONS_V1.md` (repo structure)

---

## 2) Secret Management: SOPS + Age

### 2.1 Model

Secrets are encrypted in the repository using [SOPS](https://github.com/getsops/sops) with [age](https://github.com/FiloSottile/age) encryption.

- Secrets are version-controlled alongside code.
- Encrypted at rest in git. Decrypted only at deploy time or in authorized operator sessions.
- No external secret store infrastructure required for v1.

### 2.2 File Structure

```
infra/
├── environments/
│   ├── dev/
│   │   ├── config.yaml            # Non-secret config (plain text)
│   │   └── secrets.enc.yaml       # SOPS-encrypted secrets
│   ├── staging/
│   │   ├── config.yaml
│   │   └── secrets.enc.yaml
│   └── prod/
│       ├── config.yaml
│       └── secrets.enc.yaml
├── keys/
│   └── .sops.yaml                 # SOPS config (age public keys per environment)
```

### 2.3 Encryption Rules

- `.sops.yaml` defines which keys encrypt which files (per-environment age public keys).
- Production secrets are encrypted with a production-only key that dev/staging keys cannot decrypt.
- Each environment has its own age key pair.

### 2.4 Key Storage

| Key | Location | Access |
|-----|----------|--------|
| Dev age private key | Developer machine (~/.config/sops/age/keys.txt) | Individual developer |
| Staging age private key | CI/CD secret | CI pipeline only |
| Prod age private key | Operator machine (founder) | Founder only |

---

## 3) Secret Categories

### 3.1 Database Credentials

| Secret | Environments | Rotation |
|--------|-------------|----------|
| PostgreSQL connection string | All | 90 days or on compromise |
| PostgreSQL superuser password | Prod only | 180 days |
| Read replica credentials | Staging, Prod | 90 days |

### 3.2 API Keys and Service Credentials

| Secret | Purpose | Rotation |
|--------|---------|----------|
| NATS JetStream credentials | Event transport auth | 90 days |
| OTP provider API key (Twilio/similar) | Phone verification | On compromise |
| Sentry DSN | Crash reporting | Static (non-sensitive) |
| App Store Connect API key | Build submission | Annual |
| Apple push notification key (APNs) | Push notifications | Annual |

### 3.3 Application Secrets

| Secret | Purpose | Rotation |
|--------|---------|----------|
| JWT signing key | API auth tokens | 90 days (overlap period) |
| Session encryption key | Cookie/session encryption | 90 days |
| SOPS age private keys | Secret decryption | On compromise or personnel change |

### 3.4 iOS App Secrets

| Secret | Storage | Notes |
|--------|---------|-------|
| API base URL | Config.yaml (not secret) | Per-environment |
| API client ID | Config.yaml (not secret) | Per-environment |
| Sentry DSN | Config.yaml (not secret) | Non-sensitive |
| StoreKit configuration | Xcode project | Apple-managed |

Note: iOS apps should contain **no secrets** in the binary. All sensitive operations happen server-side. The API client authenticates via tokens obtained through OTP verification.

---

## 4) Environment Config Separation

### 4.1 Config Layering

```
Base config (shared defaults)
    ↓ override
Environment config (dev/staging/prod)
    ↓ override
Runtime config (environment variables at deploy)
```

### 4.2 Config File Format

```yaml
# infra/environments/prod/config.yaml
app:
  environment: production
  log_level: info
  api_base_url: https://api.rin.com

database:
  host: db.rin.internal
  port: 5432
  name: rin_prod
  pool_size: 20
  ssl_mode: verify-full

nats:
  url: nats://nats.rin.internal:4222
  stream_replicas: 3

rate_limits:
  otp_per_phone_per_hour: 5
  shadow_creation_per_day: 3
  outbound_messages_per_hour: 50
```

### 4.3 What Goes Where

| Data | Config file (plain) | Secrets file (encrypted) | Environment variable |
|------|--------------------|-----------------------|---------------------|
| Database host/port | Yes | | |
| Database password | | Yes | |
| API base URL | Yes | | |
| JWT signing key | | Yes | |
| Log level | Yes | | Override at runtime |
| Feature flags | Yes | | Override at runtime |
| Rate limit values | Yes | | |

---

## 5) Secret Lifecycle

### 5.1 Creation

1. Generate secret value (use `openssl rand -base64 32` or equivalent).
2. Add to the appropriate `secrets.enc.yaml` using `sops`.
3. Commit encrypted file to git.
4. Deploy picks up new secret on next release.

### 5.2 Rotation

Rotation procedure:
1. Generate new secret value.
2. Update `secrets.enc.yaml` with new value.
3. For keys with overlap period (JWT signing):
   - Deploy new key as secondary/verification key first.
   - Wait for all active tokens to expire.
   - Promote new key to primary.
   - Remove old key.
4. Commit and deploy.
5. Verify service health after rotation.

### 5.3 Revocation

On compromise:
1. Generate replacement immediately.
2. Deploy emergency rotation.
3. Audit access logs for compromised period.
4. Rotate the age key if the SOPS key itself was compromised.
5. Re-encrypt all secrets with new age key.

### 5.4 Rotation Schedule

| Cadence | Secrets |
|---------|---------|
| **90 days** | Database credentials, JWT signing key, session key, NATS credentials |
| **180 days** | Database superuser |
| **Annual** | App Store Connect key, APNs key |
| **On compromise** | Any compromised secret + associated age key |
| **On personnel change** | All secrets accessible to departing personnel |

---

## 6) CI/CD Integration

### 6.1 Pipeline Access

- CI pipeline has access to **staging** age private key only.
- Production deploys require manual trigger by founder with production key.
- CI never has access to production secrets.

### 6.2 Deploy Flow

```
1. CI builds application binary.
2. CI decrypts staging secrets → runs integration tests.
3. On success: artifact promoted to production.
4. Founder triggers production deploy.
5. Deploy process decrypts prod secrets → injects as env vars → starts services.
```

### 6.3 Secret Injection

At deploy time, SOPS decrypts secrets and injects them as environment variables:

```bash
export $(sops -d infra/environments/prod/secrets.enc.yaml | yq -r 'to_entries | .[] | "\(.key)=\(.value)"')
```

Application reads secrets from environment variables, never from files on disk in production.

---

## 7) Never Rules

1. **Never** commit plaintext secrets to git.
2. **Never** share production secrets with dev/staging environments.
3. **Never** store secrets in iOS app binary or Info.plist.
4. **Never** log secret values (mask in structured logging).
5. **Never** send secrets over unencrypted channels.
6. **Never** use the same secret value across environments.
7. **Never** skip rotation after personnel changes.

---

## 8) Scaling Path

When SOPS + age becomes insufficient (team growth, compliance requirements):

| Trigger | Migration |
|---------|-----------|
| Team > 5 engineers | Evaluate HashiCorp Vault or cloud secret manager |
| SOC 2 / compliance audit | Add audit trail (Vault or cloud-native) |
| Dynamic secrets needed | Vault with database credential generation |
| Multi-region deployment | Cloud provider secret manager per region |

SOPS migration path: export secrets → import to Vault/cloud manager → update deploy pipeline → remove encrypted files from git.

---

## 9) Open Decisions

1. Exact age key distribution method for new team members (secure channel, in-person, key ceremony).
2. Whether to implement automated rotation reminders or rely on calendar-based manual process.
3. Whether CI should have read-only access to production secrets for smoke tests (adds risk).
4. Backup strategy for age private keys (paper key, hardware security module, or trusted second copy).
