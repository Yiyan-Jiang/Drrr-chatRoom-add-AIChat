import json


class ReplayPlanner:
    def __init__(self, actions: list[dict | str]):
        self._actions = list(actions)
        self.index = 0

    async def plan(self, _context) -> str:
        if self.index >= len(self._actions):
            raise RuntimeError("replay planner exhausted")

        action = self._actions[self.index]
        self.index += 1
        if isinstance(action, str):
            return action
        return json.dumps(action, ensure_ascii=False)
