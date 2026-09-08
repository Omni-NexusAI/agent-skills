#!/usr/bin/env python3
"""Fail-closed storage policy validation and inventory normalization."""
from __future__ import annotations
import argparse, datetime as dt, json, math, os, shutil, sys, tempfile
from contextlib import contextmanager
from pathlib import Path

GiB = 1024 ** 3
MiB = 1024 ** 2
DEFAULT_SOFT_MIN_BYTES = 20 * GiB
DEFAULT_SOFT_PERCENT = .05
DEFAULT_HARD_MIN_BYTES = GiB
DEFAULT_HARD_PERCENT = .01
DEFAULT_PEAK_OVERHEAD_PERCENT = .25
DEFAULT_PROBE_BYTES = 256 * MiB
MODEL_SUFFIXES = (".gguf", ".safetensors", ".ckpt", ".pt", ".bin", ".pth", ".onnx", ".h5")
MODEL_DIRS = ("checkpoint", "checkpoints", "model-cache", "model_cache", "huggingface", "hf-cache", "transformers", "models", "lm-studio", "lm_studio")
TEXT_RUNTIME_SUFFIXES = {".py", ".js", ".txt"}
PE_RUNTIME_SUFFIXES = {".dll", ".exe"}

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
    write_roots=data.get("write_roots",[])
    if not isinstance(write_roots,list): raise PolicyError("write_roots must be a list")
    for root in write_roots:
        if not isinstance(root,dict): raise PolicyError("write root must be an object")
        absolute_path(root.get("path"))
        purposes=root.get("purposes")
        if not isinstance(purposes,list) or not purposes or not all(p in {"scratch","download","extract","build","cache"} for p in purposes): raise PolicyError("write root needs supported nonempty purposes")
    ids=set()
    for grant in data["action_grants"]:
        if not isinstance(grant,dict) or not isinstance(grant.get("id"),str) or not grant["id"] or grant["id"] in ids: raise PolicyError("grant IDs must be unique and nonempty")
        ids.add(grant["id"]); absolute_path(grant.get("target"))
        if grant.get("action") not in {"delete","move","compress"}: raise PolicyError("unrecognized grant action")
        if grant.get("action") == "move": absolute_path(grant.get("destination"))
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
@contextmanager
def volume_locks(volume_roots, lock_directory):
    """Acquire every affected volume in a stable order, or fail without waiting."""
    ordered=[]
    for root in volume_roots:
        key=os.path.splitdrive(canon(root))[0] or Path(canon(root)).anchor
        if key not in ordered: ordered.append(key)
    held=[]
    try:
        for root in sorted(ordered):
            lock=volume_lock(root,lock_directory); lock.__enter__(); held.append(lock)
        yield
    finally:
        for lock in reversed(held): lock.__exit__(None,None,None)
def find_grant(path, action, policy, grant_id=None, destination=None):
    target = absolute_path(path)
    if protected(target, policy): raise PolicyError("target is protected")
    if model_like(target): raise PolicyError("model/checkpoint/cache target is excluded")
    if not any(is_within(target, root) for root in policy["approved_roots"]): raise PolicyError("target outside approved roots")
    matches=[g for g in policy["action_grants"] if g.get("action")==action and canon(g.get("target", ""))==target and (grant_id is None or g.get("id")==grant_id)]
    if len(matches)!=1: raise PolicyError("no unique exact live action grant")
    grant=matches[0]
    if parse_time(grant["expires_at"]) < now(): raise PolicyError("action grant expired")
    if action == "move":
        if destination is None or "destination" not in grant: raise PolicyError("move grant lacks exact destination binding")
        if canon(grant["destination"]) != absolute_path(destination): raise PolicyError("destination does not match exact move grant")
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
def runtime_content_issue(path):
    """Bounded, conservative content check for the small runtime allowlist."""
    item=Path(path); suffix=item.suffix.lower()
    try:
        with item.open("rb") as stream: sample=stream.read(65536)
    except OSError: return "runtime content unreadable"
    if suffix in TEXT_RUNTIME_SUFFIXES:
        if b"\0" in sample: return "text extension contains NUL/binary content"
        try: sample.decode("utf-8")
        except UnicodeDecodeError: return "text extension is not UTF-8 text"
    elif suffix in PE_RUNTIME_SUFFIXES:
        if not sample.startswith(b"MZ"): return "PE runtime extension lacks MZ signature"
    elif suffix == ".lib":
        if not sample.startswith(b"!<arch>\n"): return "library extension lacks archive signature"
    elif suffix == ".pdb":
        if not sample.startswith(b"Microsoft C/C++ MSF"): return "PDB extension lacks MSF signature"
    else: return "unsupported runtime content type"
    return None
