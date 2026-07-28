# ADR-006: LangGraph as the Agent Orchestration Runtime

- Status: Accepted
- Decision date: Initial architecture baseline
- Owners: Platform Architecture and AI Platform teams

## Context

The platform requires a stateful multi-agent runtime supporting:

- One Supervisor Agent.
- Exactly three specialized sub-agents.
- Conditional routing.
- Parallel execution.
- Durable state.
- Bounded retry.
- Reflection.
- Human interruption and resume.
- Execution tracing.
- Long-running workflows.

A basic stateless agent loop is not sufficient because the platform must
support controlled, auditable, resumable workflows.

## Decision

LangGraph is the approved orchestration runtime for the AI-agent system.

LangGraph is responsible for:

- Graph state.
- Supervisor routing.
- Specialized sub-agent execution.
- Conditional edges.
- Parallel and sequential execution.
- Reflection loops.
- Bounded retries.
- Human-in-the-loop interruption.
- Durable checkpointing.
- Resume after interruption or service restart.
- Execution metadata.

The logical graph is:

```text
START
  ↓
Load authenticated context
  ↓
Supervisor
  ├── Structured Data Agent
  ├── Unstructured Data / RAG Agent
  └── Analytics Agent
  ↓
Merge results
  ↓
Reflection
  ├── Pass
  ├── Bounded retry
  └── Human review
  ↓
Final response
  ↓
Persist memory and audit
  ↓
END
