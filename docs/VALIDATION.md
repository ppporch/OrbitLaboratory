# Validation

The isolated runner executes Bill's installed PDP-1 CPU object, with multiply
and extended memory enabled. Its Type 340 adapter captures native lists without
operating the panel or live media. Tests compare 2,000 positions each for circular,
elliptical, escape and impact cases against an independent integer implementation.
The circular/ellipse checks also assert radius bounds, independently of exact
CPU equality. Escape/impact cases stop at their defined boundaries.

Controls tests verify 12.5% speed changes, circle/ellipse resets and held-switch
debouncing. The actual main loop is run for three frames with switch 1 off and
on: the off case makes zero physics steps and the on case makes three.
A full trail scene checks all native vector endpoints, frame capacity, guard,
read-only font/force tables, and both longest stopped-state captions. Tests
restore the production binary after their special builds.

Detailed test and live results accompany the completed build. Client visual
appearance and actual timing are checked separately on the running Pi.

The complete P1GL suite also passes with the short-vector optimization,
including native points/lines/circles/text, retained frames, vector-font
clipping/banking and the embeddable vector sink. Native command geometry
is unchanged by the short-line path.

Static-prefix retention is checked across consecutive renders; the dynamic
trail and captions remain bounded and both stopped-state labels fit.

The final incremental renderer is exercised through 140 production frames,
including ring wrap. Every one of the 63 adjacent edges between retained
trail points appears in the final display, and every frame stays within the
2,000-word allocation. The ring-wrap check caught and corrected a signed
one's-complement index error. The full scene reaches 1,922 words in that test.
Unchanged records are reused only after the preceding display completes.

Live on Phillip's Pi, the completed build advanced 282 frames in 15.001
seconds (53.19 ms mean per frame, including startup). The full 64-point
trail was present; program/display faults were zero, motion remained active
and the display buffer guard was intact. The screen was visually inspected.
The first full-rebuild prototype measured about 1.8 frames/sec; immutable
prefix reuse plus changed-slot updates substantially reduce CPU building work.
This mean is not a worst-case timing or client-rendering guarantee. See
live-validation.json and orbit-screen.png. Signal Station's previous core
and registers were saved in the installed snapshots directory before loading.

## Angular fading trail

The reference circle is hidden. Field 3 holds the angle renderer and stamps,
so no orbit arithmetic or sample coordinates were changed. A seven-bit ratio
and arctangent lookup give 256 angular units per revolution; winding stamps
prevent old trail slots from reappearing after a full turn. Eight hardware
intensity levels fade the newest edges to the oldest. At age 126 units the
point SHOW and vector VISIBLE flags are cleared, giving a small quantization
margin below half a turn. A paused spacecraft leaves the trail unchanged.

All numerical/control/render regression cases pass. Across 140 frames each
of circular and elliptical motion, independent screen-space angle checks
validated 2,745 and 1,693 visible edges respectively against the half-turn
limit. Ring and angular wraps are included. A final circular scene had 24
visible and 40 expired slots, using all eight brightness levels. The scene
uses at most 1,730 of its 1,900 display words in these checks; all stopped-state
captions also fit. Detailed results are in validation.json. The old installed
source and core were saved under snapshots before replacement.

Live validation completed 150 frames in 12.001 seconds (80.01 ms mean),
with fault 0, display fault 0 and an intact buffer guard. The captured live
scene contained 24 visible trail segments across all eight intensity levels;
40 expired slots were hidden. The screen shows a fading arc and no fixed
reference circle. This mean includes CPU shading and display work; it is
not a worst-case guarantee. See fade-live-validation.json and fade-screen.png.

## Phosphor-only motion (current build)

Software trail geometry, history buffers, angle calculation and fading flags
are removed. The viewer supplies phosphor persistence. The marker is projected
on every physics step, rather than every second step. The reference circle
remains hidden. No force/integration arithmetic or console controls changed.

All existing numerical and control cases pass. An isolated 140-frame run
checks the exact marker position on every step against the independent model.
Every frame has the same 163 vectors, proving that no software trail accumulates.
The scene uses at most 1,346 of 1,500 display words in that run, and both longer
stopped-state captions also fit. Font/force data and the display guard remain
unchanged. Field 3 is no longer allocated. Earlier trail sections above describe
superseded builds. See validation.json for current test results.

Live on the Pi, the phosphor-only build completed 316 frames in 12.001 seconds
(37.98 ms mean, compared with 80.01 ms for software fading). Program/display
faults were zero and the guard was intact. The captured screen shows only the
central body and current moving marker, with viewer persistence. No phosphor
or viewer settings were changed. See phosphor-live-validation.json and
phosphor-screen.png. The previous source and core were backed up before loading.

## Instruments and PENMENU (current checkpoint)

The panel displays normalized radius R/R0, instantaneous speed V/V0 and
BOUND / NEAR ESC / ESCAPING. It recovers instantaneous velocity from the
leapfrog half-step before evaluating speed and energy, without changing
physics state. Nine-iteration integer square root and fixed-point product
extraction supply the readings. Sampling is once per five rendered frames.

Launch, ellipse, escape and near-escape fixtures pass. Twenty-four independent
quadrant cases bound radius error below 0.016 and speed error below 0.025
in normalized units. Throttling and immutable physics state are checked.
The final renderer patches only the 30 native glyph words; tests verify that
none of the panel's position/scale words change when readings change.

Bill's installed PENMENU supplies six top-bar buttons. The optional P1GL
poll hook reads/resumes light-pen pauses and saves a mailbox; main-loop
actions and all menu/list changes happen only after refresh completion.
A bank-1 wrapper scans the menu before the retained application frame.
Tests exercise all six buttons, held-pen debouncing, pause/run/step and
ignoring off-menu hits, through the actual PENMENU and production loop.
The existing orbital and complete default P1GL suites also passed.

Live mouse tests verified pause with continuing display refresh, exactly one
step, ellipse launch at 1.00 / 0.75, Faster to 0.84, and Circle reset to
1.00 / 1.00. The demo was left running. Program/display faults remained zero
and the display guard stayed intact. An initial panel rebuild had periodic
71-ms frames; character-only patching reduced the sampled mean to 43.48 ms,
median 41.19 ms and maximum 56.99 ms over 160 measured intervals. Sample
frames still averaged 52.39 ms versus roughly 41 ms for ordinary frames.
These are observations, not deadline guarantees. Further tuning is deferred.

Checkpoint: development paused at Phillip's request. Remaining optional work
is to assess visible text stability with Phillip and, if needed, reduce the
sampled-frame work further. No software trail or fading was reintroduced.
