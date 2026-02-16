# Home Screen Icon Research V1

Generated: 2026-02-16 07:56 UTC

## Sources

- Apple Top Free Apps (US): https://rss.applemarketingtools.com/api/v2/us/apps/top-free/100/apps.json
- Android Top Free (US) proxy: https://www.appbrain.com/stats/google-play-rankings/top_free/us
- Android adaptive icon guidance: https://developer.android.com/develop/ui/views/launch/icon_design_adaptive
- Apple HIG app icons entry: https://developer.apple.com/design/human-interface-guidelines/app-icons

## Key Findings

- iOS sample: 80 icons. Monochrome ratio: 0.175. Avg saturation: 0.509. Avg edge density: 0.093.
- Android sample: 80 icons. Monochrome ratio: 0.212. Avg saturation: 0.491. Avg edge density: 0.106.
- Dominant hue clusters on both platforms are blue/cyan + warm red/magenta families.
- Many high-usage apps are either very simple monochrome glyphs or visually noisy gradient/illustrative icons.
- Strategic whitespace and a single high-contrast geometric move are the clearest route to memorability.

## Top-Hue Distribution

### iOS
- blue (bin 7): 17
- pink-red (bin 11): 14
- red (bin 0): 10
- indigo (bin 8): 9
- orange (bin 1): 6
- cyan (bin 6): 6

### Android
- blue (bin 7): 18
- red (bin 0): 12
- cyan (bin 6): 11
- pink-red (bin 11): 7
- green-cyan (bin 5): 6
- orange (bin 1): 6

## Platform Fit Constraints

- Android adaptive icons: design for a centered safe zone (66x66 inside 108x108) and support monochrome themed icons.
- iOS icons: optimize for rounded-rectangle masking and no text dependence.
- Cross-platform: avoid thin strokes and micro-detail that collapses at small icon sizes.

## Practical Direction For Rin

- Build around one primitive + one structural cut/notch.
- Keep icon-level complexity below market average (target low edge density).
- Use distinctive but restrained color strategy; verify monochrome performance first.

## Top 30 App Names (iOS sample)

1. ChatGPT
2. Google Gemini
3. Threads
4. CapCut: Photo & Video Editor
5. Freecash - Get Paid Real Money
6. Google
7. Temu: Shop Like a Billionaire
8. DoorDash: Food, Grocery, More
9. Whatnot: Shop, Sell, Connect
10. Google Maps
11. Claude by Anthropic
12. Peacock TV: Stream TV & Movies
13. SHEIN - Shopping Online
14. ReelShort - Stream Drama & TV
15. Grok
16. WhatsApp Messenger
17. Instagram
18. TikTok - Videos, Shop & LIVE
19. Walmart: Shopping & Savings
20. Uber - Request a ride
21. OpenTable
22. HBO Max: Stream Movies & TV
23. Duolingo - Language Lessons
24. Tubi: Movies & Live TV
25. Gmail - Email by Google
26. Spotify: Music and Podcasts
27. Discord - Talk, Play, Hang Out
28. The Roku App (Official)
29. Netflix
30. X

## Top 30 App Names (Android sample)

1. ChatGPT
2. EdgeAura
3. TikTok Lite - Faster TikTok
4. TikTok - Videos, Shop &amp; LIVE
5. WhatsApp Messenger
6. Temu: Shop Like a Billionaire
7. Peacock TV: Stream TV &amp; Movies
8. Instagram
9. Photo Editor Video Maker Music
10. Easy Homescreen
11. CapCut - Video Editor
12. Whatnot: Shop, Sell, Connect
13. Cash App
14. Cleaner Launcher for Android
15. DoorDash - Dasher
16. Threads
17. Freecash: Earn Money
18. Snapchat
19. ​​Microsoft Copilot
20. Facebook
21. Tubi: Free Movies &amp; Live TV
22. Telegram
23. ReelShort - Stream Drama &amp; TV
24. Grok • Smartest AI Advisor
25. PDF Reader
26. Discord - Talk, Play, Hang Out
27. Walmart: Shopping &amp; Savings
28. TurboTax: File Your Tax Return
29. Indeed Job Search
30. PDF Reader - Editor &amp; Viewer

