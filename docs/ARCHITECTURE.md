# kube-validator Architecture Guide

This document explains how the codebase is structured after refactoring and how data flows across layers.

## 1) Layered structure

The project now follows a layered pattern similar to mature OSS CLI repos:

- `kubeval/domain/`
  - Pure data model and constants
  - No CLI or shell concerns
- `kubeval/application/`
  - Use-case logic (running checks, matching behavior)
- `kubeval/infrastructure/`
  - Adapters for external systems (kubectl)
- `kubeval/presentation/`
  - Output shaping and rendering (table/json)
- `kubeval/checks/`
  - Check definitions, custom check loading, and policies
- `kubeval/cli.py`
  - Composition root: wires all layers together

## 2) Runtime flow for `scan`

1. Parse args in `kubeval/cli.py`.
2. Create infra adapter `KubectlClient` from `kubeval/infrastructure/kubernetes/kubectl_client.py`.
3. Validate kubectl availability.
4. Load built-in check definitions from `kubeval/checks/builtin/*/check.json`.
5. Optionally append custom checks from `--checks-file` (`kubeval/checks/custom.py`).
6. Execute checks via application service `kubeval/application/checks/runner.py`.
7. Apply result policy `enforce_autoscaling_coverage` (`kubeval/checks/policies.py`).
8. Render output through presentation layer (`kubeval/presentation/console/reporting.py`).
9. Return exit code:
   - `0` all pass
   - `1` fail/error exists
   - `2` setup/input error

## 3) Module map

- `kubeval/domain/models.py`
  - `ResourceCheck`, `CheckResult`, `ResourceRef`
  - `PASS`, `FAIL`, `ERROR`, `VALID_MATCH_TYPES`

- `kubeval/application/checks/runner.py`
  - `matches_name()`
  - `run_resource_check()`
  - `run_checks()`

- `kubeval/infrastructure/kubernetes/kubectl_client.py`
  - `KubectlClient.validate()`
  - `KubectlClient.get_resources()`
  - Isolates subprocess and timeout behavior

- `kubeval/presentation/console/reporting.py`
  - `print_table()`, `print_checks_catalog()`
  - `summarize()`, `to_results_payload()`, `to_checks_payload()`

- `kubeval/checks/builtin/__init__.py`
  - Loads built-in checks from per-check `check.json` files

- `kubeval/checks/custom.py`
  - Validates and loads user-provided checks JSON

- `kubeval/checks/policies.py`
  - Cross-check policy adjustments

## 4) Backward compatibility

To avoid breaking existing imports, these modules remain as compatibility shims:

- `kubeval/models.py` -> re-exports from `kubeval/domain/models.py`
- `kubeval/engine.py` -> re-exports from `kubeval/application/checks/runner.py`
- `kubeval/kubectl.py` -> re-exports from `kubeval/infrastructure/kubernetes/kubectl_client.py`
- `kubeval/reporting.py` -> re-exports from `kubeval/presentation/console/reporting.py`

This keeps old imports working while allowing clean internal layering.

## 5) How to add a built-in check

1. Create a folder under `kubeval/checks/builtin/<check-id>/`.
2. Add `check.json` with required fields:

```json
{
  "id": "aws-load-balancer-controller",
  "title": "AWS Load Balancer Controller installed",
  "resource": "deployment",
  "namespace": "kube-system",
  "match_type": "contains",
  "match_value": "aws-load-balancer-controller",
  "min_count": 1
}
```

3. Register the path in `_BUILTIN_CHECK_FILES` inside `kubeval/checks/builtin/__init__.py`.
4. Validate:
   - `python3 -m kubeval list-checks --output json`

## 6) How to add custom checks

1. Put checks in JSON with top-level `checks` list.
2. Run:
   - `python3 -m kubeval scan --checks-file checks.example.json`

Validation behavior:

- Missing required keys -> user-facing error (exit `2`)
- Invalid `match_type` -> user-facing error (exit `2`)

## 7) Why this structure is maintainable

- Domain logic is isolated from process execution.
- Infrastructure adapter can be replaced/tested independently.
- Presentation is decoupled from check execution.
- CLI remains thin and focused on orchestration.
- Compatibility shims make migration safe for current users.