def sha256_file(path):
    import hashlib
    h=hashlib.sha256()
    with Path(path).open("rb") as f:
        for block in iter(lambda:f.read(1024*1024), b""): h.update(block)
    return h.hexdigest()
def copy_verify(source, destination, map_path, grant_id, estimated_peak_bytes, lock_directory, verifier=None, copy_impl=None, state=None, reservation_id=None, ledger=None, _state_locked=False):
    """Stage a copy and hash it; remove only the staged copy if verification fails."""
    src, dst = Path(source), Path(destination)
    if not src.is_file() or dst.exists(): raise PolicyError("source must be a file and destination must not exist")
    copy_impl=copy_impl or shutil.copyfile
    if state is not None and not _state_locked:
        with state_lock(state):
            return copy_verify(src,dst,map_path,grant_id,estimated_peak_bytes,lock_directory,verifier,copy_impl,state,reservation_id,ledger,True)
    effective_peak=max(estimated_peak_bytes,src.stat().st_size)
    with volume_locks((src.parent.anchor,dst.parent.anchor),lock_directory):
     stage=None
     try:
        policy=load_map(map_path)
        find_grant(src,"move",policy,grant_id,dst)
        if is_reparse_point(src) or src.stat().st_nlink>1 or protected(dst,policy) or model_like(src) or model_like(dst) or not any(is_within(dst,r) for r in policy["approved_roots"]): raise PolicyError("source or destination fails shared policy")
        if state is None:
            capacity=preflight(dst.parent,effective_peak,policy)
        else:
            reservations=load_reservations(state)
            entries=[x for x in reservation_entries(reservations,dst.parent) if x["id"] == reservation_id]
            if len(entries) != 1 or entries[0]["bytes"] < peak_reservation_bytes(effective_peak,policy): raise PolicyError("reservation missing or too small for copy")
            capacity=preflight(dst.parent,0,policy,reservation_total(reservations,dst.parent))
        if not capacity["allowed"]: raise PolicyError("destination capacity preflight failed")
        if dst.exists(): raise PolicyError("destination appeared during staging")
        dst.parent.mkdir(parents=True,exist_ok=True)
        fd,name=tempfile.mkstemp(prefix=".storage-stage-",dir=dst.parent); os.close(fd); stage=Path(name)
        journal("copy-intent",{"source":absolute_path(src),"destination":absolute_path(dst),"effective_peak_bytes":effective_peak},ledger)
        copy_impl(src,stage)
        verified=src.stat().st_size == stage.stat().st_size and sha256_file(src) == sha256_file(stage)
        if verifier is not None: verified = verified and bool(verifier(src,stage))
        if not verified: raise PolicyError("copy verification failed")
        os.link(stage,dst); stage.unlink(); stage=None
        return {"copied":True,"source":str(src),"destination":str(dst),"sha256":sha256_file(dst),"capacity":capacity}
     except Exception as e:
        if stage is not None and stage.exists(): stage.unlink()
        journal("copy-failed",{"source":str(src),"destination":str(dst),"error":str(e)},ledger)
        raise
def reservation_settings(policy=None):
    reservations = (policy or {}).get("reservations", {})
    if not isinstance(reservations,dict): raise PolicyError("reservations must be an object")
    values={
        "soft_min_bytes":reservations.get("default_min_bytes",DEFAULT_SOFT_MIN_BYTES),
        "soft_percent":reservations.get("default_percent",DEFAULT_SOFT_PERCENT),
        "hard_min_bytes":reservations.get("hard_min_bytes",DEFAULT_HARD_MIN_BYTES),
        "hard_percent":reservations.get("hard_percent",DEFAULT_HARD_PERCENT),
        "peak_overhead_percent":reservations.get("peak_overhead_percent",DEFAULT_PEAK_OVERHEAD_PERCENT),
        "default_probe_bytes":reservations.get("default_probe_bytes",DEFAULT_PROBE_BYTES),
    }
    for name,value in values.items():
        if not isinstance(value,(int,float)) or not math.isfinite(value) or value < 0: raise PolicyError(f"reservation {name} must be finite and non-negative")
    return values
