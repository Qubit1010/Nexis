# Mobile Playbook

**Source basis:** `research-synthesis.md` Q7 (sources `[s155]`–`[s174]`). Load for mobile/PWA/native questions.

## First question: do you even need a native app?
A well-built **PWA delivers ~80% of native UX at ~40–60% of the cost** [s162]. Decide by distribution + hardware, not benchmarks.

| If… | Build | Why |
|---|---|---|
| B2B SaaS / internal / content, found via search | **Web app** | No app-store needed [s162][s165] |
| Need home-screen + push + offline, one codebase | **PWA** | ~80% native UX, ~$12K–$36K vs $40K–$120K native [s162][s163] |
| Deep hardware (ARKit/NFC/HealthKit), AR, games, on-device ML, regulated, or app-store-browse discovery | **Native** | Only case native clearly wins [s162][s164] |

## Cross-platform: React Native (Expo) vs Flutter
- **React Native + Expo** — default when you have a React/web team; one codebase incl. web [s158]. **New Architecture** (Fabric + JSI + TurboModules) default in RN 0.76: ~43% faster startup, ~39% faster render [s156][s160]. Expo matches bare RN cold start (~341ms Android / ~267ms iOS) [s155]. **Expo SDK 55 / RN 0.83 = New Architecture only** [s172][s173].
- **Flutter** — pixel-perfect bespoke UI, embedded/kiosk, no web reach; ~46% share vs RN ~35%; Impeller default, jank gone [s158][s161][s160].
- **Reality:** for most business apps, cross-platform is indistinguishable from native in real UX; decide on **team skills + hiring market**, not FPS [s156][s159].

## NexusPoint default
Web-first / PWA. Recommend native only when a client requirement genuinely demands it — matches the revenue mix and team (see `dev-context.md`). If cross-platform is needed and the team is React-based, that's React Native + Expo.

## Checklist
- [ ] Ran the PWA-vs-native gate before picking a framework.
- [ ] If native/cross-platform: justified by hardware/distribution, not perf myths.
- [ ] Matched framework to team's existing skills.
- [ ] Noted New Architecture migration if RN/Expo.
