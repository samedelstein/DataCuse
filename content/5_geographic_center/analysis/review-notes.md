# Review notes - September 24, 2026

Status: ready for Sam's review; article remains draft and has not been committed, pushed or published.

- Fresh municipal polygon downloaded and hashed. Single feature, valid geometry, centroid inside city.
- Independent signed-area computation agrees to numerical precision. Equal-area projection check moves the center by 0.102 m.
- State and older city street layers agree on the nearby South McBride/Jackson location. Inspected 2022 aerial; made no present-day site/access claim.
- Opened the final article graphic and inspected geography, labels, scale and layout. Main and inset maps preserve aspect ratio.
- Browser reviewed at desktop (1280 px) and mobile (390 px). Mobile page has no horizontal overflow. Native answer and compass accordions render in place. No answer text or center marker appears in the initial view.
- Verified blue guess pin appears, answer reveal scores the guess, reset hides the answer, map zoom and keyboard movement work. The previous SVG hidden-attribute bug has a regression test.
- Manual coordinate input one hundredth of a degree north of the center yields 0.69 miles, due south (180 degrees). Choosing the center suppresses the arrow and shows the near-center message.
- Verified compass embedded in the story; there is no separate app navigation. The original guess is held fixed for scoring while the compass can use another starting point.
- 18 automated tests passed: numerical geometry/bearings, uncertainty, headings, guessing state, marker visibility, permission-denied/timeout mock responses, stale callbacks, publishing assets and existing publisher tests. `npm.cmd run build:stories` passed; this draft remains absent from the public archive/feed/output.
- GPS permission and physical phone sensors were not exercised with a real personal location. These remain a device check, not a claim of cross-device compass accuracy.
- Browser automation had intermittent scrolling/capture timeouts; verified final states with screenshots, live DOM and keyboard controls. No app console errors were observed.

The normal public build also picked up the already-edited September 24 date in post 4's source and updated its generated page/archive/feed ordering. Post 5 itself remains unpublished.
