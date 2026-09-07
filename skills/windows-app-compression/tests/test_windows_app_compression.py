import importlib.util, json, sys, tempfile, unittest
from datetime import datetime, timedelta, timezone
from pathlib import Path
from unittest import mock
ROOT=Path(__file__).parents[2]; SPEC=importlib.util.spec_from_file_location("app",ROOT/"windows-app-compression/scripts/windows_app_compression.py"); app=importlib.util.module_from_spec(SPEC); SPEC.loader.exec_module(app)
class AppCompressionTests(unittest.TestCase):
 def test_model_file_excluded(self):
  with tempfile.TemporaryDirectory() as d:
   Path(d,"model.gguf").write_bytes(b"x"); result=app.summary(d,app.load_guard(ROOT/"storage-awareness")); self.assertFalse(result["eligible_for_execution"])
 def test_hardlink_excluded(self):
  with tempfile.TemporaryDirectory() as d:
   Path(d,"a.txt").write_text("x"); Path(d,"b.txt").hardlink_to(Path(d,"a.txt")); result=app.summary(d,app.load_guard(ROOT/"storage-awareness")); self.assertFalse(result["eligible_for_execution"])
 def test_nonexistent_target_rejected(self):
  with self.assertRaises(RuntimeError): app.summary("Z:/does-not-exist",app.load_guard(ROOT/"storage-awareness"))
 def test_execution_gate_rejects_renamed_binary_txt(self):
  with tempfile.TemporaryDirectory() as d:
   Path(d,"runtime.txt").write_bytes(b"MZ\0binary"); guard=app.load_guard(ROOT/"storage-awareness")
   self.assertTrue(app.execution_issues(d,guard,{".txt"}))
 def test_execution_gate_rejects_model_metadata_txt(self):
  with tempfile.TemporaryDirectory() as d:
   model=Path(d,"models","checkpoint"); model.mkdir(parents=True); Path(model,"metadata.txt").write_text("model metadata"); guard=app.load_guard(ROOT/"storage-awareness")
   self.assertTrue(app.execution_issues(d,guard,{".txt"}))
 def test_main_checks_every_descendant_before_compact(self):
  with tempfile.TemporaryDirectory() as d:
   root=Path(d); target=root/"target"; target.mkdir(); safe=target/"safe.txt"; late=target/"z-late.txt"; safe.write_text("safe runtime text"); late.write_bytes(b"MZ\0renamed binary")
   policy={"schema_version":1,"generated_at":datetime.now(timezone.utc).isoformat(),"protected_paths":[],"approved_roots":[str(target)],"action_grants":[{"id":"compress","action":"compress","target":str(target),"agent_owned":True,"positively_disposable":True,"recovery_retained":True,"expires_at":(datetime.now(timezone.utc)+timedelta(hours=1)).isoformat(),"allowed_extensions":[".txt"]}],"reservations":{"default_min_bytes":0,"default_percent":0}}
   mapping=root/"policy.json"; state=root/"state.json"; mapping.write_text(json.dumps(policy)); guard=app.load_guard(ROOT/"storage-awareness"); checked=[]; validate=guard.runtime_content_issue
   def observe(path): checked.append(Path(path).name); return validate(path)
   argv=["compression","execute","--target",str(target),"--storage-awareness-path",str(ROOT/"storage-awareness"),"--map",str(mapping),"--algorithm","XPRESS8K","--approval-id","compress","--reservation-id","test-reservation","--estimated-peak-bytes","0","--allow-execute","--lock-directory",str(root/"locks"),"--state",str(state)]
   with mock.patch.object(app,"load_guard",return_value=guard), mock.patch.object(guard,"journal"), mock.patch.object(guard,"runtime_content_issue",side_effect=observe), mock.patch.object(app.subprocess,"run") as compact, mock.patch.object(sys,"argv",argv):
    with self.assertRaises(RuntimeError): app.main()
   self.assertEqual(set(checked),{safe.name,late.name})
   compact.assert_not_called()