def peak_reservation_bytes(peak, policy=None):
    if not isinstance(peak,int) or peak < 0: raise PolicyError("peak growth must be a known non-negative integer")
    return int(math.ceil(peak * (1 + reservation_settings(policy)["peak_overhead_percent"])))
def preflight(path, peak, policy=None, reserved_bytes=0):
    if peak is None or not isinstance(peak,int) or peak < 0: raise PolicyError("peak growth must be a known non-negative integer")
    if not isinstance(reserved_bytes,int) or reserved_bytes < 0: raise PolicyError("reserved bytes must be a known non-negative integer")
    usage = shutil.disk_usage(path)
    settings=reservation_settings(policy)
    soft_reserve=max(int(settings["soft_min_bytes"]),int(usage.total * settings["soft_percent"]))
    hard_reserve=max(int(settings["hard_min_bytes"]),int(usage.total * settings["hard_percent"]))
    peak_reservation=peak_reservation_bytes(peak,policy)
    hard_required=hard_reserve + reserved_bytes + peak_reservation
    soft_required=soft_reserve + reserved_bytes + peak_reservation
    if usage.free <= hard_required: status,warning="defer","hard operational headroom cannot cover active reservations and this write peak"
    elif usage.free > soft_required: status,warning="ready",None
    else: status,warning="warning","soft reserve would be crossed; route new work elsewhere when an approved ready volume is available"
    return {"path":canon(path),"total_bytes":usage.total,"free_bytes":usage.free,"reserve_bytes":soft_reserve,"soft_reserve_bytes":soft_reserve,"hard_reserve_bytes":hard_reserve,"active_reservation_bytes":reserved_bytes,"estimated_peak_bytes":peak,"peak_overhead_percent":settings["peak_overhead_percent"],"peak_reservation_bytes":peak_reservation,"required_free_bytes":soft_required,"hard_required_free_bytes":hard_required,"status":status,"warning":warning,"allowed":status != "defer"}
def planning_reservations(state):
    if state is None: return None,"not-supplied"
    try: return load_reservations(state),"available"
    except PolicyError as e: return None,f"unavailable: {e}"
def approved_write_root(path, purpose, policy):
    return any(is_within(path,root["path"]) and purpose in root["purposes"] for root in policy.get("write_roots",[]))
def plan_candidate(path, peak, purpose, policy, reservations):
    target=absolute_path(path); report={"path":target,"approved":False,"allowed":False}
    if not Path(target).is_dir(): report["reason"]="candidate must be an existing directory"; return report
    if is_reparse_point(target): report["reason"]="reparse-point candidate requires separate review"; return report
    if protected(target,policy): report["reason"]="candidate is protected"; return report
    if model_like(target): report["reason"]="model/checkpoint/cache candidate is excluded"; return report
    if not approved_write_root(target,purpose,policy): report["reason"]="candidate is outside an approved write root for this purpose"; return report
    active=reservation_total(reservations,target) if reservations is not None else 0
    capacity=preflight(target,peak,policy,active)
    report.update({"approved":True,"allowed":capacity["allowed"],"status":capacity["status"],"capacity":capacity})
    return report
