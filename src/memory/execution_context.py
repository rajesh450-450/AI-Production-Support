from dataclasses import dataclass, field, asdict
from datetime import datetime, timezone
from enum import Enum
import uuid


# =========================================================
# Execution Status
# =========================================================


class ExecutionStatus(str, Enum):
    RUNNING = "Running"
    COMPLETED = "Completed"
    FAILED = "Failed"


# =========================================================
# Runtime Metadata
# =========================================================


@dataclass
class RuntimeMetadata:
    conversation_id: str = ""
    workflow: str = ""
    planner_model: str = ""
    executor_model: str = ""
    reviewer_model: str = ""
    answer_model: str = ""


# =========================================================
# Runtime Progress
# =========================================================


@dataclass
class RuntimeProgress:
    current_phase: str = ""
    current_step: int = 0
    total_steps: int = 0
    current_tool: str = ""


# =========================================================
# Runtime Metrics
# =========================================================


@dataclass
class RuntimeMetrics:
    llm_calls: int = 0
    tool_calls: int = 0
    retries: int = 0
    duration_ms: float = 0.0


# =========================================================
# Runtime Event
# =========================================================


@dataclass
class RuntimeEvent:
    timestamp: datetime
    level: str
    component: str
    message: str


# =========================================================
# Investigation Runtime
# =========================================================


@dataclass
class InvestigationRuntime:
    """
    Runtime information about the current investigation.

    This is NOT LangGraph workflow state.

    It exists only for runtime monitoring,
    observability, dashboards and APIs.
    """

    # Unique ID for this execution.
    # This is the execution_id.
    id: str = field(
        default_factory=lambda: str(uuid.uuid4())
    )

    # Always store internal timestamps as
    # timezone-aware UTC datetime objects.
    started_at: datetime = field(
        default_factory=lambda: datetime.now(timezone.utc)
    )

    completed_at: datetime | None = None

    status: ExecutionStatus = ExecutionStatus.RUNNING

    metadata: RuntimeMetadata = field(
        default_factory=RuntimeMetadata
    )

    progress: RuntimeProgress = field(
        default_factory=RuntimeProgress
    )

    metrics: RuntimeMetrics = field(
        default_factory=RuntimeMetrics
    )

    events: list[RuntimeEvent] = field(
        default_factory=list
    )


# =========================================================
# Execution Context
# =========================================================


