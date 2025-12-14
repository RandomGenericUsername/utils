"""Integration tests for end-to-end pipeline execution."""

import pytest

from pipeline import (
    LogicOperator,
    ParallelConfig,
    Pipeline,
    PipelineConfig,
)


class TestPipelineBasics:
    """Test suite for basic Pipeline functionality."""

    def test_pipeline_can_be_instantiated(self):
        """Test that Pipeline can be instantiated."""
        # Arrange
        from .conftest import SimpleStep

        steps = [SimpleStep("step1", "key", "value")]

        # Act
        pipeline = Pipeline(steps)

        # Assert
        assert pipeline is not None
        assert isinstance(pipeline, Pipeline)

    def test_pipeline_with_config(self):
        """Test creating pipeline with configuration."""
        # Arrange
        from .conftest import SimpleStep

        steps = [SimpleStep("step1", "key", "value")]
        config = PipelineConfig(fail_fast=False)

        # Act
        pipeline = Pipeline(steps, config)

        # Assert
        assert pipeline.config == config
        assert pipeline.config.fail_fast is False

    def test_pipeline_create_factory_method(self):
        """Test Pipeline.create factory method."""
        # Arrange
        from .conftest import SimpleStep

        steps = [SimpleStep("step1", "key", "value")]

        # Act
        pipeline = Pipeline.create(steps)

        # Assert
        assert isinstance(pipeline, Pipeline)

    def test_pipeline_has_run_method(self):
        """Test that Pipeline has run method."""
        # Arrange
        from .conftest import SimpleStep

        pipeline = Pipeline([SimpleStep("step1", "key", "value")])

        # Assert
        assert hasattr(pipeline, "run")
        assert callable(pipeline.run)


class TestPipelineSerialExecution:
    """Test suite for serial pipeline execution."""

    def test_execute_single_step(self, pipeline_context):
        """Test executing pipeline with single step."""
        # Arrange
        from .conftest import SimpleStep

        steps = [SimpleStep("step1", "key1", "value1")]
        pipeline = Pipeline(steps)

        # Act
        result = pipeline.run(pipeline_context)

        # Assert
        assert result.results["key1"] == "value1"

    def test_execute_multiple_serial_steps(self, pipeline_context):
        """Test executing multiple steps serially."""
        # Arrange
        from .conftest import SimpleStep

        steps = [
            SimpleStep("step1", "key1", "value1"),
            SimpleStep("step2", "key2", "value2"),
            SimpleStep("step3", "key3", "value3"),
        ]
        pipeline = Pipeline(steps)

        # Act
        result = pipeline.run(pipeline_context)

        # Assert
        assert result.results["key1"] == "value1"
        assert result.results["key2"] == "value2"
        assert result.results["key3"] == "value3"

    def test_execute_serial_steps_in_order(self, pipeline_context):
        """Test that serial steps execute in order."""
        # Arrange
        from .conftest import CounterStep

        steps = [
            CounterStep("step1", "counter", 1),
            CounterStep("step2", "counter", 10),
            CounterStep("step3", "counter", 100),
        ]
        pipeline = Pipeline(steps)

        # Act
        result = pipeline.run(pipeline_context)

        # Assert - Should be 0 + 1 + 10 + 100 = 111
        assert result.results["counter"] == 111

    def test_execute_with_context_modification(self, pipeline_context):
        """Test that steps can modify context sequentially."""
        # Arrange
        from typing import Any

        from pipeline import PipelineContext, PipelineStep

        class AppendStep(PipelineStep):
            def __init__(self, step_id: str, value: str):
                self._step_id = step_id
                self._value = value

            @property
            def step_id(self) -> str:
                return self._step_id

            @property
            def description(self) -> str:
                return f"Append {self._value}"

            def run(
                self, context: PipelineContext[Any]
            ) -> PipelineContext[Any]:
                items = context.results.get("items", [])
                items.append(self._value)
                context.results["items"] = items
                return context

        steps = [
            AppendStep("step1", "a"),
            AppendStep("step2", "b"),
            AppendStep("step3", "c"),
        ]
        pipeline = Pipeline(steps)

        # Act
        result = pipeline.run(pipeline_context)

        # Assert
        assert result.results["items"] == ["a", "b", "c"]


