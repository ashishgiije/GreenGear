# Source Audit — GreenGear

Reviewed 4 November 2026 against source commit `7b63f5f6685ffb6f234c50cba93627238b7bed62`. This is a focused code/documentation review and selected local validation, not a penetration test or an exhaustive vulnerability scan. Application files and credentials were not changed. Secret values are intentionally omitted.

## Severity summary

| Critical | High | Medium | Low |
|---:|---:|---:|---:|
| 0 | 3 | 3 | 1 |

Critical: direct resource/identity boundary failure. High: serious exposure or a core reproducibility blocker. Medium: correctness, validation, or deployment issue. Low: maintenance or coverage gap. Static findings describe potential impact; only explicitly listed runtime checks were executed.

## Findings

### 1. High — A signing key is hardcoded and DEBUG is enabled

- **Affected file:** [greengear_project/settings.py](<greengear_project/settings.py>)
- **Evidence:** A signing key is hardcoded and DEBUG is enabled.
- **Potential impact:** Public deployment can expose debug details and uses a publicly known application secret.
- **Recommended correction:** Load a private secret and environment-specific debug configuration in a separate code change.

### 2. High — update_booking_status changes state without requiring POST

- **Affected file:** [bookings/views.py](<bookings/views.py>)
- **Evidence:** update_booking_status changes state without requiring POST.
- **Potential impact:** A browser GET can change a booking and bypass the intended CSRF-protected form pattern.
- **Recommended correction:** Use POST-only status transitions with CSRF validation and allowed transition checks.

### 3. Medium — Duration is converted using int before the create exception handler and is not constrained to positive values

- **Affected file:** [bookings/views.py](<bookings/views.py>)
- **Evidence:** Duration is converted using int before the create exception handler and is not constrained to positive values.
- **Potential impact:** Invalid input can produce server errors or nonsensical prices.
- **Recommended correction:** Validate dates, positive duration, and duration type with a Django form.

### 4. Medium — Administrative views reference equipment/manage_all

- **Affected file:** [equipment/views.py](<equipment/views.py>)
- **Evidence:** Administrative views reference equipment/manage_all.html, admin_edit.html, and admin_delete.html, which are absent.
- **Potential impact:** Those paths can fail with TemplateDoesNotExist.
- **Recommended correction:** Supply the missing templates or remove the unreachable UI paths in a separate fix.

### 5. Medium — An application database is committed

- **Affected file:** [db.sqlite3](<db.sqlite3>)
- **Evidence:** An application database is committed.
- **Potential impact:** Account hashes and user/business data may be redistributed with the project.
- **Recommended correction:** Review contents privately and replace tracked runtime data with safe fixtures.

### 6. Low — App test modules contain scaffold content rather than meaningful regression tests

- **Affected file:** [users/tests.py](<users/tests.py>)
- **Evidence:** App test modules contain scaffold content rather than meaningful regression tests.
- **Potential impact:** Permissions and booking transitions lack automated coverage.
- **Recommended correction:** Add role, ownership, pricing, and conflicting-booking tests.

### 7. High — dj_database_url

- **Affected file:** [greengear_project/settings.py](<greengear_project/settings.py>)
- **Evidence:** dj_database_url.config uses ssl_require=True even for SQLite, injecting an sslmode option rejected by sqlite3.
- **Potential impact:** The documented default local database cannot connect; migrate and homepage access fail without an override.
- **Recommended correction:** Apply SSL options only to supported network database engines; until fixed, use an external development settings module to remove the SQLite-only invalid option.

## Validation evidence

Django system check passed; default SQLite migrations failed because ssl_require=True injects unsupported sslmode. With an external settings module removing SQLite sslmode, migrations and an HTTP 200 homepage/content check passed. The test runner found zero tests.

## Review scope and limits

Reviewed tracked application source, entry points, manifests/configuration, routes and data models where present, existing documentation, and available test definitions. Generated dependencies and binary artifacts were inventoried rather than treated as authored application logic. Provider calls, cloud deployment, and external data/model claims remain unverified unless explicitly listed above. No secret was rotated and no migration was run against a user database.

## Priorities

Address Critical and High findings before public deployment. Then add regression tests for the affected boundary or workflow, fix Medium issues, and resolve Low maintenance findings. All application corrections require a separate reviewed coding change.
