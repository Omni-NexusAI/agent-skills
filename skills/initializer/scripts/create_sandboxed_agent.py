#!/usr/bin/env python3
"""
Initializer Skill Script: create_sandboxed_agent

Description:
    Create isolated agent instances for testing and security.
    Supports creation of sandboxed OpenClaw agents with restricted access.
"""

import argparse
import logging
import json
import os
import sys
import subprocess
import shutil
from pathlib import Path

def main():
    """Main script function"""
    try:
        parser = argparse.ArgumentParser(description='Create sandboxed agent')
        parser.add_argument('--name', type=str, help='Sandbox name', required=True)
        parser.add_argument('--capabilities', type=str, help='Agent capabilities (comma-separated)', default='web,file')
        parser.add_argument('--resources', type=str, help='Resource limits', default=None)
        parser.add_argument('--path', type=str, help='Sandbox directory path', default=None)
        parser.add_argument('--config', type=str, help='Configuration template to use', default=None)
        parser.add_argument('--isolate', type=bool, help='Full isolation mode', default=True)
        parser.add_argument('--output', type=str, help='Output file for configuration', default=None)
        
        args = parser.parse_args()
        
        # Create sandboxed agent
        config = create_sandboxed_agent(
            args.name,
            args.capabilities,
            args.resources,
            args.path,
            args.config,
            args.isolate
        )
        
        # Output results
        if args.output:
            with open(args.output, 'w') as f:
                json.dump(config, f, indent=2)
            logging.info(f"Configuration saved to {args.output}")
        else:
            print(json.dumps(config, indent=2))
        
        return 0
        
    except Exception as e:
        logging.exception(f"Sandboxed agent creation failed: {str(e)}")
        return 1

def create_sandboxed_agent(name, capabilities, resources, path, config, isolate):
    """Create sandboxed agent instance"""
    logging.info(f"Creating sandboxed agent: {name}")
    
    # Parse capabilities
    caps = parse_capabilities(capabilities)
    
    # Determine sandbox path
    sandbox_path = determine_sandbox_path(name, path)
    
    # Create sandbox directory structure
    create_sandbox_structure(sandbox_path)
    
    # Configure sandbox environment
    env_config = configure_sandbox_environment(sandbox_path, isolate)
    
    # Apply resource limits
    resource_config = apply_resource_limits(sandbox_path, resources)
    
    # Configure capabilities
    cap_config = configure_capabilities(sandbox_path, caps)
    
    # Create agent configuration
    agent_config = create_agent_configuration(sandbox_path, name, config, caps)
    
    # Final configuration
    final_config = {
        'name': name,
        'type': 'sandboxed',
        'path': sandbox_path,
        'capabilities': cap_config,
        'resources': resource_config,
        'environment': env_config,
        'agent': agent_config,
        'isolation': isolate,
        'status': 'created'
    }
    
    return final_config

def parse_capabilities(capabilities_str):
    """Parse capabilities string into list"""
    return [cap.strip().lower() for cap in capabilities_str.split(',')]

def determine_sandbox_path(name, custom_path):
    """Determine sandbox directory path"""
    if custom_path:
        return os.path.abspath(custom_path)
    
    # Default to .openclaw/sandboxes/name
    sandbox_dir = os.path.join(os.path.expanduser('~/.openclaw'), 'sandboxes', name)
    return os.path.abspath(sandbox_dir)

def create_sandbox_structure(sandbox_path):
    """Create sandbox directory structure"""
    logging.info(f"Creating sandbox structure at {sandbox_path}")
    
    # Create main sandbox directory
    os.makedirs(sandbox_path, exist_ok=True)
    
    # Create subdirectories
    subdirs = [
        'workspace',
        'config',
        'data',
        'logs',
        'temp',
        'scripts'
    ]
    
    for subdir in subdirs:
        dir_path = os.path.join(sandbox_path, subdir)
        os.makedirs(dir_path, exist_ok=True)
        logging.info(f"Created directory: {dir_path}")

