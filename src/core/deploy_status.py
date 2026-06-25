"""Admin deploy status payload — log-only merge tickets (AST-800)."""

from src.utils import deploy_status as utils_ds
from src.utils.merge_ticket_log import read_merge_ticket_log


def get_deploy_status_payload() -> dict:
    payload = utils_ds.get_deploy_status_payload()
    entries = read_merge_ticket_log()
    payload["merge_tickets"] = utils_ds.merge_tickets_recent_first(entries)
    return payload
