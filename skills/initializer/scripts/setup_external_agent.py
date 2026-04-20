#!/usr/bin/env python3
"""
Initializer Skill Script: setup_external_agent

Description:
    Configure communication with external agents.
    Allows single agent to bootstrap entire system with minimal user input.
"""

import argparse
import logging
import json
import os
import sys
import subprocess
import requests
from pathlib import Path

def main():
    """Main script function"""
    try:
        parser = argparse.ArgumentParser(description='Setup external agent communication')
        parser.add_argument('--agent', type=str, help='Agent type (internal, external, hybrid)', required=True)
        parser.add_argument('--protocol', type=str, help='Communication protocol (http, websocket, grpc)', default='http')
        parser.add_argument('--timeout', type=int, help='Connection timeout in seconds', default=30)
        parser.add_argument('--config', type=str, help='Configuration mode (auto, manual, custom)', default='auto')
        parser.add_argument('--url', type=str, help='External agent URL', default=None)
        parser.add_argument('--output', type=str, help='Output file for configuration', default=None)
        
        args = parser.parse_args()
        
        # Setup external agent
        config = setup_external_agent(args.agent, args.protocol, args.timeout, args.config, args.url)
        
        # Output results
        if args.output:
            with open(args.output, 'w') as f:
                json.dump(config, f, indent=2)
            logging.info(f"Configuration saved to {args.output}")
        else:
            print(json.dumps(config, indent=2))
        
        return 0
        
    except Exception as e:
        logging.exception(f"External agent setup failed: {str(e)}")
        return 1

def setup_external_agent(agent_type, protocol, timeout, config_mode, url):
    """Setup external agent communication"""
    logging.info(f"Setting up external agent: type={agent_type}, protocol={protocol}, config={config_mode}")
    
    config = {
        'agent_type': agent_type,
        'protocol': protocol,
        'timeout': timeout,
        'config_mode': config_mode,
        'connection': {},
        'authentication': {},
        'capabilities': {},
        'synchronization': {}
    }
    
    # Discover or configure external agent
    if config_mode == 'auto':
        config = auto_discover_agent(config, url)
    elif config_mode == 'manual':
        config = manual_configure_agent(config, url)
    elif config_mode == 'custom':
        config = custom_configure_agent(config, url)
    
    # Test connection
    if test_connection(config):
        logging.info("External agent connection successful")
    else:
        logging.warning("External agent connection test failed")
    
    # Configure synchronization
    config['synchronization'] = configure_synchronization(agent_type, protocol)
    
    return config

def auto_discover_agent(config, url):
    """Auto-discover external agent"""
    logging.info("Auto-discovering external agent")
    
    # Try common discovery methods
    discovery_methods = [
        discover_via_registry,
        discover_via_broadcast,
        discover_via_environment
    ]
    
    for method in discovery_methods:
        try:
            result = method(config)
            if result and result.get('found'):
                config['connection'].update(result.get('connection', {}))
                config['authentication'].update(result.get('authentication', {}))
                config['capabilities'].update(result.get('capabilities', {}))
                logging.info(f"Agent discovered via {method.__name__}")
                return config
        except Exception as e:
            logging.warning(f"Discovery method {method.__name__} failed: {str(e)}")
    
    # Fallback to URL if provided
    if url:
        config['connection']['url'] = url
        config = probe_agent(config)
    
    return config

def discover_via_registry(config):
    """Discover agent via service registry"""
    try:
        # Check for common service registries
        registries = [
            'http://localhost:8080/registry',
            'http://localhost:8500/v1/agent',
            'http://localhost:2379/v2/keys/agent'
        ]
        
        for registry in registries:
            try:
                response = requests.get(registry, timeout=config['timeout'])
                if response.status_code == 200:
                    data = response.json()
                    if 'agent' in data:
                        return {
                            'found': True,
                            'connection': {'url': data['agent'].get('url')},
                            'authentication': {'token': data['agent'].get('token')},
                            'capabilities': data['agent'].get('capabilities', {})
                        }
            except Exception:
                continue
    except Exception as e:
        logging.warning(f"Registry discovery failed: {str(e)}")
    
    return {'found': False}

def discover_via_broadcast(config):
    """Discover agent via network broadcast"""
    try:
        # Simulate broadcast discovery
        # In real implementation, would send UDP broadcasts to local network
        return {'found': False}
    except Exception as e:
        logging.warning(f"Broadcast discovery failed: {str(e)}")
        return {'found': False}

def discover_via_environment(config):
    """Discover agent via environment variables"""
    try:
        # Check environment variables for agent configuration
        env_vars = [
            'EXTERNAL_AGENT_URL',
            'AGENT_GATEWAY_URL',
            'OPENCLAW_GATEWAY_URL',
            'AGENT_HOST',
            'AGENT_PORT'
        ]
        
        for var in env_vars:
            value = os.getenv(var)
            if value:
                return {
                    'found': True,
                    'connection': {'url': value},
                    'authentication': {},
                    'capabilities': {}
                }
    except Exception as e:
        logging.warning(f"Environment discovery failed: {str(e)}")
    
    return {'found': False}

def manual_configure_agent(config, url):
    """Manually configure external agent"""
    logging.info("Manually configuring external agent")
    
    if not url:
        logging.error("URL required for manual configuration")
        return config
    
    config['connection']['url'] = url
    config = probe_agent(config)
    
    return config

def custom_configure_agent(config, url):
    """Custom configure external agent"""
    logging.info("Custom configuring external agent")
    
    # Custom configuration would involve user input or config file
    # For now, use manual configuration
    return manual_configure_agent(config, url)

def probe_agent(config):
    """Probe agent for capabilities"""
    url = config['connection'].get('url')
    if not url:
        return config
    
    try:
        logging.info(f"Probing agent at {url}")
        
        # Try to connect and get capabilities
        if config['protocol'] == 'http':
            response = requests.get(f"{url}/api/v1/capabilities", timeout=config['timeout'])
            if response.status_code == 200:
                data = response.json()
                config['capabilities'] = data.get('capabilities', {})
                config['authentication'] = data.get('authentication', {})
        
        return config
        
    except Exception as e:
        logging.warning(f"Agent probe failed: {str(e)}")
        return config

def test_connection(config):
    """Test connection to external agent"""
    url = config['connection'].get('url')
    if not url:
        return False
    
    try:
        logging.info(f"Testing connection to {url}")
        
        if config['protocol'] == 'http':
            response = requests.get(f"{url}/health", timeout=config['timeout'])
            return response.status_code == 200
        
        return False
        
    except Exception as e:
        logging.warning(f"Connection test failed: {str(e)}")
        return False

def configure_synchronization(agent_type, protocol):
    """Configure synchronization settings"""
    return {
        'method': 'real_time',
        'frequency': 'continuous',
        'consistency': 'strong',
        'mode': agent_type,
        'protocol': protocol,
        'message_format': 'json',
        'retry_policy': {
            'max_retries': 3,
            'backoff': 'exponential',
            'initial_delay': 1
        }
    }

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    exit(main())
