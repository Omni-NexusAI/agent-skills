#!/usr/bin/env python3
"""
Manual test script for Openclaw MCP Bridge.

This script tests basic connectivity to configured agents.
Run this after setting up environment variables.
"""

import asyncio
import os
import sys

# Add src to path for standalone testing
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from server import agent_manager, call_openclaw, list_openclaw_agents


async def test_list_agents():
    """Test listing agents."""
    print("\n" + "="*60)
    print("TEST 1: List Agents")
    print("="*60)
    
    result = await list_openclaw_agents()
    print(result)
    
    if "No agents configured" in result:
        print("\n❌ FAIL: No agents found")
        return False
    
    print("\n✅ PASS: Agents listed successfully")
    return True


async def test_agent_call(agent_name: str, message: str = "Hello, this is a test message"):
    """Test calling a specific agent."""
    print(f"\n" + "="*60)
    print(f"TEST: Call Agent '{agent_name}'")
    print("="*60)
    
    result = await call_openclaw(
        instruction=message,
        agent=agent_name
    )
    
    print(f"Response:\n{result}")
    
    if result.startswith("Error:"):
        print(f"\n❌ FAIL: {result}")
        return False
    
    print(f"\n✅ PASS: Agent responded successfully")
    return True


async def main():
    """Run all tests."""
    print("\n" + "="*60)
    print("Openclaw MCP Bridge - Manual Test Suite")
    print("="*60)
    
    # Test 1: List agents
    has_agents = await test_list_agents()
    
    if not has_agents:
        print("\n⚠️  No agents configured. Set OPENCLAW_AGENT_* environment variables.")
        return
    
    # Test 2: Try calling each enabled agent
    results = []
    for name, config in agent_manager.agents.items():
        if config.enabled:
            success = await test_agent_call(name)
            results.append((name, success))
        else:
            print(f"\n⏭️  Skipping disabled agent: {name}")
    
    # Summary
    print("\n" + "="*60)
    print("TEST SUMMARY")
    print("="*60)
    
    for name, success in results:
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status}: {name}")
    
    total = len(results)
    passed = sum(1 for _, success in results if success)
    
    print(f"\nTotal: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 All tests passed!")
    else:
        print("\n⚠️  Some tests failed. Check configuration and agent status.")


if __name__ == "__main__":
    asyncio.run(main())
