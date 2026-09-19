# SentinelFlow Demo Platform

> **This is not a real product.** It is a purpose-built, synthetic multi-service
> codebase that serves as the live-demo GitHub data source for
> [SentinelFlow](https://github.com/) release intelligence evaluation.

SentinelFlow's GitHub MCP client (readonly) reads pull requests from this
repository. SentinelFlow's own MCP server analyzes those changes using
deterministic tools — `grimp` for blast radius, `oasdiff` for contract breaks,
`gitleaks` for secrets — and produces PASS / REVIEW / BLOCK verdicts.

See [`SENTINELFLOW_CONTEXT.md`](SENTINELFLOW_CONTEXT.md) for how this repo
connects to the main SentinelFlow project plan.

## What's inside

| Component | Purpose |
|-----------|---------|
| `services/` | Six Python microservices with real cross-import dependencies |
| `contracts/` | OpenAPI 3.1 contract per service |
| `tests/` | Pytest suite for regression selection |
| `eval/pr-ground-truth.yaml` | Labeled expected verdicts for 18 demo PRs |
| `service-catalog.yaml` | Service metadata mirroring SentinelFlow domain packs |

### Services

**Healthcare claims domain**

- `svc-core-api` (critical) — claim intake; imports notification + analytics
- `svc-notification` (high) — async dispatch
- `svc-analytics` (medium) — event ingestion

**E-commerce payments domain**

- `svc-payment-api` (critical) — checkout; imports inventory + order-events
- `svc-inventory` (high) — stock reservation
- `svc-order-events` (medium) — lifecycle event publishing

## Ground-truth PR scenarios

18 branches under `pr/*` cover the eval matrix:

| Verdict | Count | Examples |
|---------|-------|----------|
| PASS | 6 | docs-only, logging with tests, config comments |
| BLOCK | 6 | breaking OpenAPI on critical services, synthetic secrets |
| REVIEW | 6 | logic changes without tests, cross-service schema drift |

Full labels and reasoning: [`eval/pr-ground-truth.yaml`](eval/pr-ground-truth.yaml).

## Local development

```bash
python -m venv .venv
.venv\Scripts\activate        # Windows
pip install -e ".[dev]"
pytest
```

## Publishing to GitHub

After creating a new public repo on GitHub:

```powershell
git remote add origin https://github.com/YOUR_USER/sentinelflow-demo-platform.git
git push -u origin main
git push origin "pr/*"
.\scripts\create_demo_prs.ps1
```

Then update `pr_number` fields in `eval/pr-ground-truth.yaml` with the assigned
GitHub PR numbers.

## Synthetic secrets warning

Several demo branches contain **obviously fake** credentials (AWS keys, ghp
tokens, RSA private keys) labeled `SYNTHETIC SECRET FOR SENTINELFLOW EVAL`.
These exist solely so gitleaks can demonstrate BLOCK verdicts. Do not reuse
these patterns in real projects.

## License

Synthetic demo data — use freely for SentinelFlow evaluation and portfolio demos.
