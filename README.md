<div align="center">

# Deep Peace

**A zero-dependency, low-frequency yoga sound app: a deep drone, a binaural beat and a slow breathing guide, in one HTML file.**

[![open the app](https://img.shields.io/badge/open-fschmutz.github.io%2FDEEP--PEACE-2ea043)](https://fschmutz.github.io/DEEP-PEACE/)
[![license](https://img.shields.io/badge/license-MIT-1f6feb)](LICENSE)
[![dependencies](https://img.shields.io/badge/dependencies-none-6e7681)](#how-it-works)
[![CI](https://github.com/fschmutz/DEEP-PEACE/actions/workflows/ci.yml/badge.svg)](https://github.com/fschmutz/DEEP-PEACE/actions/workflows/ci.yml)

</div>

---

## Screenshots

| Phone view |
|---|
| <img src="docs/screenshots/app.png" alt="The Deep Peace app on a phone: breathing circle reading Ready 20:00, EN/FR switch, four sound presets, Breathing/Steady switch, duration buttons and a volume slider" width="300"> |

## Contents

- [Use it](#use-it)
- [Presets](#presets)
- [How it works](#how-it-works)
- [Repository](#repository)

## Use it

Open **https://fschmutz.github.io/DEEP-PEACE/** in Chrome or Safari, pick a sound and a duration, tap **Begin**.

- Wear headphones: the binaural beat needs a separate tone in each ear.
- On iPhone, switch silent mode off and turn the volume up.
- The page asks the screen to stay awake while it plays, because a locked screen can pause audio.

## Presets

| Preset | Drone | Beat | Breath cycle |
|---|---|---|---|
| Deep peace | 108 Hz, harmonics up to 432 Hz | 6 Hz (theta) | 10 s |
| Om | 136.1 Hz | 7.83 Hz | 12 s |
| Yoga nidra | 72 Hz | 2.5 Hz (delta) | 14 s |
| Ocean breath | 96 Hz | 4 Hz | 11 s |

- **Breathing / Steady** — Breathing (default) gives the binaural beat, a breath-paced swell and the in/out guide. Steady removes every variation: both ears get the same tone, the noise stays constant, no detune shimmer, and the circle stays still while the countdown runs. Works with every preset. The page remembers your choice.
- **EN / FR** — the switch at the top translates the whole interface. The first visit follows the browser language, and the page remembers your choice.

Timers: 5, 10, 20, 30, 45 or 60 minutes. Start fades in over 4 s, Stop fades out over 3 s.

## How it works

Everything is `index.html`: plain HTML, CSS and JavaScript on the Web Audio API. No framework, no npm, no CDN, no web font, no build step, no network request after the page loads.

- **Binaural beat** — the left ear gets the base frequency, the right ear base + beat, joined by a `ChannelMerger`.
- **Pad** — a few harmonics of the base through a low-pass filter.
- **Breath** — looping brown-ish noise whose level follows a slow LFO at the breath rate; the circle on screen grows and shrinks with it.

GitHub Pages serves the file straight from `main` at the repository root.

## Repository

Made from the house GitHub template ([`ScaleMeNow/GITHUB-TEMPLATE`](https://github.com/ScaleMeNow/GITHUB-TEMPLATE)) with bundles **A–E** on, as for any public toy. Documentation lives in [`wiki/`](wiki/Home.md); conventions are in [`CONTRIBUTING.md`](CONTRIBUTING.md) and [`AGENTS.md`](AGENTS.md).
