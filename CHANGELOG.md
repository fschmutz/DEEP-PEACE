# Changelog

All notable changes to this repository are recorded here.

The format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/), and
this repository adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added

- Lock-screen playback: Web Audio routed through a `MediaStreamAudioDestinationNode`
  into a hidden `<audio>` element, `navigator.audioSession.type = 'playback'`,
  resume on visibility and interruption, fallback to direct output.
- Media Session metadata, artwork, play/pause/stop handlers and position state.
- Home Screen web app: `manifest.webmanifest`, generated icons, apple-touch-icon,
  cache-first versioned service worker `sw.js` with update on new version.
- Breathing pace (4–8 breaths/min, default 6) and inhale:exhale ratio, scheduled
  on the audio clock; hidden in Steady mode.
- Synthesized singing bowl at start and end, optional interval bell (5 or 10 min).
- Optional slow fade over the last 5 or 10 minutes.
- Steady mode (Breathing / Steady switch): no binaural beat, no breath LFO,
  no detune, still circle; applies to every preset and is remembered.
- English / French interface (EN | FR switch). The first visit follows
  `navigator.language`, the choice is remembered, and `<html lang>` is set.
- `index.html`: the Deep Peace app — four presets (Deep peace, Om, Yoga nidra,
  Ocean breath), binaural beat, low-pass harmonic pad, breath-modulated noise,
  5–60 minute timer, volume, breathing circle, screen wake lock. No dependencies.
- Repository created from `ScaleMeNow/GITHUB-TEMPLATE` (bundles A–E), MIT
  licence, served by GitHub Pages from `main`.
