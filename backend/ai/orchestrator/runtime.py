import os

from ai.harness.json_planner import JSONPlannerClient
from ai.harness.model_config import load_planner_model_config
from ai.harness.model_gateway import ModelGateway
from ai.harness.planner_verifier import PlannerVerifier
from ai.harness.response_renderer import FinalResponseRenderer
from ai.harness.runtime import HarnessRuntime
from ai.orchestrator.schemas import RunResult, TurnWorkspace


def build_harness_runtime(repository=None) -> HarnessRuntime:
    if os.environ.get("AGENT_CORE_ENABLE_LLM_PLANNER") != "1":
        return HarnessRuntime(repository=repository)

    config = load_planner_model_config()
    gateway = ModelGateway(config)
    return HarnessRuntime(
        repository=repository,
        planner=JSONPlannerClient(gateway=gateway),
        planner_verifier=PlannerVerifier(),
        response_renderer=FinalResponseRenderer(gateway=gateway),
    )


async def run_harness_runtime(workspace: TurnWorkspace) -> RunResult:
    return await build_harness_runtime().run_turn(workspace)


async def run_fake_harness(workspace: TurnWorkspace) -> RunResult:
    return await run_harness_runtime(workspace)
