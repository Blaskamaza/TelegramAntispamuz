# UZ AI Factory — V2 Architecture

> **Date**: 2026-01-17  
> **Status**: Production-Ready  
> **Tag**: `v0.9.0-finish-line`

## 🏗️ Architecture Overview

```
┌─────────────────────────────────────────────────────────┐
│                      TheBoss                            │
│  (Orchestrator — creates worktrees, runs agents)        │
└────────────────────────┬────────────────────────────────┘
                         │
         ┌───────────────┼───────────────┐
         ▼               ▼               ▼
   ┌──────────┐   ┌──────────┐   ┌──────────┐
   │   CPO    │   │ TechLead │   │   CMO    │
   │(generate │   │          │   │          │
   │_skills)  │   │          │   │          │
   └────┬─────┘   └──────────┘   └──────────┘
        │
        ▼
   ┌───────────────────────────────────────┐
   │          Skills System                │
   │  ┌──────────────┐ ┌────────────────┐  │
   │  │prd-standard  │ │uz-procurement  │  │
   │  │-uz           │ │-analyzer       │  │
   │  └──────────────┘ └────────────────┘  │
   └───────────────────────────────────────┘
```

## 🎯 Core Components

| Component | File | Purpose |
|-----------|------|---------|
| **WorkspaceManager** | `services/workspace_manager.py` | Git worktree isolation |
| **AgentRunner** | `services/agent_runner.py` | Subprocess execution |
| **SkillManager** | `services/skill_manager.py` | Skill discovery/loading |
| **CircuitBreaker** | `services/circuit_breaker.py` | Vertex AI protection |
| **TheBoss** | `agents/boss.py` | Pipeline orchestration |

## 🚀 Quick Start

```bash
# 1. Create a task
python tools/new_task.py "EdTech for ENT prep" --agent=cpo

# 2. Run the pipeline
python agents/boss.py --idea "EdTech for ENT prep"

# 3. Check results
python tools/battle_report.py

# 4. Review and merge
python tools/review.py <task-id>
```

## 📡 API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/health` | GET | System health |
| `/api/health/vertex` | GET | Circuit breaker status |
| `/api/board/tasks` | GET | Kanban board |
| `/api/agent/run` | POST | Start agent |
| `/api/agent/logs/{id}` | GET | Agent logs |

## 🔧 Configuration

```python
# config.py
WORKTREE_DIR = BASE_DIR / "worktrees"
V2_ROLLOUT_PERCENTAGE = 100  # 100% = V2 only
V2_MAX_PARALLEL_TASKS = 5
```

## 📊 Monitoring

```bash
# Circuit breaker status
python services/circuit_breaker.py status

# Battle report
python tools/battle_report.py

# Cleanup old tasks
python tools/cleanup_old_tasks.py --dry-run
```

## 🗂️ Skills

Skills are markdown files in `.agent/skills/{name}/SKILL.md`:

- **prd-standard-uz** — Uzbekistan PRD template
- **uz-procurement-analyzer** — Xarid.uz analysis  
- **vertex-batch-operator** — Batch predictions

Agents discover skills automatically via `generate_with_skills()`.

## 🔒 Safety Features

1. **Circuit Breaker** — Opens after 5 Vertex AI failures
2. **Heartbeat** — Agents write to META.yml every 10s
3. **Monitor** — Boss kills stale agents after 30s
4. **Cleanup** — Cron removes tasks older than 7 days

## 📈 Metrics

- Tasks per hour
- Success rate (%)
- Avg duration (seconds)
- Total XP earned
- Vertex AI latency
