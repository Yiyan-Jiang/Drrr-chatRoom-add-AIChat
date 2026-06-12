class OrchestratorError(Exception):
    error_code = "ORCHESTRATOR_ERROR"
    status_code = 400

    def __init__(self, message: str | None = None):
        super().__init__(message or self.error_code)


class RequestInProgress(OrchestratorError):
    error_code = "REQUEST_IN_PROGRESS"
    status_code = 409


class RequestIdOwnershipError(OrchestratorError):
    error_code = "REQUEST_ID_FORBIDDEN"
    status_code = 403


class PreviousRequestFailed(OrchestratorError):
    error_code = "PREVIOUS_REQUEST_FAILED"
    status_code = 409


class SessionNotFound(OrchestratorError):
    error_code = "SESSION_NOT_FOUND"
    status_code = 404


class SessionOwnershipError(OrchestratorError):
    error_code = "SESSION_OWNERSHIP_ERROR"
    status_code = 403


class SessionNotActive(OrchestratorError):
    error_code = "SESSION_NOT_ACTIVE"
    status_code = 409