class TestPipelineParallelExecution:
    """Test suite for parallel pipeline execution."""

    def test_execute_parallel_group(self, pipeline_context):
        """Test executing parallel group of steps."""
        # Arrange
        from .conftest import SimpleStep

        steps = [
            [  # Parallel group
                SimpleStep("step1", "key1", "value1"),
                SimpleStep("step2", "key2", "value2"),
                SimpleStep("step3", "key3", "value3"),
            ]
        ]
        pipeline = Pipeline(steps)

        # Act
        result = pipeline.run(pipeline_context)

        # Assert
        assert result.results["key1"] == "value1"
        assert result.results["key2"] == "value2"
        assert result.results["key3"] == "value3"

    def test_execute_multiple_parallel_groups(self, pipeline_context):
        """Test executing multiple parallel groups."""
        # Arrange
        from .conftest import SimpleStep

        steps = [
            [  # First parallel group
                SimpleStep("step1", "key1", "value1"),
                SimpleStep("step2", "key2", "value2"),
            ],
            [  # Second parallel group
                SimpleStep("step3", "key3", "value3"),
                SimpleStep("step4", "key4", "value4"),
            ],
        ]
        pipeline = Pipeline(steps)

        # Act
        result = pipeline.run(pipeline_context)

        # Assert
        assert result.results["key1"] == "value1"
        assert result.results["key2"] == "value2"
        assert result.results["key3"] == "value3"
        assert result.results["key4"] == "value4"

    def test_parallel_execution_with_and_operator(self, pipeline_context):
        """Test parallel execution with AND operator."""
        # Arrange
        from .conftest import SimpleStep

        parallel_config = ParallelConfig(operator=LogicOperator.AND)
        config = PipelineConfig(parallel_config=parallel_config)
        steps = [
            [
                SimpleStep("step1", "key1", "value1"),
                SimpleStep("step2", "key2", "value2"),
            ]
        ]
        pipeline = Pipeline(steps, config)

        # Act
        result = pipeline.run(pipeline_context)

        # Assert
        assert result.results["key1"] == "value1"
        assert result.results["key2"] == "value2"

    def test_parallel_execution_with_or_operator(self, pipeline_context):
        """Test parallel execution with OR operator."""
        # Arrange
        from .conftest import FailingStep, SimpleStep

        parallel_config = ParallelConfig(operator=LogicOperator.OR)
        config = PipelineConfig(parallel_config=parallel_config)
        steps = [
            [
                SimpleStep("step1", "key1", "value1"),
                FailingStep("fail", "Error", critical=True),
            ]
        ]
        pipeline = Pipeline(steps, config)

        # Act
        result = pipeline.run(pipeline_context)

        # Assert - Should succeed because one step succeeded
        assert result.results["key1"] == "value1"


class TestPipelineMixedExecution:
    """Test suite for mixed serial and parallel execution."""

    def test_execute_mixed_serial_and_parallel(self, pipeline_context):
        """Test executing mix of serial and parallel steps."""
        # Arrange
        from .conftest import SimpleStep

        steps = [
            SimpleStep("serial1", "s1", "v1"),  # Serial
            [  # Parallel group
                SimpleStep("parallel1", "p1", "v1"),
                SimpleStep("parallel2", "p2", "v2"),
            ],
            SimpleStep("serial2", "s2", "v2"),  # Serial
        ]
        pipeline = Pipeline(steps)

        # Act
        result = pipeline.run(pipeline_context)

        # Assert
        assert result.results["s1"] == "v1"
        assert result.results["p1"] == "v1"
        assert result.results["p2"] == "v2"
        assert result.results["s2"] == "v2"

    def test_complex_mixed_pipeline(self, pipeline_context):
        """Test complex pipeline with multiple serial and parallel steps."""
        # Arrange
        from .conftest import CounterStep, SimpleStep

        steps = [
            SimpleStep("init", "status", "initialized"),
            [  # Parallel processing
                CounterStep("count1", "total", 10),
                CounterStep("count2", "total", 20),
                CounterStep("count3", "total", 30),
            ],
            SimpleStep("middle", "status", "processed"),
            [  # Another parallel group
                SimpleStep("final1", "result1", "done"),
                SimpleStep("final2", "result2", "done"),
            ],
            SimpleStep("complete", "status", "completed"),
        ]
        pipeline = Pipeline(steps)

        # Act
        result = pipeline.run(pipeline_context)

        # Assert
        assert result.results["status"] == "completed"
        assert result.results["total"] == 60  # 10 + 20 + 30
        assert result.results["result1"] == "done"
        assert result.results["result2"] == "done"