def plan_write(map_path,path,estimated_peak_bytes=None,candidate_paths=(),state=None,probe_bytes=None,purpose="scratch"):
    """Read-only routing advice; reserve again immediately before the chosen write."""
    if purpose not in {"scratch","download","extract","build","cache"}: raise PolicyError("unsupported write purpose")
    policy=load_map(map_path); settings=reservation_settings(policy)
    unknown=estimated_peak_bytes is None
    if unknown:
        probe_bytes=settings["default_probe_bytes"] if probe_bytes is None else probe_bytes
        if not isinstance(probe_bytes,int) or probe_bytes <= 0: raise PolicyError("unknown peak requires a positive bounded probe estimate")
        peak=probe_bytes
    else:
        if not isinstance(estimated_peak_bytes,int) or estimated_peak_bytes < 0: raise PolicyError("estimated peak must be a known non-negative integer")
        peak=estimated_peak_bytes
    reservations,reservation_state=planning_reservations(state)
    candidates=[]; seen=set()
    for raw in (path,*candidate_paths):
        target=absolute_path(raw)
        if target not in seen: candidates.append(plan_candidate(target,peak,purpose,policy,reservations)); seen.add(target)
    primary=candidates[0]; ready=[c for c in candidates if c["allowed"] and c.get("status")=="ready"]
    alternate=next((c for c in ready if c["path"] != primary["path"]),None)
    any_allowed=next((c for c in candidates if c["allowed"]),None)
    if unknown:
        decision="bounded-probe-and-estimate" if any_allowed else "defer-affected-write"
        recommended=primary if primary["allowed"] and primary.get("status")=="ready" else alternate or (primary if primary["allowed"] else any_allowed)
    elif primary["allowed"] and primary.get("status")=="ready":
        decision="continue-primary"; recommended=primary
    elif alternate is not None:
        decision="route-new-work-to-approved-alternative"; recommended=alternate
    elif primary["allowed"]:
        decision="continue-primary-with-soft-warning"; recommended=primary
    elif any_allowed is not None:
        decision="route-new-work-to-approved-alternative"; recommended=any_allowed
    else:
        decision="defer-affected-write"; recommended=None
    return {"read_only":True,"purpose":purpose,"estimated_peak_known":not unknown,"planning_peak_bytes":peak,"reservation_state":reservation_state,"candidates":candidates,"decision":decision,"recommended_path":recommended and recommended["path"],"continue_unrelated_work":True,"requires_fresh_reservation_before_write":True,"note":"This is a capacity snapshot, not permission to create, move, delete, or reconfigure data."}
def runtime_root(): return Path.home()/".storage-awareness"
def journal(event, payload, ledger=None):
    target=Path(ledger) if ledger else runtime_root()/"ledger.jsonl"
    target.parent.mkdir(parents=True,exist_ok=True)
    with target.open("a",encoding="utf-8") as f:
        f.write(json.dumps({"at":now().isoformat(),"event":event,**payload})+"\n"); f.flush(); os.fsync(f.fileno())
def default_state(): return runtime_root()/"reservations.json"
@contextmanager
def state_lock(state):
    """One lock for the shared state file; volume locks alone cannot serialize cross-volume writers."""
    target=Path(state) if state else default_state(); lock=target.with_name(target.name+".lock")
    try:
        lock.parent.mkdir(parents=True,exist_ok=True)
        fd=os.open(lock,os.O_CREAT|os.O_EXCL|os.O_WRONLY)
    except FileExistsError: raise PolicyError(f"reservation state lock unavailable: {lock}")
    try:
        os.write(fd,str(os.getpid()).encode()); yield
    finally:
        os.close(fd)
        try: lock.unlink()
        except FileNotFoundError: pass
def volume_key(path):
    value=os.path.splitdrive(canon(path))[0] or Path(canon(path)).anchor
    return value.lower()
def load_reservations(state, *, create=False):
    path=Path(state) if state else default_state()
    if not path.exists():
        if create: return {"schema_version":1,"reservations":{},"transactions":{}}
        raise PolicyError("reservation state missing")
    try: data=json.loads(path.read_text(encoding="utf-8"))
    except (OSError,json.JSONDecodeError) as e: raise PolicyError(f"reservation state unreadable: {e}")
    if data.get("schema_version") != 1 or not isinstance(data.get("reservations"),dict): raise PolicyError("reservation state invalid")
    data.setdefault("transactions",{})
    if not isinstance(data["transactions"],dict): raise PolicyError("reservation state invalid")
    seen=set()
    for volume, entries in data["reservations"].items():
        if not isinstance(volume,str) or not isinstance(entries,list): raise PolicyError("reservation state invalid")
        for entry in entries:
            if not isinstance(entry,dict) or not isinstance(entry.get("id"),str) or entry["id"] in seen or not isinstance(entry.get("bytes"),int) or entry["bytes"] < 0: raise PolicyError("reservation state invalid")
            seen.add(entry["id"])
    for tx_id, tx in data["transactions"].items():
        if not isinstance(tx_id,str) or not tx_id or not isinstance(tx,dict): raise PolicyError("transaction state invalid")
        if tx.get("status") not in {"staged","finalized"}: raise PolicyError("transaction state invalid")
        for key in ("source","destination","grant_id","reservation_id","sha256"):
            if not isinstance(tx.get(key),str) or not tx[key]: raise PolicyError("transaction state invalid")
        if not isinstance(tx.get("peak_reservation_bytes"),int) or tx["peak_reservation_bytes"] < 0: raise PolicyError("transaction state invalid")
        absolute_path(tx["source"]); absolute_path(tx["destination"])
    return data
