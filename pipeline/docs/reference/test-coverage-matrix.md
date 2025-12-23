# Test Coverage Matrix

This document maps documented behavior to specific tests, following the Tests-First Documentation approach.

> "Documentation must be grounded in verified behavior. Tests are the primary source of truth."

## Overview

| Category | Test Count | Test Directory |
|----------|------------|----------------|
| Contract Tests | 34 | `tests/contract/` |
| Characterization Tests | 8 | `tests/characterization/` |
| Integration Tests | 40 | `tests/integration/` |
| Unit Tests (Pre-existing) | 132 | `tests/` |
| **Total** | **214** | |

## Contract Tests

Tests that validate public API guarantees.

### Pipeline API Contract

**File:** `tests/contract/test_pipeline_api_contract.py` (17 tests)

| Test | Documents |
|------|-----------|
| `test_pipeline_accepts_empty_steps_list` | Empty steps list is valid |
| `test_pipeline_accepts_single_step` | Single step is valid |
| `test_pipeline_accepts_multiple_serial_steps` | Multiple serial steps valid |
| `test_pipeline_accepts_parallel_step_group` | Parallel groups valid |
| `test_pipeline_accepts_mixed_serial_and_parallel_steps` | Mixed patterns valid |
| `test_pipeline_accepts_none_config_uses_defaults` | Default config behavior |
| `test_pipeline_accepts_custom_config` | Custom config accepted |
| `test_pipeline_accepts_none_progress_callback` | No callback is valid |
| `test_pipeline_accepts_progress_callback_function` | Callback signature |
| `test_run_accepts_pipeline_context` | run() accepts context |
| `test_run_returns_pipeline_context` | run() returns context |
| `test_run_returns_modified_context_with_results` | Results are populated |
| `test_run_preserves_original_context_fields` | Original fields preserved |
| `test_create_factory_method_exists` | Factory method exists |
| `test_create_accepts_steps_and_config` | Factory parameters |
| `test_create_returns_pipeline_instance` | Factory returns Pipeline |
| `test_create_pipeline_is_functional` | Factory creates working pipeline |

### PipelineStep Interface Contract

**File:** `tests/contract/test_pipelinestep_interface_contract.py` (17 tests)

| Test | Documents |
|------|-----------|
| `test_pipelinestep_is_abstract_base_class` | ABC nature |
| `test_pipelinestep_cannot_be_instantiated_directly` | Cannot instantiate |
| `test_pipelinestep_requires_step_id_implementation` | step_id required |
| `test_pipelinestep_requires_description_implementation` | description required |
| `test_pipelinestep_requires_run_implementation` | run() required |
| `test_step_id_returns_string` | step_id returns str |
| `test_description_returns_string` | description returns str |
| `test_run_accepts_pipeline_context` | run() signature |
| `test_run_returns_pipeline_context` | run() return type |
| `test_timeout_default_is_none` | Default timeout |
| `test_retries_default_is_zero` | Default retries |
| `test_critical_default_is_true` | Default critical |
| `test_timeout_can_be_overridden` | Override timeout |
| `test_retries_can_be_overridden` | Override retries |
| `test_critical_can_be_overridden` | Override critical |
| `test_complete_implementation_can_be_instantiated` | Full implementation |
| `test_complete_implementation_is_functional` | Implementation works |

## Characterization Tests

Tests that freeze current behavior where correctness is unknown.

### Step Timeout NOT Enforced

**File:** `tests/characterization/test_characterization__step_timeout_not_enforced.py` (4 tests)

| Test | Documents |
|------|-----------|
| `test_characterization__step_timeout_property_exists` | Property exists |
| `test_characterization__step_timeout_not_enforced_in_serial_execution` | Not enforced serial |
| `test_characterization__multiple_steps_with_timeout_not_enforced` | Not enforced multiple |
| `test_characterization__step_timeout_none_works_as_expected` | None timeout works |

### Step Retry NOT Enforced

**File:** `tests/characterization/test_characterization__step_retry_not_enforced.py` (4 tests)

| Test | Documents |
|------|-----------|
| `test_characterization__step_retries_property_exists` | Property exists |
| `test_characterization__step_retries_not_enforced_critical_step` | Not enforced critical |
| `test_characterization__step_retries_not_enforced_non_critical_step` | Not enforced non-critical |
| `test_characterization__step_retries_zero_default_works` | Zero default works |