class TestPipelineErrorHandling:
    """Test suite for pipeline error handling."""

    def test_fail_fast_stops_on_first_error(self, pipeline_context):
        """Test that fail_fast stops pipeline on first error."""
        # Arrange
        from .conftest import FailingStep, SimpleStep

        steps = [
            SimpleStep("step1", "key1", "value1"),
            FailingStep("fail", "Error", critical=True),
            SimpleStep("step3", "key3", "value3"),  # Should not execute
        ]
        config = PipelineConfig(fail_fast=True)
        pipeline = Pipeline(steps, config)

        # Act & Assert
        with pytest.raises(RuntimeError):
            pipeline.run(pipeline_context)

        # Assert - step3 should not have executed
        assert "key1" in pipeline_context.results
        assert "key3" not in pipeline_context.results

    def test_fail_fast_false_continues_on_error(self, pipeline_context):
        """Test that fail_fast=False continues after errors."""
        # Arrange
        from .conftest import FailingStep, SimpleStep

        steps = [
            SimpleStep("step1", "key1", "value1"),
            FailingStep("fail", "Error", critical=True),
            SimpleStep("step3", "key3", "value3"),
        ]
        config = PipelineConfig(fail_fast=False)
        pipeline = Pipeline(steps, config)

        # Act
        result = pipeline.run(pipeline_context)

        # Assert - All steps should execute
        assert result.results["key1"] == "value1"
        assert result.results["key3"] == "value3"
        assert len(result.errors) >= 1

    def test_non_critical_step_does_not_stop_pipeline(self, pipeline_context):
        """Test that non-critical step failure doesn't stop pipeline."""
        # Arrange
        from .conftest import FailingStep, SimpleStep

        steps = [
            SimpleStep("step1", "key1", "value1"),
            FailingStep("fail", "Error", critical=False),
            SimpleStep("step3", "key3", "value3"),
        ]
        pipeline = Pipeline(steps)

        # Act
        result = pipeline.run(pipeline_context)

        # Assert
        assert result.results["key1"] == "value1"
        assert result.results["key3"] == "value3"
        assert len(result.errors) == 1

    def test_parallel_group_failure_with_fail_fast(self, pipeline_context):
        """Test parallel group failure with fail_fast."""
        # Arrange
        from .conftest import FailingStep, SimpleStep

        steps = [
            SimpleStep("step1", "key1", "value1"),
            [  # Parallel group with failure
                SimpleStep("p1", "p1", "v1"),
                FailingStep("fail", "Error", critical=True),
            ],
            SimpleStep("step3", "key3", "value3"),  # Should not execute
        ]
        config = PipelineConfig(fail_fast=True)
        pipeline = Pipeline(steps, config)

        # Act & Assert
        with pytest.raises(RuntimeError):
            pipeline.run(pipeline_context)

    def test_error_accumulation(self, pipeline_context):
        """Test that errors accumulate in context."""
        # Arrange
        from .conftest import FailingStep

        steps = [
            FailingStep("fail1", "Error 1", critical=False),
            FailingStep("fail2", "Error 2", critical=False),
            FailingStep("fail3", "Error 3", critical=False),
        ]
        pipeline = Pipeline(steps)

        # Act
        result = pipeline.run(pipeline_context)

        # Assert
        assert len(result.errors) == 3


