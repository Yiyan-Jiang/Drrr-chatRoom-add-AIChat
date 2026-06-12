class HarnessError(Exception):
    error_code = "HARNESS_ERROR"

    def __init__(self, message: str | None = None):
        super().__init__(message or self.error_code)


class ActionParseError(HarnessError):
    error_code = "ACTION_PARSE_ERROR"


class PlannerInvalidAction(HarnessError):
    error_code = "PLANNER_INVALID_ACTION"


class PlannerContractError(HarnessError):
    error_code = "PLANNER_CONTRACT_ERROR"


class ModelGatewayError(HarnessError):
    error_code = "MODEL_GATEWAY_ERROR"


class PlannerExceededMaxIterations(HarnessError):
    error_code = "PLANNER_EXCEEDED_MAX_ITERATIONS"


class PlannerNoProgress(HarnessError):
    error_code = "PLANNER_NO_PROGRESS"


class CheckpointContractError(HarnessError):
    error_code = "CHECKPOINT_CONTRACT_ERROR"
