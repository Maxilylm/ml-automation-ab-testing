---
name: ab-sequential
description: "Sequential testing with alpha spending functions and optional stopping rules for A/B experiments."
aliases: [sequential test, optional stopping, group sequential, early stopping]
extends: ml-automation
user_invocable: true
---

# A/B Sequential

Sequential testing for A/B experiments with valid early stopping. Supports group sequential tests with alpha spending functions (O'Brien-Fleming, Pocock), always-valid inference, and mixture sequential probability ratio tests. Tracks test statistic trajectories against boundaries and provides adjusted confidence intervals.

## Full Specification

See `commands/ab-sequential.md` for the complete workflow.
