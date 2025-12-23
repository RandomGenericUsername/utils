# Partial Failures Reference

## Purpose

Documents the partial failure semantics of dotfiles-package-manager. This behavior is intentional and used in production pipelines.

---

## Verified Behavior

**When installing multiple packages, `success=True` if ANY package succeeds.**

This is a **characterization** of current behavior, verified by tests and used in production.

---

## Evidence

**Test File**: `tests/characterization/test_characterization__partial_install_success.py`

**Number of Tests**: 15 (3 tests × 5 package managers)

**Source Implementation**: Each package manager's `install()` method tracks individual package results.

---

## Behavior Matrix

| Scenario | Result | Evidence |
|----------|--------|----------|
| All packages succeed | `success=True` | `test_all_packages_succeed_returns_success_true` |
| Some packages succeed, some fail | `success=True` | `test_partial_install_returns_success_true` |
| All packages fail | `success=False` | `test_total_install_failure_returns_success_false` |
| Empty package list | `success=True` | `test_install_empty_list_returns_success` |

---

## Example

```python
result = pm.install(["vim", "nonexistent-package", "git"])

# Partial success scenario
result.success              # True (vim and git succeeded)
result.packages_installed   # ["vim", "git"]
result.packages_failed      # ["nonexistent-package"]
```

---

## Rationale

This behavior is intentional for **pipeline-based workflows**. From production usage in `dotfiles-installer`:

1. **Install required packages** → Log failures but continue
2. **Install optional packages** → Don't fail if optional packages fail
3. **Track what succeeded** → Report at end of pipeline

```python
# Production pattern from dotfiles-installer
result = pm.install(required_packages)
for pkg in result.packages_failed:
    pipeline.log_failure(pkg)
# Continue with next step regardless of partial failures
```

---

## Cross-Manager Consistency

This behavior is **guaranteed identical** across all 5 package managers:

| Manager | Behavior Verified |
|---------|------------------|
| `PacmanPackageManager` | ✅ 15 tests pass |
| `YayPackageManager` | ✅ 15 tests pass |
| `ParuPackageManager` | ✅ 15 tests pass |
| `AptPackageManager` | ✅ 15 tests pass |
| `DnfPackageManager` | ✅ 15 tests pass |

**Evidence**: Parametrized tests in `tests/characterization/test_characterization__partial_install_success.py` run against all 5 managers.

---

## Checking Individual Results

Always check `packages_installed` and `packages_failed` for detailed status:

```python
result = pm.install(["vim", "git", "nonexistent"])

# Don't just check success
if result.success:
    # This means AT LEAST ONE succeeded
    pass

# Check individual results
for pkg in result.packages_installed:
    print(f"✓ {pkg}")

for pkg in result.packages_failed:
    print(f"✗ {pkg}")
    # Handle the failure
```

---

## Applies To

This behavior applies to:

| Method | Partial Failure Semantics |
|--------|--------------------------|
| `install()` | ✅ Yes - `success=True` if any succeed |
| `remove()` | ✅ Yes - `success=True` if any succeed |
| `update_system()` | N/A - Single operation |

---

## Related Documentation

- [Empty Lists Reference](EmptyLists.md)
- [Exception Propagation Reference](ExceptionPropagation.md)
- [Error Handling Guide](../guides/ErrorHandling.md)

