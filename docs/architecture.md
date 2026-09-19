# Demo Platform Architecture

This repository is a **synthetic multi-service codebase** used as live-demo data for
[SentinelFlow](https://github.com/) release intelligence evaluation. It is not a production system.

## Domains

Two domain packs are represented in a single monorepo:

| Domain | Services | Critical path |
|--------|----------|---------------|
| healthcare-claims | svc-core-api, svc-notification, svc-analytics | Claims intake → notify → analytics |
| ecommerce-payments | svc-payment-api, svc-inventory, svc-order-events | Checkout → reserve → publish events |

## Dependency graph

```
svc-core-api ──publishes──▶ svc-notification
             └──publishes──▶ svc-analytics

svc-payment-api ──calls────▶ svc-inventory
                └─publishes▶ svc-order-events
```

Python import edges mirror the service catalog in `service-catalog.yaml` so tools like
`grimp` can resolve real cross-service blast radius.

## Contracts

Each service exposes an OpenAPI 3.1 contract under `contracts/`. Breaking changes to
critical services (svc-core-api, svc-payment-api) should trigger SentinelFlow BLOCK verdicts.
