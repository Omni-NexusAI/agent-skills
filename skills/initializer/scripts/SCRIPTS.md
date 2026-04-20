# Initializer Skill Scripts

This directory contains all the scripts used by the Initializer skill for agent setup, configuration, and management.

## Available Scripts

### Browser Access Scripts

#### `browser_bootstrap.py`
Bootstrap browser capabilities for web interaction.

**Usage:**
```bash
python browser_bootstrap.py --type chrome --headless true
```

**Options:**
- `--type`: Browser type (chrome, firefox, edge)
- `--headless`: Run in headless mode (true/false)
- `--timeout`: Timeout in seconds

#### `browser_permissions.py`
Configure browser permissions and access rights.

**Usage:**
```bash
python browser_permissions.py --level user --rights read,write
```

**Options:**
- `--level`: Permission level (user, admin, system)
- `--rights`: Access rights (comma-separated)
- `--context`: Security context

### Permission Scripts

#### `permission_setup.py`
Configure system permissions and access rights.

**Usage:**
```bash
python permission_setup.py --level admin --rights read,write,execute
```

**Options:**
- `--level`: Permission level (user, admin, system)
- `--rights`: Access rights (comma-separated)
- `--context`: Security context

#### `security_context.py`
Set up security context for agent operations.

**Usage:**
```bash
python security_context.py --type standard --audit enabled
```

**Options:**
- `--type`: Security type (standard, enhanced, custom)
- `--audit`: Audit logging (enabled/disabled)
- `--encryption`: Encryption (enabled/disabled)

### Framework Analysis Scripts

#### `framework_analyze.py`
Analyze and understand different agent frameworks.

**Usage:**
```bash
python framework_analyze.py --target openclaw --depth full
```

**Options:**
- `--target`: Target framework (openclaw, langchain, crewai)
- `--depth`: Analysis depth (basic, full, comprehensive)
- `--compatibility`: Compatibility mode (auto, strict, relaxed)

#### `compatibility_check.py`
Check compatibility between different agent frameworks.

**Usage:**
```bash
python compatibility_check.py --target langchain
```

**Options:**
- `--target`: Target framework
- `--mode`: Compatibility mode (auto, strict, relaxed)
- `--report`: Generate compatibility report

### External Agent Scripts

#### `external_agent_setup.py`
Configure communication with external agents.

**Usage:**
```bash
python external_agent_setup.py --agent external --protocol http
```

**Options:**
- `--agent`: Agent type (internal, external, hybrid)
- `--protocol`: Communication protocol (http, websocket, grpc)
- `--timeout`: Connection timeout

#### `agent_discovery.py`
Discover and configure external agent instances.

**Usage:**
```bash
python agent_discovery.py --method broadcast --range 192.168.1.0/24
```

**Options:**
- `--method`: Discovery method (broadcast, registry, manual)
- `--range`: Network range
- `--timeout`: Discovery timeout

### Sandboxed Agent Scripts

#### `sandbox_create.py`
Create isolated agent instances for testing.

**Usage:**
```bash
python sandbox_create.py --name test_agent --capabilities web,file
```

**Options:**
- `--name`: Sandbox name
- `--capabilities`: Agent capabilities
- `--resources`: Resource limits

#### `sandbox_manage.py`
Manage sandboxed agent instances.

**Usage:**
```bash
python sandbox_manage.py --action start --name test_agent
```

**Options:**
- `--action`: Action (start, stop, restart, delete)
- `--name`: Sandbox name
- `--resources`: Resource limits

## Internet Bootstrap Scripts

### `internet_bootstrap.py`
Help agents get internet access with minimal setup.

**Usage:**
```bash
python internet_bootstrap.py --access enabled --proxy false
```

**Options:**
- `--access`: Internet access (enabled/disabled)
- `--proxy`: Use proxy (true/false)
- `--host`: Proxy host
- `--port`: Proxy port

### `network_config.py`
Configure network settings and connectivity.

**Usage:**
```bash
python network_config.py --type standard --firewall allow_all
```

**Options:**
- `--type`: Network type (standard, advanced, custom)
- `--firewall`: Firewall rules
- `--dns`: DNS settings

## Permission Configuration Scripts

### `permission_configure.py`
Configure system permissions and access rights.

**Usage:**
```bash
python permission_configure.py --level user --rights read,write
```

**Options:**
- `--level`: Permission level (user, admin, system)
- `--rights`: Access rights (comma-separated)
- `--context`: Security context

### `access_control.py`
Set up access control and security policies.

**Usage:**
```bash
python access_control.py --type role_based --rules custom
```

