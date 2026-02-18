#!/usr/bin/env python3

from live_engine_integration import create_default_integrator

print("Testing live engine integration with persistence backed out...")

# Create integrator
integrator = create_default_integrator()

# Test validation
validation = integrator.validate_integration()
print(f"Overall validation: {validation['overall_integration']}")

# Test scenario generation (should now wire to ScenarioGenerator)
try:
    scenario_result = integrator.generate_scenario('test_scenario')
    print(f"Scenario generation: {'✅ SUCCESS' if scenario_result else '❌ FAILED'}")
    if 'fallback_reason' in scenario_result.get('generated_scenario', {}):
        print(f"  Note: Used fallback due to: {scenario_result['generated_scenario']['fallback_reason']}")
except Exception as e:
    print(f"Scenario generation: ❌ FAILED - {e}")

# Test state update
try:
    new_state = integrator.update_system_state()
    print(f"State update: {'✅ SUCCESS' if new_state is not None else '❌ FAILED'}")
except Exception as e:
    print(f"State update: ❌ FAILED - {e}")

print("Test complete.")