# Agent entry point

Read [Agent.MD](Agent.MD) before working on this project. It is the main research handoff and records the user's agreed **RIS + FJ + VLC + DRL** objective, the 2024-paper baseline, existing code, known limits and next steps.

The agreed baseline is the original paper system extended with an optical RIS. The separate `physical` mode is an earlier diagnostic alternative and must not silently replace that baseline. RIS is fully implemented and tested (87 unit tests passed; 36 multi-seed runs executed). See `antigravity_report/` for the complete master handoff and documentation. Preserve existing work and distinguish implementation tests from numerical paper reproduction.

Keep detailed handoff updates in `Agent.MD` so these two files do not become competing specifications. Explicit later user instructions take precedence over historical handoff notes.
