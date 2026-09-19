# SentinelFlow Context

This repository exists to answer **open question #3** in
[`SENTINELFLOW_PLAN.md`](../sentinelflow-release-intelligence/SENTINELFLOW_PLAN.md)
(section 15):

> Which live GitHub repository backs the demo's live mode. It needs real pull
> requests with API contract changes to be interesting; a purpose-built public
> repo with seeded PRs may serve better than a third-party project.

## MCP boundary (section 6)

SentinelFlow's live change data comes from the **GitHub official MCP server**
(readonly toolset). This repo is the synthetic codebase that server reads when
analyzing demo pull requests. SentinelFlow's own MCP server (`sentinelflow-context`)
provides the dependency graph, contract diffs, security scans, and policy gate —
not raw GitHub data.

## Domain alignment

Service names and structure mirror SentinelFlow domain packs:

- `domains/healthcare-claims` → svc-core-api, svc-notification, svc-analytics
- `domains/ecommerce-payments` → svc-payment-api, svc-inventory, svc-order-events

Ground-truth labels in `eval/pr-ground-truth.yaml` align with fixture scenarios
(CHG-H001–H004, CHG-E001–E004) from those packs.
