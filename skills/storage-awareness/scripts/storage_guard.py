#!/usr/bin/env python3
"""Fail-closed storage policy validation and inventory normalization."""
from __future__ import annotations
import argparse, datetime as dt, json, os, shutil, sys, tempfile
from contextlib import contextmanager
from pathlib import Path

GiB = 1024 ** 3
MODEL_SUFFIXES = (".gguf", ".safetensors", ".ckpt", ".pt", ".bin")
MODEL_DIRS = ("model-cache", "model_cache")

class PolicyError(RuntimeError): pass

def now(): return dt.datetime.now(dt.timezone.utc)
def parse_time(value):
    parsed=dt.datetime.fromisoformat(value.replace("Z", "+00:00"))
    if parsed.tzinfo is None or parsed.utcoffset() is None: raise ValueError("timestamp must be timezone-aware")
    return parsed.astimezone(dt.timezone.utc)
def canon(value):
    return os.path.normcase(os.path.normpath(str(Path(value).expanduser().resolve(strict=False))))
def absolute_path(value):
    text=str(value) if isinstance(value,(str,Path)) else ""
    if not text.strip() or not os.path.isabs(text): raise PolicyError("path must be nonempty and absolute")
    return canon(text)
def is_within(path, root):
    try: return os.path.commonpath([canon(path), canon(root)]) == canon(root)
    except ValueError: return False
