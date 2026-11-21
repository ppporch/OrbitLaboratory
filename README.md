# Orbit Laboratory — first prototype

An interactive two-body orbital demonstration for Bill Ezell's PiDP-1,
using P1GL and the Type 340 display. The PDP-1 computes the trajectory;
the Type 340 draws continuous vector outlines and a spacecraft marker.
The title uses P1GL's Hershey vector-stroke font.

## Build and run

Requires `/opt/pidp1-mods`, AM1, extended memory, hardware multiply/divide,
the Type 340/342 display, and the BBN clock. Five memory fields are used. Bill's `Am1Includes/PENMENU` library must be installed.

```sh
cd /opt/pidp1-mods/FunStuff/OrbitLaboratory
make
```

With power on and the CPU halted, save any current work, then load:

```sh
/opt/pidp1-mods/bin/fastload -y build/orbit.rim
```

Open the usual t30dpy/t30dpy3 viewer. Its Type 30 window title does not indicate
which controller the program uses. This program uses Type 340 commands.

A matching, previously tested binary is also included for a quick trial:

```sh
/opt/pidp1-mods/bin/fastload -y prebuilt/orbit.rim
```

Use the same power-on/CPU-halted procedure. `prebuilt/orbit.sym` matches that
binary. The compiled PENMENU component comes from Bill's repository; its
notice is included in `third_party/PIDP1-MODS-LICENSE`.

## Console controls

| Sense switch | Action |
| --- | --- |
| 1 | On: run. Off: pause; display continues refreshing. |
| 2 | Pulse on/off to advance one physics step while paused. |
| 3 | Pulse to reduce both velocity components by approximately 12.5%. |
| 4 | Pulse to increase both velocity components by approximately 12.5%. |
| 5 | Pulse to reset to the circular starting orbit. |
| 6 | Pulse to reset to an elliptical starting orbit. |

Switches 2–6 act on their rising edge. Switches already on at startup do not
trigger an action; turn one off and on to pulse it. Pause before experiments
if you want to apply a change at a chosen point. Repeated boosts near the
circular start can produce an escaping trajectory; repeated slowing can
produce an impact. Velocity boosts are bounded to prevent numeric wrap.

The central outline is the body's collision boundary. A small cross marks the
spacecraft's current position. No trajectory history or software fading is drawn;
the display viewer's phosphor persistence supplies any afterglow. The reference
circle remains hidden. IMPACT or LEFT VIEW stops physics; use switch 5 or 6 to
reset. LEFT VIEW means the fixed viewport was exceeded, not an energy classification.
Both console switches and the light-pen menu are supported.

## Instrument panel and mouse controls

The top bar uses Bill's PENMENU library. Click the drawn labels with the viewer's
left mouse button: **RunStop**, **Step**, **Slower**, **Faster**, **Circle** or
**Ellipse**. Release for at least 250 ms between presses. Holding a button does
not repeat it. Step acts while paused. A menu RunStop choice overrides the
current switch-1 setting until you next change that physical switch; switches
2–6 retain their pulse actions.

**R/R0** is distance from the central body divided by the initial launch radius.
**V/V0** is instantaneous speed divided by the initial circular speed. The initial
circle therefore reads 1.00 / 1.00; the elliptical launch reads 1.00 / 0.75.
**BOUND**, **NEAR ESC** or **ESCAPING** reports the sign of the specific orbital
energy, with a narrow uncertainty band around escape. It is a trajectory-energy
classification, not a prediction that the spacecraft will avoid an impact.
Readings are sampled once every five display frames. P1GL updates the
fixed-width labels when their values change.
They are estimates: distance has roughly 0.01 resolution, while speed's integer
square-root quantization can introduce about 0.02 of the circular speed.
The velocity calculation removes the integrator's half-step offset before
estimating speed and energy; it never changes the numerical state.

## Model and practical limits

Dimensionless gravitational parameter `mu=1`, initial radius `r=1`, and fixed
step `dt=1/16`. Positions and staggered velocity increments use signed
one's-complement Q14. Drift/kick leapfrog uses a generated inverse-cube force
table indexed by squared radius. Force products round to nearest using the
hardware multiply option's full result. CPU execution, rather than host code,
updates every displayed orbit.

Orbit builds the title, central body, captions and controls once. A P1GL
retained group holds the spacecraft marker, which is replaced when its screen
position changes. Updatable P1GL labels hold the radius, speed, energy class
and run status. The marker and readings update between completed scans.

The force table, finite step and fixed-point rounding introduce error. In the
2,000-step circular check the radius ranges about 0.947–1.023; this is an
educational prototype, not a precision orbit predictor. The ellipse test stays
bound, and separate cases exercise impact and leaving the view. Time advances
by one fixed simulation step per rendered frame, with a nominal 25-ms minimum
frame period. Slow drawing slows the simulation's wall-clock pace. Refresh
performance is measured on the target separately; no fixed frame-rate promise.

Field 0 contains the program, reading text and a bounded retained display list. Field 1
contains the vector font and menu display list; field 2 contains the read-only
force table. Field 3 contains instrument code and scratch; field 4 contains
Bill's resident PENMENU code and state. The vector font remains read-only.
The program does not read or write tape/drum media. `make test` uses an isolated
CPU and captured display lists, not the running emulator.

P1GL source is bundled for independent builds, pinned to P1GL commit `3febfbb`, with
its tested short-line fast path: lines whose components fit a single
native vector avoid a CPU walk through every intermediate pixel. See
[p1gl/README.md](p1gl/README.md) and [validation](docs/VALIDATION.md).

Direction and real-machine visual testing: Phillip Porch. Implementation and
automated checks: ChatGPT/Codex, working with Phillip. Code is MIT; Hershey
font data retain the notices in `p1gl/fonts/HERSHEY-NOTICE.txt`.