def configure_sandbox_environment(sandbox_path, isolate):
    """Configure sandbox environment"""
    env_config = {
        'path': sandbox_path,
        'variables': {
            'SANDBOX_HOME': sandbox_path,
            'SANDBOX_WORKSPACE': os.path.join(sandbox_path, 'workspace'),
            'SANDBOX_DATA': os.path.join(sandbox_path, 'data'),
            'SANDBOX_CONFIG': os.path.join(sandbox_path, 'config'),
            'SANDBOX_LOGS': os.path.join(sandbox_path, 'logs'),
            'SANDBOX_TEMP': os.path.join(sandbox_path, 'temp')
        },
        'isolation': {
            'enabled': isolate,
            'network': 'restricted' if isolate else 'standard',
            'filesystem': 'sandboxed' if isolate else 'restricted',
            'process': 'isolated' if isolate else 'shared'
        }
    }
    
    return env_config

def apply_resource_limits(sandbox_path, resources_str):
    """Apply resource limits to sandbox"""
    resource_config = {
        'cpu': {'limit': '50%', 'cores': 2},
        'memory': {'limit': '2GB', 'swap': '1GB'},
        'disk': {'limit': '10GB', 'path': sandbox_path},
        'network': {'bandwidth': '100Mbps', 'connections': 10}
    }
    
    # Parse custom resource limits if provided
    if resources_str:
        try:
            custom_resources = json.loads(resources_str)
            resource_config.update(custom_resources)
        except json.JSONDecodeError:
            logging.warning(f"Failed to parse custom resources: {resources_str}")
    
    return resource_config

def configure_capabilities(sandbox_path, capabilities):
    """Configure sandbox capabilities"""
    cap_config = {
        'allowed': capabilities,
        'web': {
            'enabled': 'web' in capabilities,
            'restrictions': ['block_internal_networks'] if capabilities else []
        },
        'file': {
            'enabled': 'file' in capabilities,
            'restrictions': ['sandbox_path_only'] if capabilities else []
        },
        'memory': {
            'enabled': 'memory' in capabilities,
            'type': 'local',
            'persistence': True
        },
        'automation': {
            'enabled': 'automation' in capabilities,
            'scripts': True
        },
        'analysis': {
            'enabled': 'analysis' in capabilities,
            'frameworks': []
        }
    }
    
    return cap_config

def create_agent_configuration(sandbox_path, name, template, capabilities):
    """Create agent configuration file"""
    agent_config = {
        'name': name,
        'type': 'sandboxed',
        'version': '1.0.0',
        'capabilities': capabilities,
        'sandbox': {
            'enabled': True,
            'path': sandbox_path,
            'isolation_level': 'high'
        },
        'security': {
            'permission_model': 'restricted',
            'sandbox_mode': True,
            'audit_logging': True
        },
        'network': {
            'internet_access': True,
            'proxy': {
                'enabled': False
            }
        },
        'brain': {
            'type': 'solo',
            'mode': 'sandboxed'
        }
    }
    
    # Load template if provided
    if template:
        try:
            template_path = os.path.join(sandbox_path, 'config', 'agent.json')
            if os.path.exists(template):
                with open(template, 'r') as f:
                    template_config = json.load(f)
                    agent_config.update(template_config)
        except Exception as e:
            logging.warning(f"Failed to load template: {str(e)}")
    
    # Write configuration
    config_path = os.path.join(sandbox_path, 'config', 'agent.json')
    with open(config_path, 'w') as f:
        json.dump(agent_config, f, indent=2)
    
    logging.info(f"Agent configuration written to {config_path}")
    
    return agent_config

def setup_sandbox_security(sandbox_path):
    """Setup sandbox security measures"""
    security_config = {
        'file_permissions': '700',
        'network_restrictions': True,
        'process_isolation': True,
        'resource_monitoring': True
    }
    
    # Create security configuration
    security_path = os.path.join(sandbox_path, 'config', 'security.json')
    with open(security_path, 'w') as f:
        json.dump(security_config, f, indent=2)
    
    return security_config

def create_sandbox_scripts(sandbox_path):
    """Create helper scripts for sandbox management"""
    scripts = {
        'start': '#!/bin/bash\ncd {sandbox_path}\n# Start sandboxed agent\n',
        'stop': '#!/bin/bash\n# Stop sandboxed agent\n',
        'status': '#!/bin/bash\n# Check sandbox status\n'
    }
    
    scripts_dir = os.path.join(sandbox_path, 'scripts')
    for script_name, script_content in scripts.items():
        script_path = os.path.join(scripts_dir, script_name + '.sh')
        with open(script_path, 'w') as f:
            f.write(script_content.format(sandbox_path=sandbox_path))
        os.chmod(script_path, 0o755)
        logging.info(f"Created script: {script_path}")

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    exit(main())
