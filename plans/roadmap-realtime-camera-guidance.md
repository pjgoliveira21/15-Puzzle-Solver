# Roadmap: real-time webcam recognition and live solve guidance

The user's actual end goal for this project, staged for future sessions.
Stage A (mode split, step-by-step instructions, algorithm comparison — all
on static/file-picker image input) is done; see
[repo-workflow-docs-and-easy-advanced-mode.md](repo-workflow-docs-and-easy-advanced-mode.md).
Stages B-E below are not started.

- **Stage B**: single-shot webcam capture — one photo via camera through
  the existing scan pipeline, using the `integration/capture.py` seam
  (`choose_photo_source`'s `Path | None` contract).
- **Stage C**: live preview prototype — periodic re-scan of a webcam feed;
  likely needs real performance work (the current template-matching
  pipeline was never built for interactive frame rates).
- **Stage D**: real-time move tracking — diff successive scans to detect
  the user's physical moves, re-plan/re-guide accordingly; likely needs
  recognition more robust than template matching given the lighting/angle
  sensitivity already measured in `tests/vision/expected_grids.json`.
- **Stage E**: full AR-style live-guided solving.

None of these have a validated file-by-file design yet - that's the next
planning pass to do before implementing Stage B.
