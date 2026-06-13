from ai.resources.models import AgentResource


def can_see_resource(workspace, resource: AgentResource) -> bool:
    if resource.scope == "session":
        return resource.session_id == workspace.session.session_id
    if resource.scope == "user":
        return resource.owner_user_id == workspace.session.user_id
    if resource.scope == "workspace":
        return resource.owner_user_id == workspace.session.user_id
    if resource.scope == "turn":
        return resource.session_id == workspace.session.session_id
    return False