**Options:**
- `--type`: Access control type (role_based, attribute_based, rule_based)
- `--rules`: Security rules
- `--policy`: Policy enforcement

## External Agent Setup Scripts

### `external_agent_bootstrap.py`
Allow single agent to bootstrap entire system with minimal user input.

**Usage:**
```bash
python external_agent_bootstrap.py --agent external --config auto
```

**Options:**
- `--agent`: Agent type (internal, external, hybrid)
- `--config`: Configuration mode (auto, manual, custom)
- `--resources`: Resource requirements

### `resource_collection.py`
Gather resources from internet or system for agent initialization.

**Usage:**
```bash
python resource_collection.py --source internet --type config
```

**Options:**
- `--source`: Resource source (internet, system, local)
- `--type`: Resource type (config, script, template)
- `--destination`: Destination directory

## Script Development

### Creating New Scripts

1. **Create script file:**
```bash
touch scripts/new_script.py
```

2. **Add script template:**
```python
#!/usr/bin/env python3
"""
Initializer Skill Script: New Script

Description: Brief description of what this script does
"""

import argparse
import logging

def main():
    """Main script function"""
    parser = argparse.ArgumentParser(description='Initializer Skill Script')
    parser.add_argument('--option', type=str, help='Script option')
    
    args = parser.parse_args()
    
    # Script logic here
    logging.info(f"Running script with option: {args.option}")
    
    # Return success
    return 0

if __name__ == "__main__":
    exit(main())
```

3. **Make executable:**
```bash
chmod +x scripts/new_script.py
```

### Script Structure

Each script should follow this structure:

```python
#!/usr/bin/env python3
"""
Initializer Skill Script: Script Name

Description: Brief description of what this script does
"""

import argparse
import logging
from initializer import config

# Global configuration
CONFIG = config.get_config()

# Logger
logger = logging.getLogger(__name__)

def main():
    """Main script function"""
    try:
        # Parse arguments
        parser = argparse.ArgumentParser(description='Script description')
        parser.add_argument('--option', type=str, help='Script option', required=True)
        
        args = parser.parse_args()
        
        # Validate arguments
        if not validate_args(args):
            logger.error("Invalid arguments")
            return 1
        
        # Execute script logic
        result = execute_script(args)
        
        if result:
            logger.info("Script completed successfully")
            return 0
        else:
            logger.error("Script failed")
            return 1
            
    except Exception as e:
        logger.exception(f"Script failed with error: {str(e)}")
        return 1

def validate_args(args):
    """Validate script arguments"""
    # Add validation logic here
    return True

def execute_script(args):
    """Execute main script logic"""
    # Add script logic here
    logger.info(f"Executing script with option: {args.option}")
    
    # Example: Perform some operation
    try:
        # Script operations
        result = True
        return result
    except Exception as e:
        logger.exception(f"Operation failed: {str(e)}")
        return False

if __name__ == "__main__":
    exit(main())
```

### Script Configuration

Each script should support configuration through the main skill configuration:

```python
from initializer import config

# Get script-specific configuration
script_config = config.get_script_config("script_name")

# Access configuration values
script_type = script_config.get("type", "default")
script_timeout = script_config.get("timeout", 30)
```

### Error Handling

Scripts should implement proper error handling:

```python
try:
    # Script operations
    result = perform_operation()
    
    if not result:
        raise ScriptError("Operation failed")
        
except ScriptError as e:
    logger.error(f"Script error: {str(e)}")
    return 1
except Exception as e:
    logger.exception(f"Unexpected error: {str(e)}")
    return 1
```

### Logging

Scripts should use the standard logging configuration:

```python
import logging

logger = logging.getLogger(__name__)

# Log messages
logger.info("Starting script operation")
logger.debug(f"Detailed operation data: {data}")
logger.warning("Potential issue detected")
logger.error("Operation failed")
```

## Testing Scripts

### Unit Testing

Create test files for each script:

```bash
touch tests/test_browser_bootstrap.py
```

Example test structure:

```python
import unittest
from unittest.mock import patch, MagicMock
from scripts.browser_bootstrap import main

class TestBrowserBootstrap(unittest.TestCase):
    
    @patch('scripts.browser_bootstrap.logging')
    def test_browser_bootstrap_success(self, mock_logging):
        """Test browser bootstrap success"""
        # Mock arguments
        args = ['--type', 'chrome', '--headless', 'true']
        
        # Mock subprocess
        with patch('subprocess.run') as mock_run:
            mock_run.return_value = MagicMock(returncode=0)
            
            # Run script
            result = main()
            
            # Assert success
            self.assertEqual(result, 0)
            mock_logging.info.assert_called_with("Browser bootstrap completed successfully")
    
    @patch('scripts.browser_bootstrap.logging')
    def test_browser_bootstrap_failure(self, mock_logging):
        """Test browser bootstrap failure"""
        # Mock arguments
        args = ['--type', 'chrome', '--headless', 'true']
        
        # Mock subprocess failure
        with patch('subprocess.run') as mock_run:
            mock_run.return_value = MagicMock(returncode=1)
            
            # Run script
            result = main()
            
            # Assert failure
            self.assertEqual(result, 1)
            mock_logging.error.assert_called_with("Browser bootstrap failed")

if __name__ == '__main__':
    unittest.main()
```

### Integration Testing

Test scripts in the context of the complete skill:

```python
import unittest
from initializer import skill
from scripts.browser_bootstrap import main

class TestScriptIntegration(unittest.TestCase):
    
    def setUp(self):
        """Set up test environment"""
        self.skill = skill.InitializerSkill()
        
    def test_browser_bootstrap_integration(self):
        """Test browser bootstrap integration with skill"""
        # Initialize skill
        self.skill.initialize()
        
        # Test browser bootstrap
        result = main(['--type', 'chrome', '--headless', 'true'])
        
        # Verify result
        self.assertEqual(result, 0)
        self.assertTrue(self.skill.has_browser_capability())

if __name__ == '__main__':
    unittest.main()
```

## Documentation

### Script Documentation

Each script should include comprehensive documentation:

```python
"""
Initializer Skill Script: browser_bootstrap.py

Description:
    Bootstrap browser capabilities for web interaction.
    Supports Chrome, Firefox, and Edge browsers.
    Can run in headless mode for server environments.

Usage:
    python browser_bootstrap.py --type chrome --headless true

Options:
    --type: Browser type (chrome, firefox, edge)
    --headless: Run in headless mode (true/false)
    --timeout: Timeout in seconds

Examples:
    # Bootstrap Chrome in headless mode
    python browser_bootstrap.py --type chrome --headless true
    
    # Bootstrap Firefox with GUI
    python browser_bootstrap.py --type firefox --headless false

Dependencies:
    - selenium
    - webdriver_manager
    - browser-specific drivers

Configuration:
    - browser_type: chrome
    - headless_mode: true
    - timeout: 30

Error Handling:
    - Connection errors
    - Driver not found errors
    - Timeout errors

Returns:
    0 on success
    1 on failure
"""
```

### API Documentation

Document script APIs for external integration:

```python
class BrowserBootstrap:
    """
    Browser Bootstrap API
    
    Provides programmatic access to browser bootstrapping functionality.
    
    Methods:
        - bootstrap(browser_type, headless, timeout)
        - configure_permissions(level, rights)
        - check_capabilities()
    """
    
    def __init__(self, config=None):
        """Initialize browser bootstrap"""
        self.config = config or get_default_config()
        self.logger = logging.getLogger(__name__)
    
    def bootstrap(self, browser_type, headless=True, timeout=30):
        """
        Bootstrap browser capabilities
        
        Args:
            browser_type (str): Browser type (chrome, firefox, edge)
            headless (bool): Run in headless mode
            timeout (int): Timeout in seconds
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            # Bootstrap logic
            self.logger.info(f"Bootstrapping {browser_type} browser")
            # ... implementation ...
            return True
        except Exception as e:
            self.logger.error(f"Browser bootstrap failed: {str(e)}")
            return False
    
    def configure_permissions(self, level, rights):
        """
        Configure browser permissions
        
        Args:
            level (str): Permission level (user, admin, system)
            rights (list): Access rights
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            # Permission configuration
            self.logger.info(f"Configuring {level} permissions")
            # ... implementation ...
            return True
        except Exception as e:
            self.logger.error(f"Permission configuration failed: {str(e)}")
            return False
```

## Version Control

### Script Versioning

Scripts should include version information:

```python
"""
Initializer Skill Script: browser_bootstrap.py
Version: 1.0.0
Last Updated: 2026-02-11
Author: OpenClaw Team
"""
```

### Change Log

Maintain change logs for script updates:

```markdown
# Change Log

## 1.0.0 (2026-02-11)
- Initial release
- Added Chrome, Firefox, and Edge support
- Implemented headless mode
- Added permission configuration

## 1.0.1 (2026-02-12)
- Fixed browser driver compatibility issues
- Added timeout configuration
- Improved error handling
- Added logging enhancements

## 1.1.0 (2026-02-15)
- Added support for additional browsers
- Implemented parallel processing
- Added configuration file support
- Improved performance
```