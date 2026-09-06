# Trust Model

## Principle

Workers are untrusted. Claims are not evidence.

The system MUST remain safe and auditable even if a worker is mistaken, hallucinating, prompt-injected, compromised, misconfigured, or intentionally adversarial.

## Trust Hierarchy

Evidence is not equally authoritative. A default trust ordering is:

1. explicit human authorization within constitutional bounds,
2. constitutional and active system policy,
3. deterministic independently collected evidence,
4. trusted external receipts or state observations,
5. independent specialist verification,
6. calibrated semantic/LLM evaluation,
7. worker self-report.

The ordering is contextual. Human judgment can be wrong, validators can fail, and external systems can be inconsistent. The purpose is to prevent low-grade claims from silently becoming high-authority facts.

## Claims

Examples of claims:

- `The tests passed.`
- `The payment was created.`
- `The requirement is satisfied.`
- `The file was uploaded.`
- `I am 95% confident.`

A claim MUST NOT be treated as authoritative until supported by appropriate evidence.

## Evidence

Evidence should be independently collected when practical.

Examples:

- test process exit code and output,
- file content hash,
- git commit hash,
- schema validation result,
- external API receipt,
- database state read through an independent path,
- integration test result from a fresh environment,
- browser observation,
- security scanner output.

Evidence artifacts SHOULD be content-addressed or anchored by immutable identifiers where practical.

## Facts, Judgments, Policies

### Facts

Append-only historical truth about observed events or artifacts.

Normal flows MUST NOT rewrite facts.

### Judgments

Interpretations derived from facts and evidence.

Judgments MAY be superseded or overridden, but the original record remains.

### Policies

Rules governing what the system is allowed or expected to do.

Policies MAY be versioned, changed, waived, or rolled back by authorized governance.

## Human Authority

Human authority is high but not magical.

Humans MAY:

- override a judgment,
- authorize a sensitive effect,
- grant a scoped policy waiver,
- redirect a Task,
- accept or reject an Objective.

Humans MUST NOT, through normal operation:

- erase an audit record,
- rewrite an already observed external Effect as if it never occurred,
- falsify evidence provenance,
- cause a worker to become its own validator,
- bypass constitutional invariants without a constitutional amendment.

## Break Glass

Emergency authority MAY exist as a special mechanism.

Break-glass use requires:

- strong authentication,
- explicit reason,
- narrow scope,
- short expiration,
- high-severity audit event,
- post-event review.

Break glass does not authorize rewriting historical facts.
