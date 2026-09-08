import importlib.util, json, tempfile, unittest
from collections import namedtuple
from datetime import datetime, timedelta, timezone
from pathlib import Path
from unittest import mock
SPEC=importlib.util.spec_from_file_location("guard",Path(__file__).parents[1]/"scripts"/"storage_guard.py"); guard=importlib.util.module_from_spec(SPEC); SPEC.loader.exec_module(guard)
_RUNTIME=tempfile.TemporaryDirectory(prefix=".storage-guard-tests-",dir=str(Path(__file__).parents[3])); _DEFAULT_LEDGER=Path(_RUNTIME.name)/"ledger.jsonl"; _journal=guard.journal
def isolated_journal(event,payload,ledger=None): return _journal(event,payload,ledger or _DEFAULT_LEDGER)
guard.journal=isolated_journal
def policy(**extra):
 d={"schema_version":1,"generated_at":datetime.now(timezone.utc).isoformat(),"protected_paths":["C:/safe"],"approved_roots":["C:/work"],"action_grants":[],"reservations":{}}; d.update(extra); return d
class GuardTests(unittest.TestCase):
 def copy_args(self,src,dst,root):
  p=policy(protected_paths=[],approved_roots=[str(root)],action_grants=[{"id":"move","action":"move","target":str(src),"destination":str(dst),"agent_owned":True,"positively_disposable":True,"recovery_retained":True,"expires_at":(datetime.now(timezone.utc)+timedelta(hours=1)).isoformat()}])
  m=root/"policy.json"; m.write_text(json.dumps(p)); return m,"move",0,str(root/"locks")
 def test_protected_alias_wins(self):
  p=policy(action_grants=[{"id":"x","action":"delete","target":"C:/safe/file","agent_owned":True,"positively_disposable":True,"recovery_retained":True,"expires_at":(datetime.now(timezone.utc)+timedelta(hours=1)).isoformat()}])
  with self.assertRaises(guard.PolicyError): guard.mutation_allowed("C:/safe/file","delete",p)
 def test_model_is_excluded(self): self.assertTrue(guard.model_like("C:/work/models/a.gguf"))
 def test_stale_map_fails_closed(self):
  with tempfile.TemporaryDirectory() as d:
   f=Path(d)/"p.json"; f.write_text(json.dumps(policy(generated_at="2000-01-01T00:00:00Z")))
   with self.assertRaises(guard.PolicyError): guard.load_map(f)
 def test_missing_grant_fails_closed(self):
  with self.assertRaises(guard.PolicyError): guard.mutation_allowed("C:/work/a","delete",policy())
 def test_unknown_inventory_is_not_actionable(self): self.assertEqual(guard.normalized_item({"path":"C:/x","category":"nonsense"})["category"],"unknown")
 def test_camelcase_inventory_is_normalized(self):
  x=guard.normalized_item({"path":"C:/cache","logicalBytes":12,"allocatedBytes":None,"confidence":"medium","category":"runtime cache; compression review","compressionAnalysis":"candidate for trial"})
  self.assertEqual((x["logical_bytes"],x["category"]),(12,"compression_analysis"))
 def test_contention_fails_closed(self):
  with tempfile.TemporaryDirectory() as d:
   with guard.volume_lock("C:/",d):
    with self.assertRaises(guard.PolicyError):
     with guard.volume_lock("C:/",d): pass
 def test_insufficient_capacity_is_not_allowed(self):
  r=guard.preflight(".",10**30); self.assertFalse(r["allowed"]); self.assertEqual(r["status"],"defer")
 def disk(self,free,total=100*guard.GiB): return namedtuple("DiskUsage","total used free")(total,total-free,free)
 def test_soft_reserve_warning_allows_bounded_reservation(self):
  with tempfile.TemporaryDirectory() as d:
   root=Path(d); m=root/"policy.json"; m.write_text(json.dumps(policy(protected_paths=[],approved_roots=[str(root)],reservations={"default_min_bytes":20*guard.GiB,"default_percent":.05,"hard_min_bytes":guard.GiB,"hard_percent":.01}))); state=root/"state.json"
   with mock.patch.object(guard.shutil,"disk_usage",return_value=self.disk(10*guard.GiB)):
    entry=guard.reserve(m,root,"soft-warning",guard.GiB,str(root/"locks"),state)
   self.assertEqual(entry["id"],"soft-warning")
 def test_hard_margin_wins_when_soft_reserve_is_configured_lower(self):
  with mock.patch.object(guard.shutil,"disk_usage",return_value=self.disk(guard.GiB//2)):
   result=guard.preflight(".",0,policy(reservations={"default_min_bytes":0,"default_percent":0,"hard_min_bytes":guard.GiB,"hard_percent":0}))
  self.assertFalse(result["allowed"]); self.assertEqual(result["status"],"defer")
 def test_custom_peak_overhead_is_used_for_checkpoint_reservation(self):
  with tempfile.TemporaryDirectory() as d:
   root=Path(d); m=root/"policy.json"; state=root/"state.json"; p=policy(protected_paths=[],approved_roots=[str(root)],reservations={"default_min_bytes":0,"default_percent":0,"hard_min_bytes":0,"hard_percent":0,"peak_overhead_percent":.1}); m.write_text(json.dumps(p))
   entry=guard.reserve(m,root,"custom-overhead",10,str(root/"locks"),state)
   self.assertEqual(entry["bytes"],11); self.assertTrue(guard.checkpoint(m,root,10,str(root/"locks"),state=state,reservation_id="custom-overhead")["allowed"])
 def test_hard_capacity_defers_only_affected_write(self):
  with tempfile.TemporaryDirectory() as d:
   root=Path(d); primary=root/"primary"; alternate=root/"alternate"; primary.mkdir(); alternate.mkdir(); m=root/"policy.json"
   p=policy(protected_paths=[],approved_roots=[],write_roots=[{"path":str(primary),"purposes":["build"]},{"path":str(alternate),"purposes":["build"]}],reservations={"default_min_bytes":20*guard.GiB,"default_percent":.05,"hard_min_bytes":guard.GiB,"hard_percent":.01}); m.write_text(json.dumps(p))
   with mock.patch.object(guard.shutil,"disk_usage",return_value=self.disk(2*guard.GiB)):
    result=guard.plan_write(m,primary,guard.GiB,[alternate],purpose="build")
   self.assertEqual(result["decision"],"defer-affected-write"); self.assertTrue(result["continue_unrelated_work"])
 def test_plan_routes_new_work_from_warning_to_ready_alternative(self):
  with tempfile.TemporaryDirectory() as d:
   root=Path(d); primary=root/"primary"; alternate=root/"alternate"; primary.mkdir(); alternate.mkdir(); m=root/"policy.json"
   p=policy(protected_paths=[],approved_roots=[],write_roots=[{"path":str(primary),"purposes":["build"]},{"path":str(alternate),"purposes":["build"]}],reservations={"default_min_bytes":20*guard.GiB,"default_percent":.05,"hard_min_bytes":guard.GiB,"hard_percent":.01}); m.write_text(json.dumps(p))
   def usage(path): return self.disk(10*guard.GiB if guard.canon(path)==guard.canon(primary) else 30*guard.GiB)
   with mock.patch.object(guard.shutil,"disk_usage",side_effect=usage): result=guard.plan_write(m,primary,guard.GiB,[alternate],purpose="build")
   self.assertEqual(result["decision"],"route-new-work-to-approved-alternative"); self.assertEqual(result["recommended_path"],guard.canon(alternate)); self.assertEqual(result["candidates"][0]["status"],"warning")
 def test_plan_counts_reservations_on_their_own_volume_only(self):
  with tempfile.TemporaryDirectory() as d:
   root=Path(d); primary=root/"primary"; alternate=root/"alternate"; primary.mkdir(); alternate.mkdir(); m=root/"policy.json"; state=root/"state.json"
   p=policy(protected_paths=[],approved_roots=[],write_roots=[{"path":str(primary),"purposes":["build"]},{"path":str(alternate),"purposes":["build"]}],reservations={"default_min_bytes":20*guard.GiB,"default_percent":.05,"hard_min_bytes":guard.GiB,"hard_percent":.01}); m.write_text(json.dumps(p)); state.write_text(json.dumps({"schema_version":1,"reservations":{"c":[{"id":"existing-c","bytes":28*guard.GiB}],"e":[]},"transactions":{}}))
   def volume(path): return "c" if guard.is_within(path,primary) else "e"
   with mock.patch.object(guard,"volume_key",side_effect=volume), mock.patch.object(guard.shutil,"disk_usage",return_value=self.disk(30*guard.GiB)):
    result=guard.plan_write(m,primary,guard.GiB,[alternate],state=state,purpose="build")
   self.assertEqual(result["decision"],"route-new-work-to-approved-alternative"); self.assertEqual(result["recommended_path"],guard.canon(alternate)); self.assertFalse(result["candidates"][0]["allowed"]); self.assertTrue(result["candidates"][1]["allowed"])
 def test_plan_rejects_unapproved_or_wrong_purpose_candidates(self):
  with tempfile.TemporaryDirectory() as d:
   root=Path(d); build=root/"build"; other=root/"other"; build.mkdir(); other.mkdir(); m=root/"policy.json"; m.write_text(json.dumps(policy(protected_paths=[],approved_roots=[],write_roots=[{"path":str(build),"purposes":["build"]}],reservations={"default_min_bytes":0,"default_percent":0,"hard_min_bytes":0,"hard_percent":0})))
   result=guard.plan_write(m,build,0,[other],purpose="cache")
   self.assertEqual(result["decision"],"defer-affected-write"); self.assertTrue(all(not item["approved"] for item in result["candidates"]))
 def test_unknown_peak_uses_bounded_probe_without_writing_state(self):
  with tempfile.TemporaryDirectory() as d:
   root=Path(d); target=root/"target"; target.mkdir(); m=root/"policy.json"; state=root/"state.json"; m.write_text(json.dumps(policy(protected_paths=[],approved_roots=[],write_roots=[{"path":str(target),"purposes":["cache"]}],reservations={"default_min_bytes":0,"default_percent":0,"hard_min_bytes":0,"hard_percent":0,"default_probe_bytes":64*guard.MiB})))
   with mock.patch.object(guard.shutil,"disk_usage",return_value=self.disk(2*guard.GiB)): result=guard.plan_write(m,target,state=state,purpose="cache")
   self.assertEqual(result["decision"],"bounded-probe-and-estimate"); self.assertEqual(result["planning_peak_bytes"],64*guard.MiB); self.assertFalse(state.exists())
 def test_negative_peak_is_rejected(self):
  with self.assertRaises(guard.PolicyError): guard.preflight(".",-1)
 def test_volume_lock_keys_by_drive_not_directory(self):
  with tempfile.TemporaryDirectory() as d:
   with guard.volume_lock("C:/one",d):
    with self.assertRaises(guard.PolicyError):
     with guard.volume_lock("C:/two",d): pass
 def test_lock_is_released_after_failure(self):
  with tempfile.TemporaryDirectory() as d:
   try:
    with guard.volume_lock("C:/",d): raise RuntimeError("simulated stage failure")
   except RuntimeError: pass
   with guard.volume_lock("C:/",d): pass
 def test_copy_verification_preserves_source(self):
  with tempfile.TemporaryDirectory() as d:
   src=Path(d)/"source"; dst=Path(d)/"copy"; src.write_bytes(b"safe")
   r=guard.copy_verify(src,dst,*self.copy_args(src,dst,Path(d))); self.assertTrue(r["copied"]); self.assertEqual(src.read_bytes(),dst.read_bytes())
 def test_copy_verification_failure_rolls_back_staged_copy(self):
  with tempfile.TemporaryDirectory() as d:
   src=Path(d)/"source"; dst=Path(d)/"copy"; src.write_bytes(b"safe")
   args=self.copy_args(src,dst,Path(d))
   with self.assertRaises(guard.PolicyError): guard.copy_verify(src,dst,*args,verifier=lambda *_:False)
   self.assertTrue(src.exists()); self.assertFalse(dst.exists())
 def test_preexisting_destination_is_never_deleted(self):
  with tempfile.TemporaryDirectory() as d:
   src=Path(d)/"source"; dst=Path(d)/"destination"; src.write_bytes(b"safe"); dst.write_bytes(b"prior")
   with self.assertRaises(guard.PolicyError): guard.copy_verify(src,dst,*self.copy_args(src,dst,Path(d)))
   self.assertEqual(dst.read_bytes(),b"prior")
 def test_tree_issues_reports_hardlink_and_protected_child(self):
  with tempfile.TemporaryDirectory() as d:
   root=Path(d)/"work"; root.mkdir(); a=root/"a.txt"; a.write_text("x"); (root/"b.txt").hardlink_to(a)
   p=policy(protected_paths=[str(a)],approved_roots=[str(root)])
   self.assertGreaterEqual(len(guard.tree_issues(root,p,{".txt"})),2)
 def test_tree_issues_rejects_directory_symlink(self):
  with tempfile.TemporaryDirectory() as d:
   root=Path(d)/"work"; outside=Path(d)/"outside"; root.mkdir(); outside.mkdir(); (root/"link").symlink_to(outside,target_is_directory=True)
   self.assertTrue(guard.tree_issues(root,policy(protected_paths=[],approved_roots=[str(root)])))
 def test_inventory_dependencies_keep_hardlink_evidence(self):
  x=guard.normalized_item({"path":"C:/work/cache"},[{"file":"C:/work/cache/a","linkedPath":"C:/other/a"}])
  self.assertEqual(x["dependencies"][0]["type"],"hardlink_evidence")
 def test_owned_delete_requires_exact_grant_and_journals(self):
  with tempfile.TemporaryDirectory() as d:
   root=Path(d); target=root/"owned.tmp"; target.write_text("dispose")
   p=policy(protected_paths=[],approved_roots=[str(root)],action_grants=[{"id":"delete","action":"delete","target":str(target),"agent_owned":True,"positively_disposable":True,"recovery_retained":True,"expires_at":(datetime.now(timezone.utc)+timedelta(hours=1)).isoformat()}])
   m=root/"policy.json"; m.write_text(json.dumps(p)); ledger=root/"ledger.jsonl"
   guard.delete_owned(m,target,"delete",0,str(root/"locks"),ledger)
   self.assertFalse(target.exists()); self.assertIn("owned-delete",ledger.read_text())
 def test_owned_delete_is_not_blocked_by_low_capacity(self):
  with tempfile.TemporaryDirectory() as d:
   root=Path(d); target=root/"owned.tmp"; target.write_text("dispose")
   p=policy(protected_paths=[],approved_roots=[str(root)],action_grants=[{"id":"delete","action":"delete","target":str(target),"agent_owned":True,"positively_disposable":True,"recovery_retained":True,"expires_at":(datetime.now(timezone.utc)+timedelta(hours=1)).isoformat()}]); m=root/"policy.json"; m.write_text(json.dumps(p))
   with mock.patch.object(guard.shutil,"disk_usage",return_value=self.disk(0)):
    guard.delete_owned(m,target,"delete",0,str(root/"locks"))
   self.assertFalse(target.exists())
 def test_reservation_checkpoint_release_and_corrupt_state_fail_closed(self):
  with tempfile.TemporaryDirectory() as d:
   root=Path(d); m=root/"policy.json"; m.write_text(json.dumps(policy(protected_paths=[],approved_roots=[str(root)])))
   state=root/"state.json"; lock=str(root/"locks"); ledger=root/"ledger.jsonl"
   guard.reserve(m,root,"r1",0,lock,state,ledger)
   self.assertTrue(guard.checkpoint(m,root,0,lock,ledger,state,"r1")["allowed"])
   guard.release_reservation(root,"r1",lock,state,ledger)
   state.write_text("not-json")
   with self.assertRaises(guard.PolicyError): guard.checkpoint(m,root,0,lock,ledger,state)
 def test_reservation_contention_fails_closed(self):
  with tempfile.TemporaryDirectory() as d:
   root=Path(d); m=root/"policy.json"; m.write_text(json.dumps(policy(protected_paths=[],approved_roots=[str(root)])))
   with guard.volume_lock(root.anchor,str(root/"locks")):
    with self.assertRaises(guard.PolicyError): guard.reserve(m,root,"r1",0,str(root/"locks"),root/"state.json")
 def test_staged_relocation_persists_state_and_retains_source(self):
  with tempfile.TemporaryDirectory() as d:
   root=Path(d); src=root/"source.tmp"; dst=root/"destination.tmp"; src.write_bytes(b"safe")
   m,g,peak,lock=self.copy_args(src,dst,root); state=root/"state.json"; ledger=root/"ledger.jsonl"; guard.reserve(m,dst.parent,"r1",max(peak,src.stat().st_size),lock,state,ledger)
   result=guard.stage_relocation(m,src,dst,g,peak,lock,state=state,reservation_id="r1",transaction_id="tx1",ledger=ledger)
   self.assertFalse(result["finalized"]); self.assertTrue(src.exists()); self.assertTrue(dst.exists()); self.assertEqual(json.loads(state.read_text())["transactions"]["tx1"]["status"],"staged")
   with self.assertRaises(guard.PolicyError): guard.finalize_relocation(m,"tx1",lock,state=state,ledger=ledger)
 def test_relocation_finalizes_only_after_separate_dispositions_and_verified_copy(self):
  with tempfile.TemporaryDirectory() as d:
   root=Path(d); src=root/"source.tmp"; dst=root/"destination.tmp"; src.write_bytes(b"safe")
   m,g,peak,lock=self.copy_args(src,dst,root); state=root/"state.json"; ledger=root/"ledger.jsonl"; guard.reserve(m,dst.parent,"r1",max(peak,src.stat().st_size),lock,state,ledger)
   guard.stage_relocation(m,src,dst,g,peak,lock,state=state,reservation_id="r1",transaction_id="tx1",ledger=ledger)
   self.assertTrue(src.exists())
   guard.record_relocation_disposition("tx1",state,"passed","passed",ledger)
   result=guard.finalize_relocation(m,"tx1",lock,state=state,ledger=ledger)
   self.assertTrue(result["finalized"]); self.assertFalse(src.exists()); self.assertEqual(dst.read_bytes(),b"safe"); self.assertIn("relocation-finalized",ledger.read_text()); self.assertFalse(guard.reservation_entries(json.loads(state.read_text()),dst.parent))
 def test_failed_relocation_disposition_releases_growth_reservation(self):
  with tempfile.TemporaryDirectory() as d:
   root=Path(d); src=root/"source.tmp"; dst=root/"destination.tmp"; src.write_bytes(b"safe")
   m,g,peak,lock=self.copy_args(src,dst,root); state=root/"state.json"; guard.reserve(m,dst.parent,"r1",src.stat().st_size,lock,state)
   guard.stage_relocation(m,src,dst,g,peak,lock,state=state,reservation_id="r1",transaction_id="tx1")
   guard.record_relocation_disposition("tx1",state,"failed","passed")
   self.assertTrue(src.exists()); self.assertTrue(dst.exists()); self.assertFalse(guard.reservation_entries(guard.load_reservations(state),dst.parent))
 def test_relocation_finalize_rejects_staged_destination_hardlink(self):
  with tempfile.TemporaryDirectory() as d:
   root=Path(d); src=root/"source.tmp"; dst=root/"destination.tmp"; src.write_bytes(b"safe")
   m,g,peak,lock=self.copy_args(src,dst,root); state=root/"state.json"; guard.reserve(m,dst.parent,"r1",src.stat().st_size,lock,state)
   guard.stage_relocation(m,src,dst,g,peak,lock,state=state,reservation_id="r1",transaction_id="tx1")
   (root/"alias.tmp").hardlink_to(dst); guard.record_relocation_disposition("tx1",state,"passed","passed")
   with self.assertRaises(guard.PolicyError): guard.finalize_relocation(m,"tx1",lock,state=state)
   self.assertTrue(src.exists())
 def test_relocation_finalize_rejects_staged_destination_symlink(self):
  with tempfile.TemporaryDirectory() as d:
   root=Path(d); src=root/"source.tmp"; dst=root/"destination.tmp"; outside=root/"outside.tmp"; src.write_bytes(b"safe"); outside.write_bytes(b"safe")
   m,g,peak,lock=self.copy_args(src,dst,root); state=root/"state.json"; guard.reserve(m,dst.parent,"r1",src.stat().st_size,lock,state)
   guard.stage_relocation(m,src,dst,g,peak,lock,state=state,reservation_id="r1",transaction_id="tx1")
   dst.unlink(); dst.symlink_to(outside); guard.record_relocation_disposition("tx1",state,"passed","passed")
   with self.assertRaises(guard.PolicyError): guard.finalize_relocation(m,"tx1",lock,state=state)
   self.assertTrue(src.exists())
 def test_global_state_lock_blocks_cross_volume_writer(self):
  with tempfile.TemporaryDirectory() as d:
   root=Path(d); state=root/"state.json"
   with guard.state_lock(state):
    with self.assertRaises(guard.PolicyError):
     with guard.state_lock(state): pass
 def test_copy_peak_is_never_below_source_size(self):
  with tempfile.TemporaryDirectory() as d:
   root=Path(d); src=root/"source.tmp"; dst=root/"destination.tmp"; src.write_bytes(b"safe" * 1024)
   m,g,_,lock=self.copy_args(src,dst,root); r=guard.copy_verify(src,dst,m,g,0,lock)
   self.assertGreaterEqual(r["capacity"]["estimated_peak_bytes"],src.stat().st_size)
 def test_model_extensions_and_huggingface_cache_are_excluded(self):
  self.assertTrue(guard.model_like("C:/cache/huggingface/tokenizers/a.json")); self.assertTrue(guard.model_like("C:/cache/lm-studio/models/x/vocab.txt")); self.assertTrue(guard.model_like("C:/work/a.onnx")); self.assertTrue(guard.model_like("C:/work/a.pth"))
 def test_lm_studio_extension_runtime_is_not_blanket_model_excluded(self):
  self.assertFalse(guard.model_like("C:/Users/example/.cache/lm-studio/extensions/backends/runtime.dll")); self.assertTrue(guard.model_like("C:/Users/example/.cache/lm-studio/extensions/models/runtime.js")); self.assertTrue(guard.model_like("C:/Users/example/.cache/lm-studio/models/vendor/weights.json"))
 def test_checkpoint_refuses_model_directory(self):
  with tempfile.TemporaryDirectory() as d:
   root=Path(d); model=root/"models"; model.mkdir(); m=root/"policy.json"; m.write_text(json.dumps(policy(protected_paths=[],approved_roots=[str(root)])))
   with self.assertRaises(guard.PolicyError): guard.checkpoint(m,model,0,str(root/"locks"),state=root/"state.json")
 def test_checkpoint_marker_directory_is_model_like(self):
  self.assertTrue(guard.model_like("C:/work/checkpoints/metadata.txt"))
 def test_runtime_content_validator_rejects_renamed_binary(self):
  with tempfile.TemporaryDirectory() as d:
   fake=Path(d)/"runtime.txt"; fake.write_bytes(b"MZ\0binary")
   self.assertIn("NUL",guard.runtime_content_issue(fake))
