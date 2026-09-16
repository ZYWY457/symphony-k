# Stage 13 — Production Hardening and Release Engineering

**Status:** PLANNED — not implementation authorization
**Constitutional baseline:** `constitution-v0.1`

## Objective and why this stage exists

Make the accepted v1 scope installable, supportable, secure, recoverable and
reproducible for its declared deployment model.

## In scope

- packaging/install and environment validation;
- configuration and secret-integration boundary;
- schema upgrade/migration policy;
- backup/restore, crash/restart and upgrade/rollback procedures;
- logging, metrics and tracing;
- security scanning and dependency review;
- CI release gates, artifact/SBOM strategy and reproducible builds;
- performance/resource baselines and appropriate load/stress limits;
- operator runbooks and compatibility policy.

## Out of scope

- unsupported distributed or HA claims;
- major features or late architecture expansion;
- uncontrolled auto-update or secret storage invented outside an ADR;
- publishing the final v1 release.

## Architecture boundaries

Hardening wraps accepted behavior without bypassing domain/application
authority. Deployment assumptions remain explicit. A single-node v1 is valid if
Human accepted; it must not be described as distributed or HA.

## Expected new interfaces and concepts

Configuration schema, environment preflight, migration/backup manifests,
release artifact metadata, SBOM/signing/provenance boundary, compatibility and
support matrix. Cross-cutting packaging, schema and secret decisions require
accepted ADRs.

## Cross-stage dependencies

Requires accepted Stages 1–12. Produces the release-candidate substrate and
operational evidence consumed by Stage 14.

## Security and trust requirements

Reproducible/pinned inputs, least-privilege deployment, secret redaction and
rotation boundary, dependency provenance, scanner findings with explicit
disposition, protected release gates and recoverable data procedures.

## Failure model

Unsupported environment, invalid configuration, failed migration, partial
upgrade, corrupt backup, failed restore, missing secret, scanner finding,
artifact mismatch, resource exhaustion and crash loop all fail visibly with a
documented safe recovery/rollback path.

## Milestones

1. Accept deployment, configuration, compatibility and release ADRs.
2. Implement packaging/install/environment preflight.
3. Implement schema migration, backup/restore and upgrade/rollback.
4. Complete secrets/observability/security/dependency gates.
5. Establish reproducible artifacts/SBOM and performance baselines.
6. Drill runbooks and complete Human operational-readiness review.

## Proposed bounded Issue decomposition

- deployment/release ADRs;
- packaging and environment validation;
- configuration and secret integration;
- migration and compatibility policy;
- backup/restore and upgrade/rollback;
- observability and security gates;
- reproducible build/SBOM;
- performance/crash durability;
- runbook drills and stage reconciliation.

## Validation strategy

Fresh-environment installs, invalid-environment negatives, forward migration and
rollback, backup/restore verification, crash/restart durability, secret leakage
checks, scanners/dependency audit, reproducible build comparison, resource/load
baselines and operator runbook drills.

## Human Exit Review questions

- Are deployment scope, supported environments and limits stated honestly?
- Can installation, backup, restore, upgrade and rollback be reproduced?
- Are secrets and release credentials outside Worker authority?
- Are security/dependency findings resolved or explicitly accepted?
- Do artifacts, SBOM and source inputs have traceable provenance?

## Stage Definition of Done

The declared v1 deployment is installable, observable, secure within accepted
scope, recoverable and reproducibly releasable; no production-readiness blocker
remains. Human Exit reconciliation precedes Stage 14.
