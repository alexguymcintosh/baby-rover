# Architecture decision records (ADRs): design choices, tradeoffs, and rationale.

## ADR-001 — Encoder reading: polling vs interrupt-driven callbacks

**Date:** 2026-02-24
**Status:** Active

**Decision:**
Poll encoder pins at 100Hz via ROS 2 timer instead of interrupt-driven callbacks.

**Why:**
lgpio 0.2.0.0 (installed on Pi 5 Ubuntu 24.04) has broken interrupt-driven callbacks.
gpio_claim_alert registers correctly but callbacks never fire. Hardware confirmed working
via raw GPIO reads — the bug is in lgpio's callback threading, not the wiring.

**Alternatives considered:**
- Interrupt-driven callbacks via lgpio — broken on this version
- gpiozero edge detection — not tested
- Dedicated microcontroller (Arduino) for encoder counting over serial — overkill at this scale

**Tradeoff:**
Polling at 100Hz may miss pulses at high wheel speeds. Acceptable for baby rover scale.
Will cause odometry drift at university rover speeds.

**Revisit when:**
- lgpio is upgraded
- Moving to university rover with higher speed motors