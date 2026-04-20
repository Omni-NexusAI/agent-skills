# Unicode Encoding Fixes for Windows

**Date**: 2026-02-16 00:10 EST
**Issue**: UnicodeEncodeError when processing voice messages on Windows

## Problem

When running Python scripts on Windows with console output, Unicode characters like:
- → (U+2192)
- ✓ (U+2713)
- ± (U+00B1)
cause encoding errors because Windows console uses cp1252 encoding by default.

## Solutions

### 1. Set Environment Variable (Best Solution)
```bash
# PowerShell
$env:PYTHONIOENCODING="utf-8"

# Command Prompt
set PYTHONIOENCODING=utf-8
```

### 2. Use UTF-8 Encoding Explicitly
```python
# When writing to console
import sys
sys.stdout.reconfigure(encoding='utf-8')

# When writing to files
with open(file, 'w', encoding='utf-8') as f:
    f.write(content)
```

### 3. Use ASCII-Safe Characters
```python
# Instead of Unicode symbols
print("[OK]")      # Instead of ✓
print("[PASS]")    # Instead of ✓
print("[ERROR]")   # Instead of ✗
print("[ARROW]")    # Instead of →
print("[DOT]")      # Instead of ⚫
```

### 4. Avoid Console Output for Unicode
```python
# Log to file instead of console
import logging
logging.basicConfig(filename='output.log', encoding='utf-8')

# Use ASCII status codes
import sys
print("SUCCESS", file=sys.stderr)  # Safe
```

## Voice Messaging Skill Updates

### Update voice_handler.py
```python
# Add at top of file
import sys
import os

# Set UTF-8 encoding for all output
os.environ['PYTHONIOENCODING'] = 'utf-8'

# Reconfigure stdout/stderr
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')
if hasattr(sys.stderr, 'reconfigure'):
    sys.stderr.reconfigure(encoding='utf-8')
```

### Update Test Scripts
```python
# Replace Unicode symbols with ASCII
✓  → "[OK]"
✗  → "[ERROR]"
→  → "->"

# Or remove entirely for cleaner output
```

## Recommendation

**Set PYTHONIOENCODING=utf-8 globally in the environment where the skill will be used.** This is the most reliable solution for Windows.

## Files to Update

1. `C:\Users\yepyy\.openclaw\workspace\voice-messaging-skill\src\voice_handler.py`
2. `C:\Users\yepyy\.openclaw\workspace\voice-messaging-skill\test.py`
3. Any test scripts that print Unicode characters

## Testing

After fixes, test with:
```bash
set PYTHONIOENCODING=utf-8
python test_script.py
```
