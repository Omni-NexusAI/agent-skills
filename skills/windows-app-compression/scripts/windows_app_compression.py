#!/usr/bin/env python3
"""Analysis-first Windows compact.exe gate using the shared storage policy."""
from __future__ import annotations
import argparse, importlib.util, json, os, subprocess, sys
from pathlib import Path
SUPPORTED_EXTENSIONS={".dll",".exe",".lib",".pdb",".js",".py",".txt"}
def load_guard(root):
 f=Path(root)/"scripts"/"storage_guard.py"; spec=importlib.util.spec_from_file_location("storage_guard",f)
 if not f.is_file() or spec is None: raise RuntimeError("storage-awareness helper unavailable")
 m=importlib.util.module_from_spec(spec); spec.loader.exec_module(m); return m
def summary(target, guard):
 root=Path(target)
 if not root.is_dir(): raise RuntimeError("target must be an existing directory")
 files=list(root.rglob("*")); regular=[f for f in files if f.is_file()]
 excluded=[str(f) for f in regular if guard.model_like(f)]
 hardlinks=[str(f) for f in regular if f.stat().st_nlink > 1]
 logical=sum(f.stat().st_size for f in regular)
 return {"target":guard.canon(root),"logical_bytes":logical,"allocated_bytes":None,"allocation_measured":False,"compression_state":"unknown","compression_confidence":"unknown","regular_file_count":len(regular),"model_exclusion_count":len(excluded),"model_exclusion_examples":excluded[:20],"hardlink_count":len(hardlinks),"hardlink_examples":hardlinks[:20],"eligible_for_execution":False if excluded or hardlinks else None,"note":"Run a bounded measured test and app smoke check; no savings estimate is inferred. Any model content or hardlink requires an exact narrower review."}
def execution_issues(target, guard, allowlist, policy=None):
 policy=policy or {"protected_paths":[],"approved_roots":[str(target)],"action_grants":[]}
 issues=guard.tree_issues(target,policy,allowlist)
 for item in Path(target).rglob("*"):
  if item.is_file() and not guard.is_reparse_point(item) and item.suffix.lower() in allowlist:
   reason=guard.runtime_content_issue(item)
   if reason: issues.append((str(item),reason))
 return issues
def main():
 p=argparse.ArgumentParser(); s=p.add_subparsers(dest="cmd",required=True)
 for name in ("analyze","execute"):
  q=s.add_parser(name); q.add_argument("--target",required=True); q.add_argument("--storage-awareness-path",required=True); q.add_argument("--map"); q.add_argument("--algorithm",choices=("XPRESS4K","XPRESS8K","XPRESS16K","LZX")); q.add_argument("--approval-id"); q.add_argument("--allow-execute",action="store_true"); q.add_argument("--estimated-peak-bytes",type=int); q.add_argument("--lock-directory",default=str(Path.home()/".storage-awareness"/"locks")); q.add_argument("--state",default=str(Path.home()/".storage-awareness"/"reservations.json")); q.add_argument("--reservation-id")
 a=p.parse_args(); guard=load_guard(a.storage_awareness_path); result=summary(a.target,guard)
 if a.cmd=="execute":
  if not a.map or not a.algorithm or not a.approval_id or not a.reservation_id: raise RuntimeError("execute requires map, exact approval-id, reservation-id, and algorithm")
  if not a.allow_execute: raise RuntimeError("execute requires explicit --allow-execute after target review")
  if a.estimated_peak_bytes is None: raise RuntimeError("execute requires a measured non-negative peak estimate")
  if guard.is_reparse_point(a.target): raise RuntimeError("reparse-point target requires separate review")
  target=guard.absolute_path(a.target)
  guard.journal("compression-intent",{"target":target,"grant_id":a.approval_id,"reservation_id":a.reservation_id,"algorithm":a.algorithm},None)
  reserved=False
  try:
   guard.reserve(a.map,target,a.reservation_id,a.estimated_peak_bytes,a.lock_directory,a.state); reserved=True
   with guard.state_lock(a.state), guard.volume_lock(Path(target).anchor,a.lock_directory):
     policy=guard.load_map(a.map)
     grant=guard.find_grant(target,"compress",policy,a.approval_id)
     extensions=grant.get("allowed_extensions")
     if not isinstance(extensions,list) or not extensions or not all(isinstance(x,str) and x.startswith(".") for x in extensions): raise RuntimeError("compression grant needs a nonempty allowed_extensions list")
     reservations=guard.load_reservations(a.state)
     capacity=guard.preflight(target,0,policy,guard.reservation_total(reservations,target))
     if not capacity["allowed"]: raise RuntimeError("capacity preflight failed")
     allowlist={x.lower() for x in extensions} & SUPPORTED_EXTENSIONS
     if not allowlist: raise RuntimeError("grant allowlist has no supported runtime content types")
     issues=execution_issues(target,guard,allowlist,policy)
     if issues: raise RuntimeError("recursive target contains protected, model, hardlink, reparse-point, or unallowlisted descendants")
     if os.name != "nt": raise RuntimeError("compact.exe execution is Windows-only")
     completed=subprocess.run(["compact.exe","/c",f"/s:{target}",f"/exe:{a.algorithm}"],capture_output=True,text=True,check=False)
     result.update({"executed":True,"returncode":completed.returncode,"stdout":completed.stdout,"stderr":completed.stderr,"capacity":capacity})
     if completed.returncode: raise RuntimeError("compact.exe failed; stop and investigate before retry")
     guard.journal("compression-complete",{"target":target,"grant_id":a.approval_id,"algorithm":a.algorithm,"returncode":completed.returncode},None)
  except Exception as e:
   guard.journal("compression-failed",{"target":target,"grant_id":a.approval_id,"error":str(e),"recovery":"no source deletion; inspect target before retry"},None)
   raise
  finally:
   if reserved: guard.release_reservation(target,a.reservation_id,a.lock_directory,a.state)
 print(json.dumps(result,indent=2)); return 0
if __name__=="__main__":
 try: sys.exit(main())
 except (RuntimeError, OSError) as e: print(json.dumps({"allowed":False,"error":str(e)})); sys.exit(2)
