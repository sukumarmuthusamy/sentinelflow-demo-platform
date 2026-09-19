# Inventory Service Guide

Operational guide for `svc-inventory` reservation workflows.

## Reservation flow

1. Payment API calls `reserve_stock()` during checkout.
2. Stock is decremented atomically in the in-memory ledger.
3. Insufficient stock returns HTTP 409 equivalent status.

This is synthetic documentation for SentinelFlow demo purposes.
