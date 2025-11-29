import os, json, uuid, time, glob
from datetime import datetime, timezone, date 
import pandas as pd

DATA_DIR = os.getenv("DATA_DIR", "./data")

def _part_dir(dataset: str, when=None):
    if when is None:
        when = datetime.now(timezone.utc)
    date_str = when.astimezone(timezone.utc).strftime("%Y-%m-%d")
    p = os.path.join(DATA_DIR, dataset, f"date={date_str}")
    os.makedirs(p, exist_ok=True)
    return p

def _file_path(dataset: str, when=None):
    pdir = _part_dir(dataset, when)
    ts_ns = time.time_ns()
    uid = uuid.uuid4().hex
    return os.path.join(pdir, f"{dataset}-{ts_ns}-{uid}.parquet")

def _deep_normalize(v):
    if isinstance(v, dict):
        return {k: _deep_normalize(v2) for k, v2 in v.items()}
    if isinstance(v, (list, tuple, set)):
        return [_deep_normalize(i) for i in v]
    if isinstance(v, (datetime, date)):
        return v.isoformat()
    if isinstance(v, (bytes, bytearray)):
        try:
            return v.decode("utf-8", "ignore")
        except Exception:
            return str(v)
    return v

def _normalize_row(row: dict) -> dict:
    norm = {k: _deep_normalize(v) for k, v in row.items()}
    out = {}
    for k, v in norm.items():
        if isinstance(v, (dict, list)):
            out[k] = json.dumps(v, ensure_ascii=False)
        else:
            out[k] = v
    return out

def write_row(dataset: str, row: dict, when=None):
    fp = _file_path(dataset, when)
    df = pd.DataFrame([_normalize_row(row)])
    df.to_parquet(fp, engine="pyarrow", index=False)

def write_rows(dataset: str, rows: list[dict], when=None):
    if not rows:
        return
    fp = _file_path(dataset, when)
    df = pd.DataFrame([_normalize_row(r) for r in rows])
    df.to_parquet(fp, engine="pyarrow", index=False)

def ensure_layout():
    for ds in [
        "app_events", "messages", "conversations", "bans",
        "blocks", "users_status_changes", "users_snapshot", "metrics_snapshots",
        os.path.join("messages", "chunks")
    ]:
        _part_dir(ds)

def _msg_chunk_dir(conversation_id: str, when=None):
    return _part_dir(os.path.join("messages", "chunks", f"conversation={conversation_id}"), when)

def write_message_chunk(conversation_id: str, row: dict, when=None):
    fpdir = _msg_chunk_dir(conversation_id, when)
    ts_ns = time.time_ns()
    uid = uuid.uuid4().hex
    fp = os.path.join(fpdir, f"chunk-{ts_ns}-{uid}.parquet")
    df = pd.DataFrame([_normalize_row(row)])
    df.to_parquet(fp, engine="pyarrow", index=False)

def compact_messages(conversation_id: str, delete_chunks: bool = True) -> dict:
    base = os.path.join(DATA_DIR, "messages", "chunks", f"conversation={conversation_id}")
    parts = glob.glob(os.path.join(base, "date=*"))
    files = []
    for p in parts:
        files.extend(glob.glob(os.path.join(p, "*.parquet")))
    if not files:
        return {"conversation_id": conversation_id, "files": 0, "rows": 0, "written": False}

    dfs = []
    for f in files:
        try:
            dfs.append(pd.read_parquet(f, engine="pyarrow"))
        except Exception:
            pass
    if not dfs:
        return {"conversation_id": conversation_id, "files": len(files), "rows": 0, "written": False}

    df = pd.concat(dfs, ignore_index=True)
    if "ts" in df.columns:
        try:
            df = df.sort_values("ts")
        except Exception:
            pass

    outdir = os.path.join(DATA_DIR, "messages", f"conversation={conversation_id}")
    os.makedirs(outdir, exist_ok=True)
    outfile = os.path.join(outdir, "messages.parquet")
    df.to_parquet(outfile, engine="pyarrow", index=False)

    if delete_chunks:
        for f in files:
            try:
                os.remove(f)
            except Exception:
                pass

    return {
        "conversation_id": conversation_id,
        "files": len(files),
        "rows": int(df.shape[0]),
        "written": True,
        "outfile": outfile
    }
