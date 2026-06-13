class SkillError(Exception):
    pass


class SkillContractError(SkillError, ValueError):
    pass


class SkillNotFound(SkillError, KeyError):
    pass
