from storage.parquet_store import write_row
from state.state import USERS, WAITING

def snapshot_metrics():
    users_total = len(USERS)
    users_active_24h = users_total
    users_waiting_now = len(WAITING)
    conversations_active_now = sum(1 for u in USERS.values() if u.status == "conversando") // 2
    write_row("metrics_snapshots", {
        "users_total": users_total,
        "users_active_24h": users_active_24h,
        "users_waiting_now": users_waiting_now,
        "conversations_active_now": conversations_active_now
    })
