# Vision

## Mission

Build an outcome-oriented AI work orchestrator that converts bounded human or system objectives into governed, auditable, resource-aware execution across interchangeable agents, models, skills, tools, programs, and eventually human operators.

The system is not primarily a multi-agent chat framework and is not limited to software development. Its long-term role is to coordinate computer-mediated work while preserving human authority over consequential outcomes.

## Core Thesis

The orchestrator manages **work**, not agents.

Agents, models, skills, sandboxes, and tools are execution resources. They may improve, disappear, become cheaper, become more expensive, or be replaced entirely. The orchestration layer should become stronger as the ecosystem improves rather than being locked to one vendor, model, or agent runtime.

## Desired Interaction Model

A requester should eventually be able to specify:

- the desired objective,
- success criteria,
- budget constraints,
- risk boundaries,
- time constraints,
- acceptable permissions,
- and required human approval points.

The system should then:

1. propose bounded work,
2. assess value, risk, budget, confidence, and verifiability,
3. route work to appropriate execution resources,
4. isolate execution,
5. collect evidence,
6. verify results independently,
7. recover from failure,
8. control external side effects,
9. present evidence-backed candidate outcomes,
10. preserve human authority for final acceptance where required,
11. learn cautiously from verified history.

## Value Model

The system should optimize expected utility rather than raw model capability.

A future routing decision may consider:

- expected success probability,
- task value,
- financial cost,
- compute cost,
- latency,
- human attention cost,
- security and operational risk,
- reversibility,
- verification difficulty,
- historical reliability,
- available permissions,
- available skills and tools.

The strongest model is not automatically the correct worker. The correct worker is the execution profile with the best expected value under current constraints.

## Human Role

The system exists to reduce unnecessary coordination work and complete the final operational miles of bounded tasks. It is not designed to erase human authority.

Humans remain the ultimate authority for:

- accepting high-level objectives when human acceptance is required,
- authorizing irreversible or constitutionally sensitive effects,
- resolving escalated ambiguity and conflicts,
- changing constitutional policy,
- exercising tightly controlled break-glass authority.

## Security Philosophy

Every worker is treated as potentially fallible, compromised, misconfigured, prompt-injected, or intentionally untrusted.

Safety is therefore based on capability boundaries, sandboxing, scoped credentials, independent verification, auditability, and controlled effects—not on assumptions that a model is obedient, honest, or sufficiently intelligent.

## Verification Philosophy

Worker output is a claim until independently supported.

The system uses a value-driven, evidence-based dynamic verification pipeline that may combine:

- precondition checks,
- intermediate assertions,
- static validation,
- dynamic validation,
- environment and tool diversity,
- semantic and logical validation,
- confidence gating,
- anomaly detection,
- weighted evidence aggregation,
- arbitration and human escalation.

## Recovery Philosophy

Workers are temporary. Runs may fail. Hosts may restart. Providers may disappear.

Work must survive workers.

The authoritative system state therefore lives outside the worker and supports checkpointing, takeover, replay, rewind, reassignment, and audit.

## Learning Philosophy

Raw history does not directly become policy.

Learning must be delayed, evidence-backed, versioned, auditable, and resistant to contamination. Trust may decrease quickly after strong negative evidence and should recover slowly through repeated verified performance.

## Non-Goals for Early Stages

The first implementation will not attempt to:

- support every agent or model,
- autonomously discover unlimited work,
- implement a fully distributed control plane,
- replace human approval for irreversible actions,
- optimize routing with machine learning before sufficient data exists,
- build a universal workflow language,
- treat self-reported model confidence as authoritative,
- provide perfect sandboxing solely through Docker.

## Long-Term Direction

The long-term system may orchestrate:

- coding agents,
- research agents,
- browser and computer-use agents,
- local models,
- frontier API models,
- deterministic programs,
- domain-specific tools,
- external APIs,
- edge or GPU workers,
- human specialists.

The durable asset is the orchestration experience accumulated across:

`work -> execution strategy -> evidence -> cost -> risk -> result -> verified outcome`.