def write_reservations(state, data):
    path=Path(state) if state else default_state(); path.parent.mkdir(parents=True,exist_ok=True)
    fd,name=tempfile.mkstemp(prefix=f".{path.name}.{os.getpid()}.",suffix=".tmp",dir=path.parent)
    try:
        with os.fdopen(fd,"w",encoding="utf-8") as f:
            json.dump(data,f,indent=2); f.flush(); os.fsync(f.fileno())
        os.replace(name,path)
    finally:
        if os.path.exists(name): os.unlink(name)
def reservation_entries(data, path): return data["reservations"].get(volume_key(path),[])
def reservation_total(data, path): return sum(x["bytes"] for x in reservation_entries(data,path))
def reserve(map_path,path,reservation_id,peak,lock_directory,state=None,ledger=None):
    target=absolute_path(path)
    if model_like(target): raise PolicyError("model/checkpoint/cache target is excluded")
    if not isinstance(reservation_id,str) or not reservation_id: raise PolicyError("reservation id must be nonempty")
    with state_lock(state):
      with volume_lock(Path(target).anchor,lock_directory):
        policy=load_map(map_path); data=load_reservations(state,create=True)
        if any(x["id"] == reservation_id for rows in data["reservations"].values() for x in rows): raise PolicyError("reservation id already exists")
        active=reservation_total(data,target); result=preflight(target,peak,policy,active)
        if not result["allowed"]: raise PolicyError("capacity preflight failed")
        entry={"id":reservation_id,"bytes":result["peak_reservation_bytes"],"created_at":now().isoformat()}
        data["reservations"].setdefault(volume_key(target),[]).append(entry); write_reservations(state,data)
        journal("reservation-created",{"reservation_id":reservation_id,"volume":volume_key(target),"bytes":entry["bytes"],"capacity":result},ledger); return entry
def release_reservation(path,reservation_id,lock_directory,state=None,ledger=None):
    target=absolute_path(path)
    with state_lock(state):
      with volume_lock(Path(target).anchor,lock_directory):
        data=load_reservations(state); key=volume_key(target); entries=data["reservations"].get(key,[])
        retained=[entry for entry in entries if entry["id"] != reservation_id]
        if len(retained) == len(entries): raise PolicyError("reservation id not found on target volume")
        data["reservations"][key]=retained; write_reservations(state,data)
        journal("reservation-released",{"reservation_id":reservation_id,"volume":key},ledger); return {"released":reservation_id}
def checkpoint(map_path,path,peak,lock_directory,ledger=None,state=None,reservation_id=None):
    target=absolute_path(path)
    if model_like(target): raise PolicyError("model/checkpoint/cache target is excluded")
    with state_lock(state):
      with volume_lock(Path(target).anchor,lock_directory):
        policy=load_map(map_path); data=load_reservations(state)
        if reservation_id is not None:
            entries=[x for x in reservation_entries(data,target) if x["id"] == reservation_id]
            if len(entries) != 1 or entries[0]["bytes"] < peak_reservation_bytes(peak,policy): raise PolicyError("reservation missing or too small for checkpoint")
            peak=0
        result=preflight(target,peak,policy,reservation_total(data,target)); journal("capacity-checkpoint",{"reservation_id":reservation_id,**result},ledger)
        if not result["allowed"]: raise PolicyError("capacity checkpoint failed")
        return result