## Integration Tests

Tests that validate end-to-end workflows.

### Execution Flows

**File:** `tests/integration/test_execution_flows.py` (7 tests)

| Test | Documents |
|------|-----------|
| `test_serial_execution_runs_steps_in_order` | Serial order |
| `test_serial_execution_context_flows_between_steps` | Context flow |
| `test_empty_pipeline_returns_unmodified_context` | Empty pipeline |
| `test_parallel_and_all_steps_succeed` | AND logic success |
| `test_parallel_and_fails_when_one_step_fails` | AND logic failure |
| `test_parallel_or_succeeds_when_all_steps_succeed` | OR all succeed |
| `test_parallel_or_succeeds_when_one_step_succeeds` | OR one succeeds |

### Context Merging

**File:** `tests/integration/test_context_merging.py` (3 tests)

| Test | Documents |
|------|-----------|
| `test_parallel_steps_merge_lists` | List concatenation |
| `test_parallel_steps_sum_numeric_increments` | Numeric summation |
| `test_parallel_steps_merge_dicts_shallowly` | Dict shallow merge |

### Error Handling

**File:** `tests/integration/test_error_handling.py` (6 tests)

| Test | Documents |
|------|-----------|
| `test_fail_fast_stops_on_first_critical_error` | Fail-fast critical |
| `test_fail_fast_continues_on_non_critical_error` | Fail-fast non-critical |
| `test_fail_slow_accumulates_all_errors` | Fail-slow accumulation |
| `test_fail_slow_continues_even_on_critical_error` | Fail-slow critical |
| `test_multiple_non_critical_failures_all_recorded` | Multiple failures |
| `test_successful_steps_after_non_critical_failures` | Success after failure |

### Progress Tracking

**File:** `tests/integration/test_progress_tracking.py` (7 tests)

| Test | Documents |
|------|-----------|
| `test_progress_callback_invoked_for_each_step` | Callback invocation |
| `test_progress_callback_receives_increasing_progress` | Progress increases |
| `test_progress_callback_reaches_100_percent` | Reaches 100% |
| `test_progress_callback_with_parallel_steps` | Parallel progress |
| `test_pipeline_works_without_progress_callback` | No callback ok |
| `test_pipeline_with_none_callback_explicit` | Explicit None ok |
| `test_progress_with_mixed_serial_and_parallel` | Mixed progress |

### Advanced Scenarios

**File:** `tests/integration/test_advanced_scenarios.py` (7 tests)

| Test | Documents |
|------|-----------|
| `test_parallel_group_timeout_enforced` | Group timeout works |
| `test_parallel_group_completes_within_timeout` | Within timeout ok |
| `test_parallel_steps_have_isolated_contexts` | Context isolation |
| `test_serial_then_parallel_then_serial` | Mixed execution |
| `test_multiple_parallel_groups_in_sequence` | Sequential groups |
| `test_nested_parallel_not_supported_but_sequential_works` | Nested handling |
| `test_parallel_execution_is_thread_safe` | Thread safety |

### Progress Patterns Verification

**File:** `tests/integration/test_examples_verification.py` (10 tests)

| Test | Documents |
|------|-----------|
| `test_step_can_report_granular_progress` | Granular progress within steps |
| `test_get_status_returns_step_details` | `Pipeline.get_status()` API |
| `test_step_details_include_weight_and_contribution` | Step weights |
| `test_decorator_injects_noop_when_callback_not_provided` | `@with_progress_callback` |
| `test_decorator_uses_provided_callback` | Decorator with callback |
| `test_decorator_works_with_step_update_method` | Decorator with context |
| `test_parallel_steps_each_have_weight` | Parallel step weight distribution |
| `test_parallel_steps_can_report_individual_progress` | Parallel progress |
| `test_get_status_can_be_called_during_execution` | Real-time progress querying |
| `test_is_running_reflects_execution_state` | Pipeline running state |

## Running Tests

```bash
# All tests
uv run pytest tests/ -v

# Contract tests only
uv run pytest tests/contract/ -v

# Characterization tests only
uv run pytest tests/characterization/ -v

# Integration tests only
uv run pytest tests/integration/ -v

# With coverage
uv run pytest tests/ --cov=task_pipeline --cov-report=html
```

