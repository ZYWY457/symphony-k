# Stage 1 Correction M7D1B — Creation Event Provenance Annotations

**Version:** 1
**Status:** Completed; cumulative corrected M7D1 protocol HUMAN ACCEPTED
**TaskSpec:** [GitHub Issue #65](https://github.com/ZYWY457/symphony-k/issues/65)
**TaskSpec access mode:** `materialized-handoff`
**Starting baseline:** `c4e634c44fe9fab935bc1a4ff02cc53e67e8552c`
(`fix(domain): close creation protocol binding gaps`)

## Scope

This is the final bounded M7D1 correction and closure pass before independent
Human Review. It removes the Issue #64 empty-only annotation regression, audits
the complete shared creation protocol against Issues #62, #63, and #64, and
completes direct deterministic regression proof for that frozen common
architecture.

This correction does not implement Objective, Task, Run, Outcome, Evaluation,
or Effect creation semantics. It introduces no repository, persistence,
currentness, uniqueness, transaction, or atomic-insert behavior from M8. It
does not alter the accepted non-creation lifecycle path.

## Annotation Regression

Issue #62 froze one canonical creation lifecycle event per successful edge and
explicitly allowed narrow stable metadata/reference annotations for creation
authority, availability, relationship observations, semantic evidence, Effect
observations, governance findings, incidents, deduplication, and quarantine
context. Large evidence bodies and arbitrary free-form metadata were excluded,
but a blanket empty annotation set was not required.

Issue #64 subsequently made `CreationResult` require:

```text
event.metadata.annotations == frozenset()
```

That empty-only rule contradicted Issue #62 because it rejected every otherwise
exact creation event carrying the stable provenance references that later
entity-specific creation slices must emit. This correction removes only that
blanket equality check.

The corrected common event contract still exact-binds:

```text
request event ID
canonical event type and entity family
request entity ID
EntityVersion(1)
authorized decision actor
request timestamp
request correlation and causation IDs
request reason
prior_state = None
new_state = the request variant's canonical target
```

Exactly one event remains paired with exactly one initial snapshot. No event
collection or fake source state/version is introduced.

## Annotation Responsibility Boundary

M7D1 owns structural annotation capability. `DomainEventMetadata` continues to
require:

```text
an immutable frozenset
members shaped exactly as (key, value)
string keys and values
non-whitespace keys and values
unique keys
```

M7D1 does not treat structurally valid annotations as authority, uniqueness,
relationship truth, currentness, execution permission, or Effect governance
status. It adds no `Any`, mutable dictionary, arbitrary object bag, opaque JSON
metadata, or large evidence body.

M7D2–M7D5 own the exact canonical annotation vocabulary and semantic values for
their successful entity-specific edges. Structural compatibility in M7D1 is
therefore necessary but never sufficient for semantic authorization.

## Preserved M7D1A Corrections

The Issue #64 fixes remain intact:

- all eight immutable request variants fix their exact entity family and
  canonical target;
- typed `entity_spec` and typed `semantic_input` remain part of the immutable
  normalized scope;
- `CreationResult` exact-binds every family-specific immutable snapshot field;
- a new PROPOSED Outcome rejects fabricated `superseded_by_outcome_id` lineage;
- a PENDING Evaluation cannot contain a result;
- requester, Outcome producer, planned Effect proposer, and observed Effect
  observer cannot acquire authority by retaining an `ActorId` while relabeling
  only `ActorType`;
- the relabel defense is not a blanket principal-inequality rule;
- `SYSTEM` is not a superuser, actor eligibility is not a grant, and only an
  exact-scoped AUTHORIZED decision can proceed;
- identifier availability remains typed, exact-scoped pre-M8 evidence and must
  be AVAILABLE; and
- `EntityVersion(1)` remains the only creation result/event version while
  version 0 remains neither absence nor a creation input.

## Bounded M7D1 Closure Audit

The current shared protocol was audited against Issues #62–#64 for:

```text
the eight closed request variants and request-field restrictions
variant/family/target/spec/semantic-input binding
immutable normalized request scope
authority status, eligibility, exact scope, and principal identity
availability status, provenance, scope, type, ID, and correlation
version-1 and NONE-as-absence semantics
CreationResult snapshot and event exact binding
DomainEvent prior_state=None creation-target restriction
annotation structural compatibility
the separate fail-closed create_entity() boundary
transition_entity() isolation and accepted non-creation behavior
absence of repository/persistence or entity-specific semantics
```

No further source-level contradiction was found inside the frozen M7D1 shared
architecture. The only implementation discrepancy was the empty-only
annotation rule, which this correction removes.

The closure audit did find missing direct, isolated regression proof in the
dedicated creation suite. This correction adds that proof without changing the
architecture or introducing entity-specific semantics. Coverage now includes:

- all eight variant/family/target mappings and absence of source, prior,
  expected-version, and caller-selected initial-version request fields;
- canonical version 1 plus version 0/non-1, family, ID, state, immutable spec,
  Outcome lineage, and Evaluation result-injection rejection;
- isolated event ID, entity ID, authority actor, correlation, causation,
  reason, event type, prior-state, and new-state/creation-target defenses;
- acceptance of structurally valid nonempty stable-reference annotations and
  rejection of malformed, blank-key, blank-value, and duplicate-key forms;
- denied/unresolved/ineligible/SYSTEM authority, exact-scope substitution,
  all four principal-relabel surfaces, and legitimate exact-identity behavior;
- missing, duplicate, unresolved, scope-substituted, wrong-type, wrong-ID,
  wrong-correlation, Boolean, and requester-self-attested availability; and
- fail-closed public creation plus representative transition-path isolation.

## Fail-Closed and Completion Boundary

`create_entity()` continues to perform common request, authority, availability,
and additional-guard checks and then raises `InvariantViolation` because no
M7D2–M7D5 canonical semantic validator exists. Structurally valid annotations
cannot bypass this denial. No authoritative entity snapshot or success event is
created by the public M7D1 boundary.

Accepted lifecycle coverage remains:

```text
non-creation accepted = 91 / 91
creation accepted     = 0 / 8
integrated accepted   = 91 / 99
```

At this correction's candidate boundary, no creation edge was Human Accepted
and one direct event-version regression proof still remained. Issue #66 added
that proof without changing production behavior. Independent Human Review then
accepted the cumulative M7D1 shared authoritative creation protocol at commit
`e18b22aa26514b08b6faa0ea7ab251d356b7d48f`.

That cumulative acceptance accepts no creation edge. The lifecycle counts above
remain unchanged. M7 and Stage 1 remain incomplete, and M7D2 Objective + Task is
the next implementation slice.

## Validation and Commit Boundary

The candidate must pass the focused creation-protocol suite and all locked
repository gates from Issue #65. Only the three explicitly authorized files
may be staged. The resulting work is one local forward commit named:

```text
fix(domain): preserve creation event provenance annotations
```

No remote repository state is authorized to change.