def delete_owned(map_path,path,grant_id,peak,lock_directory,ledger=None):
    raw=Path(path)
    if is_reparse_point(raw) or not raw.is_file(): raise PolicyError("delete target must be a regular file")
    target=absolute_path(raw)
    with volume_lock(raw.anchor,lock_directory):
        policy=load_map(map_path); find_grant(target,"delete",policy,grant_id)
        if raw.stat().st_nlink>1: raise PolicyError("hardlink target requires separate review")
        journal("owned-delete-intent",{"target":target,"grant_id":grant_id},ledger)
        try: raw.unlink()
        except OSError as e:
            journal("owned-delete-failed",{"target":target,"grant_id":grant_id,"error":str(e)},ledger); raise
        journal("owned-delete",{"target":target,"grant_id":grant_id,"outcome":"deleted"},ledger); return {"deleted":target}
def stage_relocation(map_path,source,destination,grant_id,peak,lock_directory,*,state,reservation_id,transaction_id,ledger=None,verifier=None,copy_impl=None):
    """Stage a verified copy only. Finalization is a separate reviewed operation."""
    src,dst=Path(source),Path(destination)
    if not src.is_file() or is_reparse_point(src) or src.stat().st_nlink > 1: raise PolicyError("relocation source must be an unlinked regular file")
    if not isinstance(transaction_id,str) or not transaction_id: raise PolicyError("transaction id must be nonempty")
    with state_lock(state):
        data=load_reservations(state)
        if transaction_id in data["transactions"]: raise PolicyError("transaction id already exists")
        staged=copy_verify(src,dst,map_path,grant_id,peak,lock_directory,verifier,copy_impl,state=state,reservation_id=reservation_id,ledger=ledger,_state_locked=True)
        tx={"status":"staged","source":absolute_path(src),"destination":absolute_path(dst),"grant_id":grant_id,"reservation_id":reservation_id,"sha256":staged["sha256"],"peak_reservation_bytes":max(peak,src.stat().st_size),"config_disposition":"not-run","smoke_disposition":"not-run","staged_at":now().isoformat()}
        data["transactions"][transaction_id]=tx; write_reservations(state,data)
        journal("relocation-staged",{"transaction_id":transaction_id,"source_retained":True,**tx},ledger)
        return {"transaction_id":transaction_id,"finalized":False,"source_retained":True,"recovery":"source and verified staged destination retained",**staged}
def record_relocation_disposition(transaction_id,state,config_disposition,smoke_disposition,ledger=None):
    if config_disposition not in {"passed","failed"} or smoke_disposition not in {"passed","failed"}: raise PolicyError("dispositions must be reviewed passed or failed")
    with state_lock(state):
        data=load_reservations(state); tx=data["transactions"].get(transaction_id)
        if not tx or tx["status"] != "staged": raise PolicyError("transaction is not staged")
        tx["config_disposition"],tx["smoke_disposition"]=config_disposition,smoke_disposition
        if "failed" in {config_disposition,smoke_disposition}:
            key=volume_key(tx["destination"]); entries=data["reservations"].get(key,[])
            data["reservations"][key]=[entry for entry in entries if entry["id"] != tx["reservation_id"]]
            journal("reservation-released",{"reservation_id":tx["reservation_id"],"volume":key,"reason":"relocation disposition failed; source and staged copy retained"},ledger)
        write_reservations(state,data)
        journal("relocation-disposition",{"transaction_id":transaction_id,"config_disposition":config_disposition,"smoke_disposition":smoke_disposition},ledger); return tx
