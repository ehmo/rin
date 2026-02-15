# iOS App Architecture V1

## 1) Purpose

Define the iOS app module structure, architecture pattern, and dependency boundaries for v1.

Companion docs:
- `docs/architecture/SERVICE_IMPLEMENTATION_BLUEPRINT_V1.md` (backend service map)
- `docs/architecture/MONOREPO_CONVENTIONS_V1.md` (repo structure)
- `docs/product/IOS_ONBOARDING_SCREEN_SPEC_V1.md` (screen inventory)

---

## 2) Architecture Pattern: MVVM + Coordinator

### 2.1 Layer Responsibilities

| Layer | Responsibility | Rules |
|-------|---------------|-------|
| **View** | SwiftUI views, UI state rendering | No business logic. Binds to ViewModel only. |
| **ViewModel** | Presentation logic, state management | @Observable classes. Calls domain services. No UIKit/SwiftUI imports. |
| **Coordinator** | Navigation flow, screen transitions | Owns NavigationPath. Creates ViewModels. Handles deep links. |
| **Domain** | Business rules, use cases | Pure Swift. No framework dependencies. Testable in isolation. |
| **Data** | Networking, persistence, device APIs | Repository pattern. Protocols for testability. |

### 2.2 Dependency Direction

```
View → ViewModel → Domain → Data (protocols)
                              ↑
Coordinator → ViewModel    Data (implementations)
```

- Views depend on ViewModels.
- ViewModels depend on Domain services (via protocols).
- Domain defines repository protocols.
- Data implements repository protocols.
- Coordinators create ViewModels and manage navigation.
- No circular dependencies. No upward dependencies.

---

## 3) Module Structure: Swift Packages

Each feature is a separate Swift Package for build isolation, testability, and clear boundaries.

### 3.1 Package Map

```
apps/ios/
├── RinApp/                    # App target (thin shell)
│   ├── AppDelegate.swift
│   ├── RinApp.swift
│   └── AppCoordinator.swift
│
packages/swift/
├── RinCore/                   # Shared foundation
│   ├── Models/               # Domain models, DTOs
│   ├── Networking/           # API client, auth, request/response
│   ├── Storage/              # Local persistence (SwiftData/UserDefaults)
│   ├── Analytics/            # Event tracking abstraction
│   └── Utilities/            # Extensions, formatters, constants
│
├── RinUI/                     # Shared UI components
│   ├── Components/           # Reusable views (buttons, cards, badges)
│   ├── Theme/                # Colors, typography, spacing tokens
│   └── Modifiers/            # Common view modifiers
│
├── RinOnboarding/             # Onboarding feature
│   ├── Coordinator/
│   ├── ViewModels/
│   ├── Views/
│   └── Services/
│
├── RinContacts/               # Contacts import, sync, dedup, list
│   ├── Coordinator/
│   ├── ViewModels/
│   ├── Views/
│   └── Services/
│
├── RinCircles/                # Circle management, access policies
│   ├── Coordinator/
│   ├── ViewModels/
│   ├── Views/
│   └── Services/
│
├── RinProfiles/               # Profile management, shadow profiles, card picker
│   ├── Coordinator/
│   ├── ViewModels/
│   ├── Views/
│   └── Services/
│
├── RinScore/                  # Rin Score display, explanations, analytics
│   ├── Coordinator/
│   ├── ViewModels/
│   ├── Views/
│   └── Services/
│
├── RinSecurity/               # Security inbox, disputes, trust flows
│   ├── Coordinator/
│   ├── ViewModels/
│   ├── Views/
│   └── Services/
│
├── RinSettings/               # App settings, account management, premium
│   ├── Coordinator/
│   ├── ViewModels/
│   ├── Views/
│   └── Services/
│
└── RinPremium/                # Premium features, StoreKit 2, paywall
    ├── Coordinator/
    ├── ViewModels/
    ├── Views/
    └── Services/
```

### 3.2 Dependency Graph

```
RinApp
├── RinOnboarding → RinCore, RinUI
├── RinContacts   → RinCore, RinUI
├── RinCircles    → RinCore, RinUI
├── RinProfiles   → RinCore, RinUI
├── RinScore      → RinCore, RinUI
├── RinSecurity   → RinCore, RinUI
├── RinSettings   → RinCore, RinUI, RinPremium
└── RinPremium    → RinCore, RinUI

RinCore → (no internal dependencies)
RinUI   → RinCore (for theme tokens)
```

Rules:
- Feature packages depend on RinCore and RinUI only.
- Feature packages never depend on each other directly.
- Cross-feature communication via Coordinator or shared domain protocols in RinCore.

---

## 4) App Shell

### 4.1 AppCoordinator

