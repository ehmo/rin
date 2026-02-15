# iOS Navigation and State Management V1

## 1) Purpose

Define the navigation model, deep linking architecture, and state management approach for the iOS app.

Companion docs:
- `docs/architecture/IOS_APP_ARCHITECTURE_V1.md` (module structure)
- `docs/product/IOS_ONBOARDING_SCREEN_SPEC_V1.md` (onboarding flow)

---

## 2) Navigation Architecture

### 2.1 SwiftUI NavigationStack

Each feature coordinator owns a `NavigationPath`:

```
AppCoordinator
├── TabView (4 tabs)
│   ├── HomeCoordinator → NavigationStack(path: homePath)
│   ├── CirclesCoordinator → NavigationStack(path: circlesPath)
│   ├── ScoreCoordinator → NavigationStack(path: scorePath)
│   └── ProfileCoordinator → NavigationStack(path: profilePath)
└── Modal overlay layer (sheets, full-screen covers)
```

### 2.2 Coordinator Protocol

```swift
protocol Coordinator: ObservableObject {
    associatedtype Route: Hashable
    var path: NavigationPath { get set }
    func navigate(to route: Route)
    func pop()
    func popToRoot()
}
```

Each feature defines its own `Route` enum with all navigable destinations.

---

## 3) Deep Linking: URL-Based

### 3.1 URL Scheme

`rin://` scheme with path-based routing.

| URL | Destination |
|-----|-------------|
| `rin://home` | Home tab |
| `rin://contacts/{id}` | Contact detail |
| `rin://circles` | Circles tab |
| `rin://circles/{id}` | Circle detail |
| `rin://score` | Score tab |
| `rin://score/component/{name}` | Score component detail |
| `rin://profile` | Profile tab |
| `rin://profile/shadow/{id}` | Shadow profile detail |
| `rin://settings` | Settings screen |
| `rin://security` | Security inbox |
| `rin://security/dispute/{id}` | Dispute detail |
| `rin://premium` | Premium paywall |
| `rin://onboarding` | Restart onboarding |

### 3.2 Universal Links

`https://rin.app/` domain for web-to-app deep links:
- `https://rin.app/invite/{code}` — Invite acceptance.
- `https://rin.app/profile/{username}` — Public profile view.

### 3.3 Routing Engine

```
URL received (push notification, universal link, widget, shortcut)
    ↓
AppCoordinator.handleDeepLink(url:)
    ↓
Parse URL into (tab: Tab, route: Route?)
    ↓
Switch to target tab
    ↓
If route exists: push route onto tab's NavigationPath
```

### 3.4 Push Notification Deep Links

| Notification type | Deep link |
|-------------------|-----------|
| Score updated | `rin://score` |
| Dedup suggestions ready | `rin://home?section=dedup` |
| Contact enrichment | `rin://contacts/{id}` |
| Dispute update | `rin://security/dispute/{id}` |
| Circle access request (Ask flow) | `rin://circles/{id}?request={requestId}` |
| Who Viewed Me (premium) | `rin://profile?section=viewers` |

---

## 4) State Management

### 4.1 Observable Pattern

- ViewModels are `@Observable` classes (iOS 17+ Observation framework).
- State flows unidirectionally: ViewModel → View (via @Observable binding).
- User actions flow: View → ViewModel (via method calls).
- No Combine publishers for UI state (Observation replaces this).

### 4.2 Shared State

Cross-feature state managed via shared services in RinCore:

| Service | Shared state | Consumers |
|---------|-------------|-----------|
| `AuthService` | Auth state, current principal | All features |
| `ProfileService` | Active profile (primary/shadow) | All features |
| `SyncService` | Sync status, last sync time | Home, Contacts |
| `ScoreService` | Current score, staleness | Score, Home |
| `NotificationService` | Badge counts | All tabs |
| `PremiumService` | Subscription status | Premium gates |

### 4.3 State Persistence

| State type | Storage | Restore on launch |
|-----------|---------|-------------------|
| Auth tokens | Keychain | Always |
| User preferences | UserDefaults | Always |
| Active profile selection | UserDefaults | Always |
| Contact cache | SwiftData | Always |
| Navigation state | Not persisted | Start at home tab |
| Pending mutations | SwiftData | Resume sync queue |

---

## 5) Modal Presentation Strategy

### 5.1 Modal Types

| Type | Use case | Presentation |
|------|----------|-------------|
| Sheet (half) | Quick actions, confirmations | `.sheet` with detents |
| Sheet (full) | Multi-step flows (dedup review, circle creation) | `.sheet` fullscreen detent |
| Full-screen cover | Onboarding, paywall | `.fullScreenCover` |
| Alert | Destructive confirmations | `.alert` |
| Confirmation dialog | Multiple choice actions | `.confirmationDialog` |

### 5.2 Modal Ownership

The presenting coordinator owns the modal lifecycle. Modals can contain their own NavigationStack for multi-step flows (e.g., circle creation wizard).

---

## 6) Tab Badge Management

| Tab | Badge source | Update trigger |
|-----|-------------|---------------|
| Home | Unreviewed dedup suggestions | Sync completion |
| Circles | Pending access requests (Ask flow) | Push notification |
| Score | Score changed since last view | Daily score batch |
| Profile | Security inbox items | Push notification |

Badges cleared when user views the relevant screen.

---

## 7) Open Decisions

1. Whether to persist navigation state across app kills (state restoration).
2. Whether widget deep links should bypass onboarding if auth is valid.
3. Whether to support Siri Shortcuts for common actions (e.g., "Show my Rin Score").
4. Whether to use `NavigationSplitView` for iPad adaptation or keep iPhone-only layout.
