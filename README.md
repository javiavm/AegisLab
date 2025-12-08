# Safety Agent PoC

AI-driven safety observation workflow with multi-agent architecture.

## Overview

This PoC validates an agentic architecture for processing safety observations in industrial environments. The system consists of three core agents orchestrated by a central pipeline:

1. **Risk Analyzer Agent** - Parses observations and detects hazards
2. **Score Manager Agent** - Scores hazards using risk matrices
3. **Action Planner Agent** - Generates corrective action plans

## Architecture

```
Observation Input
       │
       ▼
┌─────────────────┐
│   Orchestrator  │
└────────┬────────┘
         │
    ┌────┴────┐
    ▼         ▼
┌─────────┐ ┌─────────┐ ┌─────────┐
│  Risk   │→│  Score  │→│ Action  │
│Analyzer │ │ Manager │ │ Planner │
└─────────┘ └─────────┘ └─────────┘
    │           │           │
    ▼           ▼           ▼
 Hazards   ScoredHazards  ActionPlans
```

## Quick Start

### Installation

```bash
# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # Linux/Mac
# or: .venv\Scripts\activate  # Windows

```


## License

MIT