The root coordinator manages:
- Tab bar navigation (if tabbed) or root navigation stack.
- Feature coordinator lifecycle.
- Deep link routing.
- Authentication state gating (show onboarding vs main app).
- Profile switching (delegates to RinProfiles coordinator).

### 4.2 Navigation Model

SwiftUI NavigationStack with programmatic NavigationPath per coordinator.

- Each feature coordinator owns its own NavigationPath.
- AppCoordinator switches between feature coordinators at the tab/root level.
- Modal presentations handled by the presenting coordinator.

### 4.3 Tab Structure (V1)

| Tab | Package | Primary screen |
|-----|---------|---------------|
| **Home** | RinContacts | Smart sections contact list |
| **Circles** | RinCircles | Circle management |
| **Score** | RinScore | Rin Score + explanations |
| **Profile** | RinProfiles | Active profile + card picker |

Settings and Security accessible from Profile tab.

---

## 5) Networking Layer (RinCore)

### 5.1 API Client

- Single `APIClient` actor in RinCore.
- Typed request/response with `Codable` DTOs.
- Auth token management (JWT or session token).
- Automatic retry with exponential backoff for transient errors.
- Request correlation IDs for server-side tracing.
- Idempotency key injection for mutations.

### 5.2 Auth Boundary

- Token storage in Keychain.
- Token refresh handled transparently by APIClient.
- Auth state published via `AuthService` protocol for coordinators to observe.
- Unauthenticated state triggers onboarding coordinator.

### 5.3 Contract Versioning

- API version header sent with every request.
- Client supports graceful degradation for unknown response fields (`CodingKeys` ignore extras).
- Server contract changes follow expand/contract strategy per API surface outline.

---

## 6) Local Storage (RinCore)

### 6.1 Technology

- **SwiftData** for structured local data (contacts cache, circle membership, profile state).
- **UserDefaults** for simple preferences (onboarding complete, last sync timestamp, theme).
- **Keychain** for sensitive data (auth tokens, encryption keys).

### 6.2 Offline Behavior (V1)

- Contacts list and circle membership cached locally for offline viewing.
- Mutations queue locally and sync when connectivity returns.
- Rin Score cached with last-computed timestamp. Stale indicator shown if >24h old.
- No offline-first write architecture in v1 — online is required for most actions.

---

## 7) Analytics and Events (RinCore)

### 7.1 Event Tracking

- `AnalyticsService` protocol in RinCore.
- Feature packages emit domain events via protocol (no direct SDK dependency).
- Implementation in RinApp injects the concrete analytics SDK (Sentry, product analytics).
- All onboarding funnel events from screen spec are wired in RinOnboarding.

### 7.2 Crash Reporting

- Sentry SDK integrated at the app target level.
- Breadcrumbs for navigation events and API calls.
- User context (anonymized principal ID) attached for debugging.

---

## 8) Testing Strategy

### 8.1 Unit Tests

- Each feature package has its own test target.
- ViewModels tested with mock services (protocol-based injection).
- Domain services tested with mock repositories.
- Target: 80%+ coverage on ViewModels and Domain layers.

### 8.2 UI Tests

- Snapshot tests for key screens using Swift Snapshot Testing.
- Accessibility audit tests (Dynamic Type, VoiceOver labels).

### 8.3 Integration Tests

- API contract tests against staging environment.
- End-to-end onboarding flow test via Maestro or XCUITest.

---

## 9) Build and CI

- Xcode project uses Swift Package Manager for all internal packages.
- CI pipeline: build all packages → run unit tests → run snapshot tests → archive.
- Build time target: <3 minutes for incremental builds (package isolation helps).
- No CocoaPods. SPM for third-party dependencies.

---

## 10) Third-Party Dependencies (V1 Minimal)

| Dependency | Purpose | Integration |
|-----------|---------|-------------|
| **Sentry** | Crash reporting + performance | App target only |
| **StoreKit 2** | Premium subscriptions | RinPremium package |
| **CNContactStore** | Contact import | RinContacts package |
| **SwiftData** | Local persistence | RinCore |

Principle: minimize third-party dependencies. Prefer Apple frameworks. Add dependencies only when build-vs-buy analysis clearly favors buy.

---

## 11) Open Decisions

1. Whether to use SwiftData or Core Data for local persistence (SwiftData is newer but less battle-tested).
2. Exact analytics SDK choice for product events (Sentry vs Mixpanel vs custom).
3. Whether to support iOS 17+ only or iOS 16+ for broader reach.
4. Image caching strategy for profile photos (URLCache vs third-party like Kingfisher).
5. Whether the card picker (profile switcher) should be a shared component in RinUI or scoped to RinProfiles.
