# Logs Directory (`logs/`)

## Purpose
The `logs/` directory stores persistent application execution logs for the **Sovereign On-Premise Agentic AI Workbench**.

## Storage & Retention Rules
- **Log Format**: `[YYYY-MM-DD HH:MM:SS.sss] [LEVEL] [LOGGER] [MODULE:LINE] - MESSAGE`
- **Primary Log File**: `workbench.log`
- **Rotation Strategy**: Standard rotating file handler (default 10 MB per file, up to 5 historical log backups).
- **Git Status**: Log files (`*.log`) are ignored by version control to maintain confidentiality and clean repository tracking.
