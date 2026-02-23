# Jira ticket – copy into Jira

Use this when creating the issue in Jira (Create issue → paste below).

---

## Summary
App Status, Maintenance Mode & Health Check APIs – Implementation & Hardening

## Type
Story

## Description

Implement and harden app-level status, maintenance mode, and health check APIs so that:

- Load balancers and probes can check health with clear failure reasons.
- Operators can put the app in maintenance (all APIs return 503) and toggle/reset data-ingestion status.
- Toggle/reset actions are debounced (Redis + in-memory fallback), audit-logged, and documented in Swagger.

---

## Acceptance Criteria

- **Health (GET `/app-health-status`)**
  - Returns 200 when server is healthy (not in maintenance, DB reachable).
  - Returns 503 with `data.reasons` (e.g. `maintenance`, `database_unavailable`) and `data.detail` when unhealthy.

- **Maintenance status (GET `/app-maintenance-status`)**
  - Returns 503 when maintenance is ON; 200 with `data.is_maintenance: false` when OFF.

- **Toggle maintenance (POST `/toggle-app-maintenance-status`)**
  - Flips maintenance flag. When ON, all API requests return 503 via MaintenanceMiddleware.
  - Debounced 2s (429 if too soon). Action audit-logged with user_id.

- **Data ingestion status (GET `/app-data-ingestion-status`)**
  - Returns whether a data ingestion run is in progress (`data.app_data_ingestion_status`).

- **Toggle data ingestion (POST `/toggle-app-data-ingestion-status`)**
  - Flips data-ingestion flag only (does not start/stop job). Debounced 2s. Audit-logged.

- **Reset data ingestion (PUT `/reset-app-data-ingestion-status`)**
  - Forces data-ingestion flag to OFF (manual correction after crashed job). Idempotent. Debounced 2s. Audit-logged.

- **Maintenance middleware** enabled so that when maintenance is ON, every API request returns 503.

- **EXCLUDED_API** includes all six app-status paths so probes/toggles can run without tenant auth as needed.

- **OpenAPI (Swagger)** has tag "App Status" and each endpoint has summary + description.

- **Debounce** uses Redis when available (multi-instance safe); in-memory fallback when Redis is down.

- **Tests** in `backend/tests/test_health.py` cover all six endpoints.

- **Redis flag parsing** – Flag values from Redis (e.g. string `"False"`) are normalized to boolean so toggle state is correct when read from cache (avoids back-to-back toggle bug).

- **Health 503 payload** – `HealthCheckStatusException` accepts optional `message` and `data`; unhealthy response includes `data.reasons` and `data.detail` in the JSON body.

- **Debounce 429** – When toggle/reset is called within 2s of previous call for same flag, API returns 429 with message to wait, and current status in `data` so client stays in sync.

- **DB schema** – `bp_app_status_master.is_active` is BOOLEAN (migration from SMALLINT); all queries use `is_active = TRUE`. Migration script: `backend/migrations/bp_app_status_master_is_active_boolean.sql`.

- **Audit logging** – Toggle and reset actions log `[AUDIT]` with user_id and previous/new status (or "reset to OFF") for traceability.

---

## Technical Details

| Item | Detail |
|------|--------|
| **Base path** | `/base-pricing/api/v1` |
| **Endpoints** | GET app-health-status, GET app-maintenance-status, POST toggle-app-maintenance-status, GET app-data-ingestion-status, POST toggle-app-data-ingestion-status, PUT reset-app-data-ingestion-status |
| **DB** | `base_pricing.bp_app_status_master` (flags: `app_maintenance`, `app_data_ingestion`); `is_active` as BOOLEAN |
| **Redis** | Flags cached under namespace `app_status`; debounce keys `app_status:debounce:app_maintenance`, `app_status:debounce:app_data_ingestion` (TTL 2s) |
| **Files** | `app/routes/app_status_endpoints.py`, `app/services/app_status_service.py` (incl. `_redis_value_to_bool`), `app/core/exceptions.py` (HealthCheckStatusException), `app/extensions/middleware/maintenance.py`, `app/extensions/setup_middlewares.py`, `app/extensions/middleware/constants.py`, `backend/tests/test_health.py`, `backend/migrations/bp_app_status_master_is_active_boolean.sql`, Postman BaseSmart collection |

---

## Out of Scope (optional follow-ups)

- Auth/role restriction on toggle and reset APIs.
- Persisting audit log to a DB table (currently log-only with `[AUDIT]`).

---

## Labels / Components

- **Labels:** `backend`, `api`, `operational-tooling` (or `reliability`)
- **Components:** PriceSmart-BasePricing
- **Project:** MTP

---

## Link to Confluence / README (optional)

- App status and health: see `readme.md` (or link to internal doc) for usage and runbook.