def load_map(filename):
    try: data = json.loads(Path(filename).read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as e: raise PolicyError(f"policy map unreadable: {e}")
    if data.get("schema_version") != 1: raise PolicyError("unsupported or missing schema_version")
    try: age = (now() - parse_time(data["generated_at"])).total_seconds()
    except (KeyError, ValueError, TypeError) as e: raise PolicyError(f"invalid generated_at: {e}")
    if age < -300 or age > int(data.get("max_age_seconds", 3600)): raise PolicyError("policy map stale or clock-invalid")
    for key in ("protected_paths", "approved_roots", "action_grants"):
        if not isinstance(data.get(key, []), list): raise PolicyError(f"{key} must be a list")
    for path in data["protected_paths"] + data["approved_roots"]: absolute_path(path)
    ids=set()
    for grant in data["action_grants"]:
        if not isinstance(grant,dict) or not isinstance(grant.get("id"),str) or not grant["id"] or grant["id"] in ids: raise PolicyError("grant IDs must be unique and nonempty")
        ids.add(grant["id"]); absolute_path(grant.get("target"))
        if grant.get("action") not in {"delete","move","compress"}: raise PolicyError("unrecognized grant action")
        if not all(grant.get(k) is True for k in ("agent_owned","positively_disposable","recovery_retained")): raise PolicyError("grant lacks ownership/disposal/recovery evidence")
        try: parse_time(grant["expires_at"])
        except (KeyError,TypeError,ValueError): raise PolicyError("grant expiry must be timezone-aware")
    return data
def protected(path, policy): return any(is_within(path, p) or is_within(p, path) for p in policy["protected_paths"])
def is_reparse_point(path):
    p=Path(path)
    try:
        return p.is_symlink() or (hasattr(p,"is_junction") and p.is_junction()) or bool(getattr(p.lstat(),"st_file_attributes",0) & 0x400)
    except OSError: return True
def model_like(path):
    lower = canon(path).replace("\\", "/")
    name = lower.rsplit("/", 1)[-1]
    return name.endswith(MODEL_SUFFIXES) or any(f"/{marker}/" in f"/{lower}/" for marker in MODEL_DIRS) or "/cache/models/" in f"/{lower}/"
@contextmanager
def volume_lock(volume_root, lock_directory):
    """Atomic per-volume lock; contention fails closed rather than waiting."""
    drive=os.path.splitdrive(canon(volume_root))[0] or Path(canon(volume_root)).anchor
    key = drive.replace(":", "").replace("\\", "_").replace("/", "_")
    path = Path(lock_directory) / f"storage-{key}.lock"
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        fd = os.open(path, os.O_CREAT | os.O_EXCL | os.O_WRONLY)
    except FileExistsError: raise PolicyError(f"volume lock unavailable: {path}")
    try:
        os.write(fd, str(os.getpid()).encode()); yield path
    finally:
        os.close(fd)
        try: path.unlink()
        except FileNotFoundError: pass
def find_grant(path, action, policy, grant_id=None):
    target = absolute_path(path)
    if protected(target, policy): raise PolicyError("target is protected")
    if model_like(target): raise PolicyError("model/checkpoint/cache target is excluded")
    if not any(is_within(target, root) for root in policy["approved_roots"]): raise PolicyError("target outside approved roots")
    matches=[g for g in policy["action_grants"] if g.get("action")==action and canon(g.get("target", ""))==target and (grant_id is None or g.get("id")==grant_id)]
    if len(matches)!=1: raise PolicyError("no unique exact live action grant")
    grant=matches[0]
    if parse_time(grant["expires_at"]) < now(): raise PolicyError("action grant expired")
    return grant
def mutation_allowed(path, action, policy, grant_id=None): return find_grant(path,action,policy,grant_id)["id"]
def tree_issues(path, policy, allowed_extensions=None):
    """Inspect every descendant before a recursive mutation; never infer safety."""
    root = Path(path)
    if not root.is_dir(): raise PolicyError("target must be an existing directory")
    if is_reparse_point(root): return [(str(root),"reparse-point target requires separate review")]
    issues=[]
    for item in root.rglob("*"):
        if is_reparse_point(item): issues.append((str(item),"reparse-point descendant requires separate review")); continue
        if not item.is_file(): continue
        resolved=canon(item)
        if protected(resolved, policy): issues.append((str(item),"protected descendant")); continue
        if model_like(resolved): issues.append((str(item),"model/checkpoint/cache descendant")); continue
        try:
            if item.stat().st_nlink > 1: issues.append((str(item),"hardlink alias requires separate review")); continue
        except OSError: issues.append((str(item),"unstatable descendant")); continue
        if allowed_extensions is not None and item.suffix.lower() not in allowed_extensions:
            issues.append((str(item),"extension not in exact grant allowlist"))
    return issues
def copy_verify(source, destination, map_path, grant_id, estimated_peak_bytes, lock_directory, verifier=None, copy_impl=None):
    """Stage a copy and hash it; remove only the staged copy if verification fails."""
    src, dst = Path(source), Path(destination)
    if not src.is_file() or dst.exists(): raise PolicyError("source must be a file and destination must not exist")
    def digest(p):
        import hashlib
        h=hashlib.sha256()
        with p.open("rb") as f:
            for block in iter(lambda:f.read(1024*1024), b""): h.update(block)
        return h.hexdigest()
    copy_impl=copy_impl or shutil.copyfile
    with volume_lock(dst.parent.anchor,lock_directory):
     stage=None
     try:
        policy=load_map(map_path)
        find_grant(src,"move",policy,grant_id)
        if is_reparse_point(src) or src.stat().st_nlink>1 or protected(dst,policy) or model_like(src) or model_like(dst) or not any(is_within(dst,r) for r in policy["approved_roots"]): raise PolicyError("source or destination fails shared policy")
        if not preflight(dst.parent,estimated_peak_bytes,policy)["allowed"]: raise PolicyError("destination capacity preflight failed")
        if dst.exists(): raise PolicyError("destination appeared during staging")
        dst.parent.mkdir(parents=True,exist_ok=True)
        fd,name=tempfile.mkstemp(prefix=".storage-stage-",dir=dst.parent); os.close(fd); stage=Path(name)
        copy_impl(src,stage)
        verified=src.stat().st_size == stage.stat().st_size and digest(src) == digest(stage)
        if verifier is not None: verified = verified and bool(verifier(src,stage))
        if not verified: raise PolicyError("copy verification failed")
        os.link(stage,dst); stage.unlink(); stage=None
        return {"copied":True,"source":str(src),"destination":str(dst),"sha256":digest(dst)}
     except Exception:
        if stage is not None and stage.exists(): stage.unlink()
        raise
def preflight(path, peak, policy=None):
    if peak is None or not isinstance(peak,int) or peak < 0: raise PolicyError("peak growth must be a known non-negative integer")
    usage = shutil.disk_usage(path)
    reservations = (policy or {}).get("reservations", {})
    minimum=reservations.get("default_min_bytes",20*GiB); percent=reservations.get("default_percent",.05)
    if not isinstance(minimum,(int,float)) or not isinstance(percent,(int,float)) or minimum<0 or percent<0: raise PolicyError("reservation values must be finite and non-negative")
    reserve = max(int(minimum), int(usage.total * float(percent)))
    required = reserve + int(peak * 1.25)
    return {"path": canon(path), "total_bytes": usage.total, "free_bytes": usage.free, "reserve_bytes": reserve, "estimated_peak_bytes": peak, "required_free_bytes": required, "allowed": usage.free > required}
def value(item, snake, camel, default=None): return item.get(snake, item.get(camel, default))
def normalized_item(item, hardlink_evidence=()):
    path = item.get("path") or item.get("exact_path") or ""
    purpose = item.get("purpose", "unspecified")
    declared = str(item.get("category", "unknown")).lower()
    compression = str(value(item, "compression_analysis", "compressionAnalysis", "")).lower()
    removal = str(value(item, "removal_review", "removalReview", "")).lower()
    if model_like(path) or any(x in purpose.lower() for x in ("model", "checkpoint", "weight")): category, action = "keep", "hard-exclude model data; no compression, move, or deletion"
    elif "excluded" in compression or "do not remove" in removal: category, action = "keep", "retained or excluded by supplied evidence"
    elif "compression" in declared or "compress" in compression: category, action = "compression_analysis", "requires measured bounded test and smoke check"
    elif declared in {"keep", "compression_analysis", "relocation_review", "removal_review", "unknown"}: category, action = declared, "review evidence before any mutation"
    else: category, action = "unknown", "insufficient classification evidence"
    deps=list(item.get("dependencies", []))
    base=canon(path)
    for link in hardlink_evidence:
        if any(is_within(link.get(k,""),base) for k in ("file","linkedPath","linked_path")): deps.append({"type":"hardlink_evidence","evidence":link})
    if deps: category, action="keep","hardlink alias requires separate review"
    return {"path": path, "purpose": purpose, "logical_bytes": value(item,"logical_bytes","logicalBytes"), "allocated_bytes": value(item,"allocated_bytes","allocatedBytes"), "allocation_measured": bool(value(item,"allocation_measured","allocationMeasured",False)), "compression_state": value(item,"compression_state","compressionState","unknown"), "compression_confidence": value(item,"compression_confidence","confidence","unknown"), "dependencies": deps, "category": category, "action": action, "recovery": item.get("recovery", "not established")}
def main():
    p=argparse.ArgumentParser(); sub=p.add_subparsers(dest="cmd", required=True)
    q=sub.add_parser("validate-map"); q.add_argument("--map", required=True)
    q=sub.add_parser("preflight"); q.add_argument("--path", required=True); q.add_argument("--estimated-peak-bytes", type=int, required=True); q.add_argument("--map")
    q=sub.add_parser("check-mutation"); q.add_argument("--map", required=True); q.add_argument("--path", required=True); q.add_argument("--action", choices=("delete","move"), required=True); q.add_argument("--estimated-peak-bytes",type=int,required=True); q.add_argument("--lock-directory",default=str(Path.home()/".storage-awareness"/"locks")); q.add_argument("--grant-id")
    q=sub.add_parser("audit-inventory"); q.add_argument("--input", required=True); q.add_argument("--output", required=True)
    a=p.parse_args()
    try:
        if a.cmd == "validate-map": result={"valid": True, "schema_version": load_map(a.map)["schema_version"]}
        elif a.cmd == "preflight": result=preflight(a.path,a.estimated_peak_bytes,load_map(a.map) if a.map else None)
        elif a.cmd == "check-mutation":
            if is_reparse_point(a.path): raise PolicyError("reparse-point target requires separate review")
            target=absolute_path(a.path)
            with volume_lock(Path(target).anchor,a.lock_directory):
                policy=load_map(a.map); grant_id=mutation_allowed(target,a.action,policy,a.grant_id); capacity=preflight(target,a.estimated_peak_bytes,policy)
                if not capacity["allowed"]: raise PolicyError("capacity preflight failed")
                if Path(target).is_dir() and tree_issues(target,policy): raise PolicyError("recursive target contains unsafe descendants")
                if Path(target).is_file() and Path(target).stat().st_nlink > 1: raise PolicyError("hardlink target requires separate review")
                result={"allowed":True,"grant_id":grant_id,"capacity":capacity}
        else:
            raw=json.loads(Path(a.input).read_text(encoding="utf-8")); items=raw.get("items", raw if isinstance(raw,list) else [])
            if not isinstance(items,list): raise PolicyError("inventory items must be a list")
            links=raw.get("hardlinkEvidence",raw.get("hardlink_evidence",[])) if isinstance(raw,dict) else []
            result={"schema_version":1,"generated_at":now().isoformat(),"source_metadata":{"mode":raw.get("mode"),"limitations":raw.get("limitations",[]),"known_subtotals":raw.get("knownSubtotals",raw.get("known_subtotals",[]))},"hardlink_evidence":links,"items":[normalized_item(i,links) for i in items]}; Path(a.output).write_text(json.dumps(result,indent=2),encoding="utf-8")
        print(json.dumps(result, indent=2))
    except PolicyError as e: print(json.dumps({"allowed":False,"error":str(e)})); return 2
    return 0
if __name__ == "__main__": sys.exit(main())