class ExecutionContext:

    def __init__(self):
        self.runtime = InvestigationRuntime()

    # -----------------------------------------------------
    # Lifecycle
    # -----------------------------------------------------

    def reset(self):
        self.runtime = InvestigationRuntime()

    def complete(self):
        self.runtime.status = ExecutionStatus.COMPLETED

        # Keep completed_at as a timezone-aware datetime.
        # Do NOT use .isoformat() here because duration
        # calculation requires datetime arithmetic.
        self.runtime.completed_at = datetime.now(timezone.utc)

        self._calculate_duration()

    def fail(self):
        self.runtime.status = ExecutionStatus.FAILED

        # Keep completed_at as a timezone-aware datetime.
        self.runtime.completed_at = datetime.now(timezone.utc)

        self._calculate_duration()

    def set_status(
        self,
        status: ExecutionStatus,
    ):
        self.runtime.status = status

    def _calculate_duration(self):
        if self.runtime.completed_at:

            duration = (
                self.runtime.completed_at
                - self.runtime.started_at
            )

            self.runtime.metrics.duration_ms = (
                duration.total_seconds() * 1000
            )

    # -----------------------------------------------------
    # Metadata
    # -----------------------------------------------------

    def set_conversation_id(
        self,
        conversation_id: str,
    ):
        """
        Associate the current execution with
        the conversation that triggered it.
        """

        self.runtime.metadata.conversation_id = (
            conversation_id
        )

    def update_metadata(
        self,
        **kwargs,
    ):
        for key, value in kwargs.items():

            if hasattr(
                self.runtime.metadata,
                key,
            ):
                setattr(
                    self.runtime.metadata,
                    key,
                    value,
                )

    # -----------------------------------------------------
    # Progress
    # -----------------------------------------------------

    def update_progress(
        self,
        **kwargs,
    ):
        for key, value in kwargs.items():

            if hasattr(
                self.runtime.progress,
                key,
            ):
                setattr(
                    self.runtime.progress,
                    key,
                    value,
                )

    # -----------------------------------------------------
    # Metrics
    # -----------------------------------------------------

    def update_metrics(
        self,
        **kwargs,
    ):
        for key, value in kwargs.items():

            if hasattr(
                self.runtime.metrics,
                key,
            ):
                setattr(
                    self.runtime.metrics,
                    key,
                    value,
                )

    def increment_llm_calls(self):
        self.runtime.metrics.llm_calls += 1

    def increment_tool_calls(self):
        self.runtime.metrics.tool_calls += 1

    def increment_retries(self):
        self.runtime.metrics.retries += 1

    # -----------------------------------------------------
    # Events
    # -----------------------------------------------------

    def add_event(
        self,
        level: str,
        component: str,
        message: str,
    ):
        self.runtime.events.append(
            RuntimeEvent(
                timestamp=datetime.now(timezone.utc),
                level=level,
                component=component,
                message=message,
            )
        )

    # -----------------------------------------------------
    # Read Runtime
    # -----------------------------------------------------

    def get(self):
        return self.runtime

    # -----------------------------------------------------
    # Serialization
    # -----------------------------------------------------

    def to_dict(self):

        data = asdict(
            self.runtime
        )

        data["status"] = (
            self.runtime.status.value
        )

        return data

    # -----------------------------------------------------
    # Summary
    # -----------------------------------------------------

    def summary(self):

        return {
            "execution_id": self.runtime.id,

            "conversation_id": (
                self.runtime.metadata.conversation_id
            ),

            "status": (
                self.runtime.status.value
            ),

            "started_at": (
                self.runtime.started_at
            ),

            "completed_at": (
                self.runtime.completed_at
            ),

            "duration_ms": (
                self.runtime.metrics.duration_ms
            ),

            "current_phase": (
                self.runtime.progress.current_phase
            ),

            "current_step": (
                self.runtime.progress.current_step
            ),

            "total_steps": (
                self.runtime.progress.total_steps
            ),

            "llm_calls": (
                self.runtime.metrics.llm_calls
            ),

            "tool_calls": (
                self.runtime.metrics.tool_calls
            ),

            "retries": (
                self.runtime.metrics.retries
            ),
        }

    # -----------------------------------------------------
    # Display
    # -----------------------------------------------------

    def display(self):

        print(
            "\n========== Execution Context =========="
        )

        print(
            f"Execution ID    : "
            f"{self.runtime.id}"
        )

        print(
            f"Conversation ID  : "
            f"{self.runtime.metadata.conversation_id}"
        )

        print(
            f"Status           : "
            f"{self.runtime.status.value}"
        )

        print(
            f"Started At       : "
            f"{self.runtime.started_at}"
        )

        if self.runtime.completed_at:

            print(
                f"Completed At     : "
                f"{self.runtime.completed_at}"
            )

        print("\nMetadata")

        print(
            self.runtime.metadata
        )

        print("\nProgress")

        print(
            self.runtime.progress
        )

        print("\nMetrics")

        print(
            self.runtime.metrics
        )

        print("\nEvents")

        if not self.runtime.events:

            print("  None")

        else:

            for event in self.runtime.events:

                print(
                    f"  [{event.timestamp}] "
                    f"{event.level:<7} "
                    f"{event.component:<20} "
                    f"{event.message}"
                )

        print(
            "=======================================\n"
        )


# =========================================================
# Global Execution Context
# =========================================================


execution_context = ExecutionContext()