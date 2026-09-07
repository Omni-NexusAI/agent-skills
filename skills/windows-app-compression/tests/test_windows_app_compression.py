import importlib.util, tempfile, unittest
from pathlib import Path
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
