"""Admin deploy status payload — orchestrates utils + Linear state filter (AST-792)."""

from src.external.linear import LinearApiError, fetch_parent_issue_states
from src.utils import deploy_status as utils_ds
from src.utils.config import MERGE_TICKET_LOG_CONFIG
from src.utils.merge_ticket_log import read_merge_ticket_log


def get_deploy_status_payload() -> dict:
    payload = utils_ds.get_deploy_status_payload()
    entries = read_merge_ticket_log()
    if not entries:
        payload["merge_tickets"] = []
        return payload
    ticket_ids = list(
        dict.fromkeys(e.get("ticket_id", "") for e in entries if e.get("ticket_id"))
    )
    try:
        state_by_id = fetch_parent_issue_states(ticket_ids)
    except (LinearApiError, KeyError, ValueError):
        payload["merge_tickets"] = []
        return payload
    uat = MERGE_TICKET_LOG_CONFIG["uat_state_name"]
    filtered = utils_ds.filter_merge_tickets_by_state(
        entries, state_by_id, uat_state_name=uat
    )
    payload["merge_tickets"] = utils_ds.merge_tickets_recent_first(filtered)
    return payload