def finalize_relocation(map_path,transaction_id,lock_directory,*,state,ledger=None):
    with state_lock(state):
      data=load_reservations(state); tx=data["transactions"].get(transaction_id)
      if not tx or tx["status"] != "staged": raise PolicyError("transaction is not staged")
      if tx["config_disposition"] != "passed" or tx["smoke_disposition"] != "passed": raise PolicyError("reviewed config and smoke dispositions have not both passed")
      src,dst=Path(tx["source"]),Path(tx["destination"])
      with volume_locks((src.parent.anchor,dst.parent.anchor),lock_directory):
        policy=load_map(map_path); find_grant(src,"move",policy,tx["grant_id"],dst)
        entries=[x for x in reservation_entries(data,dst.parent) if x["id"] == tx["reservation_id"]]
        if len(entries) != 1 or entries[0]["bytes"] < peak_reservation_bytes(tx["peak_reservation_bytes"],policy): raise PolicyError("reservation missing or too small for finalization")
        if (not src.is_file() or is_reparse_point(src) or src.stat().st_nlink > 1 or not dst.is_file() or is_reparse_point(dst) or dst.stat().st_nlink > 1 or protected(dst,policy) or model_like(dst) or not any(is_within(dst,root) for root in policy["approved_roots"]) or sha256_file(src) != tx["sha256"] or sha256_file(dst) != tx["sha256"]): raise PolicyError("source or staged destination changed before finalization")
        journal("relocation-finalize-intent",{"transaction_id":transaction_id,"source":tx["source"]},ledger)
        try: src.unlink()
        except OSError as e:
            journal("relocation-finalize-failed",{"transaction_id":transaction_id,"error":str(e)},ledger); raise
        key=volume_key(dst.parent); data["reservations"][key]=[entry for entry in data["reservations"].get(key,[]) if entry["id"] != tx["reservation_id"]]
        tx["status"]="finalized"; tx["finalized_at"]=now().isoformat(); write_reservations(state,data)
        journal("reservation-released",{"reservation_id":tx["reservation_id"],"volume":key,"reason":"relocation finalized"},ledger)
        journal("relocation-finalized",{"transaction_id":transaction_id,"source_deleted":tx["source"],"destination":tx["destination"]},ledger)
        return {"transaction_id":transaction_id,"finalized":True,"source_deleted":tx["source"],"destination":tx["destination"]}
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
    q=sub.add_parser("plan-write"); q.add_argument("--map",required=True); q.add_argument("--path",required=True); q.add_argument("--purpose",choices=("scratch","download","extract","build","cache"),required=True); q.add_argument("--estimated-peak-bytes",type=int); q.add_argument("--candidate-path",action="append",default=[]); q.add_argument("--probe-bytes",type=int); q.add_argument("--state")
    q=sub.add_parser("check-mutation"); q.add_argument("--map", required=True); q.add_argument("--path", required=True); q.add_argument("--action", choices=("delete","move"), required=True); q.add_argument("--estimated-peak-bytes",type=int,required=True); q.add_argument("--lock-directory",default=str(Path.home()/".storage-awareness"/"locks")); q.add_argument("--grant-id")
    q=sub.add_parser("audit-inventory"); q.add_argument("--input", required=True); q.add_argument("--output", required=True)
    q=sub.add_parser("reserve"); q.add_argument("--map",required=True); q.add_argument("--path",required=True); q.add_argument("--reservation-id",required=True); q.add_argument("--estimated-peak-bytes",type=int,required=True); q.add_argument("--lock-directory",default=str(runtime_root()/"locks")); q.add_argument("--state",default=str(default_state())); q.add_argument("--ledger")
    q=sub.add_parser("release-reservation"); q.add_argument("--path",required=True); q.add_argument("--reservation-id",required=True); q.add_argument("--lock-directory",default=str(runtime_root()/"locks")); q.add_argument("--state",default=str(default_state())); q.add_argument("--ledger")
    q=sub.add_parser("checkpoint"); q.add_argument("--map",required=True); q.add_argument("--path",required=True); q.add_argument("--estimated-peak-bytes",type=int,required=True); q.add_argument("--lock-directory",default=str(runtime_root()/"locks")); q.add_argument("--state",default=str(default_state())); q.add_argument("--reservation-id"); q.add_argument("--ledger")
    q=sub.add_parser("delete-owned"); q.add_argument("--map",required=True); q.add_argument("--path",required=True); q.add_argument("--grant-id",required=True); q.add_argument("--estimated-peak-bytes",type=int,required=True); q.add_argument("--lock-directory",default=str(runtime_root()/"locks")); q.add_argument("--ledger")
    q=sub.add_parser("stage-relocation"); q.add_argument("--map",required=True); q.add_argument("--source",required=True); q.add_argument("--destination",required=True); q.add_argument("--grant-id",required=True); q.add_argument("--reservation-id",required=True); q.add_argument("--transaction-id",required=True); q.add_argument("--estimated-peak-bytes",type=int,required=True); q.add_argument("--lock-directory",default=str(runtime_root()/"locks")); q.add_argument("--state",default=str(default_state())); q.add_argument("--ledger")
    q=sub.add_parser("record-relocation-disposition"); q.add_argument("--transaction-id",required=True); q.add_argument("--state",default=str(default_state())); q.add_argument("--ledger"); q.add_argument("--config-disposition",choices=("passed","failed"),required=True); q.add_argument("--smoke-disposition",choices=("passed","failed"),required=True)
    q=sub.add_parser("finalize-relocation"); q.add_argument("--map",required=True); q.add_argument("--transaction-id",required=True); q.add_argument("--lock-directory",default=str(runtime_root()/"locks")); q.add_argument("--state",default=str(default_state())); q.add_argument("--ledger")
    a=p.parse_args()
    try:
        if a.cmd == "validate-map": result={"valid": True, "schema_version": load_map(a.map)["schema_version"]}
        elif a.cmd == "preflight": result=preflight(a.path,a.estimated_peak_bytes,load_map(a.map) if a.map else None)
        elif a.cmd == "plan-write": result=plan_write(a.map,a.path,a.estimated_peak_bytes,a.candidate_path,a.state,a.probe_bytes,a.purpose)
        elif a.cmd == "check-mutation":
            if is_reparse_point(a.path): raise PolicyError("reparse-point target requires separate review")
            target=absolute_path(a.path)
            with volume_lock(Path(target).anchor,a.lock_directory):
                policy=load_map(a.map); grant_id=mutation_allowed(target,a.action,policy,a.grant_id); capacity=preflight(target,a.estimated_peak_bytes,policy)
                if not capacity["allowed"]: raise PolicyError("capacity preflight failed")
                if Path(target).is_dir() and tree_issues(target,policy): raise PolicyError("recursive target contains unsafe descendants")
                if Path(target).is_file() and Path(target).stat().st_nlink > 1: raise PolicyError("hardlink target requires separate review")
                result={"allowed":True,"grant_id":grant_id,"capacity":capacity}
        elif a.cmd == "reserve": result=reserve(a.map,a.path,a.reservation_id,a.estimated_peak_bytes,a.lock_directory,a.state,a.ledger)
        elif a.cmd == "release-reservation": result=release_reservation(a.path,a.reservation_id,a.lock_directory,a.state,a.ledger)
        elif a.cmd == "checkpoint": result=checkpoint(a.map,a.path,a.estimated_peak_bytes,a.lock_directory,a.ledger,a.state,a.reservation_id)
        elif a.cmd == "delete-owned": result=delete_owned(a.map,a.path,a.grant_id,a.estimated_peak_bytes,a.lock_directory,a.ledger)
        elif a.cmd == "stage-relocation": result=stage_relocation(a.map,a.source,a.destination,a.grant_id,a.estimated_peak_bytes,a.lock_directory,state=a.state,reservation_id=a.reservation_id,transaction_id=a.transaction_id,ledger=a.ledger)
        elif a.cmd == "record-relocation-disposition": result=record_relocation_disposition(a.transaction_id,a.state,a.config_disposition,a.smoke_disposition,a.ledger)
        elif a.cmd == "finalize-relocation": result=finalize_relocation(a.map,a.transaction_id,a.lock_directory,state=a.state,ledger=a.ledger)
        else:
            raw=json.loads(Path(a.input).read_text(encoding="utf-8")); items=raw.get("items", raw if isinstance(raw,list) else [])
            if not isinstance(items,list): raise PolicyError("inventory items must be a list")
            links=raw.get("hardlinkEvidence",raw.get("hardlink_evidence",[])) if isinstance(raw,dict) else []
            result={"schema_version":1,"generated_at":now().isoformat(),"source_metadata":{"mode":raw.get("mode"),"limitations":raw.get("limitations",[]),"known_subtotals":raw.get("knownSubtotals",raw.get("known_subtotals",[]))},"hardlink_evidence":links,"items":[normalized_item(i,links) for i in items]}; Path(a.output).write_text(json.dumps(result,indent=2),encoding="utf-8")
        print(json.dumps(result, indent=2))
    except PolicyError as e: print(json.dumps({"allowed":False,"error":str(e)})); return 2
    return 0
if __name__ == "__main__": sys.exit(main())
