# Stage 14 — v1.0 Release Candidate and Final Delivery

**Status:** PLANNED — not implementation or release authorization
**Constitutional baseline:** `constitution-v0.1`

## Objective and why this stage exists

Freeze, verify, document and obtain independent Human acceptance for the first
complete Symphony-K delivery. No major feature work begins here.

## In scope

- frozen v1 scope and release-candidate baseline;
- complete install/setup, operator and developer/contributor guides;
- architecture and security review;
- end-to-end acceptance matrix and known limitations;
- migration, backup and restore documentation;
- example governed workflows;
- release notes, version/tag rules and metadata/license audit;
- clean CI/release-candidate validation and final Human v1 acceptance.

## Out of scope

- major new features or post-v1 candidates;
- hiding release blockers as known limitations;
- tagging, publishing or creating a release without a separate explicit Human
  authorization for that remote Effect.

## Architecture boundaries

The candidate is built from Human-accepted stage outputs. Review findings append
corrections through bounded Issues; failed/rejected candidates remain history.
Release publication is separate from candidate acceptance.

## Expected new interfaces and concepts

No new product-domain concept is expected. Release manifest, acceptance matrix,
known-limitations register and reproducibility record are delivery artifacts.
Any discovered architecture change requires an ADR and earlier-stage correction.

## Cross-stage dependencies

Requires completed Stages 0–13 and their accepted evidence. Exit is the v1.0
delivery gate; post-v1 candidates remain non-blocking.

## Security and trust requirements

Independent architecture/security review, reproducible artifacts, immutable
source/evidence references, protected signing/publishing credentials and
explicit Human authorization for release Effects.

## Failure model

Documentation gap, non-reproducible artifact, failing acceptance scenario,
security/constitutional defect, unsupported migration/restore, metadata/license
issue or CI/release gate failure blocks acceptance. Corrections use new commits
and review; no failed candidate is rewritten.

## Milestones

1. Freeze scope, supported environment and candidate baseline.
2. Complete all user/operator/developer and limitation documentation.
3. Run fresh-maintainer installation and governed-workflow drills.
4. Complete architecture, security, metadata and release reviews.
5. Produce/reproduce candidate artifacts and acceptance matrix.
6. Obtain final Human v1 acceptance and reconcile Stage 14.
7. Only under separate explicit authorization, publish tag/release Effects.

## Proposed bounded Issue decomposition

- scope freeze and release checklist;
- install/operator/developer documentation;
- examples and known limitations;
- architecture/security review;
- metadata/license/versioning audit;
- reproducible candidate and acceptance matrix;
- Human acceptance reconciliation;
- separately authorized publication, if requested.

## Validation strategy

Fresh clone/install on each supported environment, complete governed workflow,
backup/restore/migration drill, documentation link and command checks,
architecture/security review, full acceptance matrix, clean CI, artifact/SBOM
reproduction and release credential boundary review.

## Human Exit Review questions

- Can a fresh maintainer install and operate v1 from repository docs alone?
- Are all required governed workflow, recovery and Effect scenarios accepted?
- Are artifacts reproducible and traceable to the candidate source?
- Is any constitutional, security or release blocker unresolved?
- Is publication separately and explicitly authorized?

## Stage Definition of Done

```text
v1.0 Human Acceptance = ACCEPTED
release artifacts reproducible
critical documentation complete
no unresolved release-blocking constitutional/security defect
```

Final delivery means a fresh maintainer can submit and govern bounded
Objectives, use sandboxed interchangeable AgentDrivers, independently verify
Outcomes, recover from bounded failure, control Effects and inspect audit
history from repository documentation alone. Publication remains a separate
authorized Effect.