class TestPipelineRealWorldScenarios:
    """Test suite for real-world pipeline scenarios."""

    def test_data_processing_pipeline(self, pipeline_context):
        """Test a data processing pipeline scenario."""
        # Arrange
        from typing import Any

        from pipeline import PipelineContext, PipelineStep

        class LoadDataStep(PipelineStep):
            @property
            def step_id(self) -> str:
                return "load_data"

            @property
            def description(self) -> str:
                return "Load data"

            def run(
                self, context: PipelineContext[Any]
            ) -> PipelineContext[Any]:
                context.results["data"] = [1, 2, 3, 4, 5]
                return context

        class ProcessDataStep(PipelineStep):
            def __init__(self, multiplier: int):
                self.multiplier = multiplier

            @property
            def step_id(self) -> str:
                return f"process_{self.multiplier}"

            @property
            def description(self) -> str:
                return f"Process with multiplier {self.multiplier}"

            def run(
                self, context: PipelineContext[Any]
            ) -> PipelineContext[Any]:
                data = context.results.get("data", [])
                processed = [x * self.multiplier for x in data]
                context.results[f"processed_{self.multiplier}"] = sum(
                    processed
                )
                return context

        class AggregateStep(PipelineStep):
            @property
            def step_id(self) -> str:
                return "aggregate"

            @property
            def description(self) -> str:
                return "Aggregate results"

            def run(
                self, context: PipelineContext[Any]
            ) -> PipelineContext[Any]:
                total = 0
                for key, value in context.results.items():
                    if key.startswith("processed_"):
                        total += value
                context.results["total"] = total
                return context

        steps = [
            LoadDataStep(),
            [  # Parallel processing
                ProcessDataStep(2),
                ProcessDataStep(3),
                ProcessDataStep(4),
            ],
            AggregateStep(),
        ]
        pipeline = Pipeline(steps)

        # Act
        result = pipeline.run(pipeline_context)

        # Assert
        assert result.results["data"] == [1, 2, 3, 4, 5]
        assert result.results["processed_2"] == 30  # (1+2+3+4+5)*2
        assert result.results["processed_3"] == 45  # (1+2+3+4+5)*3
        assert result.results["processed_4"] == 60  # (1+2+3+4+5)*4
        assert result.results["total"] == 135  # 30+45+60

    def test_installation_pipeline_scenario(self, pipeline_context):
        """Test an installation pipeline scenario."""
        # Arrange
        from typing import Any

        from pipeline import PipelineContext, PipelineStep

        class ValidateStep(PipelineStep):
            @property
            def step_id(self) -> str:
                return "validate"

            @property
            def description(self) -> str:
                return "Validate environment"

            def run(
                self, context: PipelineContext[Any]
            ) -> PipelineContext[Any]:
                context.results["validated"] = True
                return context

        class BackupStep(PipelineStep):
            @property
            def step_id(self) -> str:
                return "backup"

            @property
            def description(self) -> str:
                return "Backup existing files"

            def run(
                self, context: PipelineContext[Any]
            ) -> PipelineContext[Any]:
                context.results["backed_up"] = True
                return context

        class InstallComponentStep(PipelineStep):
            def __init__(self, component: str):
                self.component = component

            @property
            def step_id(self) -> str:
                return f"install_{self.component}"

            @property
            def description(self) -> str:
                return f"Install {self.component}"

            def run(
                self, context: PipelineContext[Any]
            ) -> PipelineContext[Any]:
                installed = context.results.get("installed", [])
                installed.append(self.component)
                context.results["installed"] = installed
                return context

        class FinalizeStep(PipelineStep):
            @property
            def step_id(self) -> str:
                return "finalize"

            @property
            def description(self) -> str:
                return "Finalize installation"

            def run(
                self, context: PipelineContext[Any]
            ) -> PipelineContext[Any]:
                context.results["completed"] = True
                return context

        steps = [
            ValidateStep(),
            BackupStep(),
            [  # Parallel installation
                InstallComponentStep("vim"),
                InstallComponentStep("zsh"),
                InstallComponentStep("tmux"),
            ],
            FinalizeStep(),
        ]
        pipeline = Pipeline(steps)

        # Act
        result = pipeline.run(pipeline_context)

        # Assert
        assert result.results["validated"] is True
        assert result.results["backed_up"] is True
        assert len(result.results["installed"]) == 3
        assert "vim" in result.results["installed"]
        assert "zsh" in result.results["installed"]
        assert "tmux" in result.results["installed"]
        assert result.results["completed"] is True
