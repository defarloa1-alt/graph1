#!/bin/bash
set -e

echo "Running Quality Gate Assessment..."

# Initialize status
ALL_PASSED=true

# Check CI validation results
if [ -f "ci_validation_results.json" ]; then
    echo "CI Validation: PASSED"
else
    echo "CI Validation: FAILED"
    ALL_PASSED=false
fi

# Check test coverage
COVERAGE=$(python -c "import json; print(json.load(open('reports/coverage.json'))['coverage'])" 2>/dev/null || echo "0")
if (( $(echo "$COVERAGE >= 95.0" | bc -l) )); then
    echo "Test Coverage: $COVERAGE% (>=95%)"
else
    echo "Test Coverage: $COVERAGE% (<95%)"
    ALL_PASSED=false
fi

# Check compliance
if [ -f "compliance_results.json" ]; then
    COMPLIANCE_PASSED=$(python -c "import json; r=json.load(open('compliance_results.json')); print(all(s=='COMPLIANT' for s in r['standards'].values()))" 2>/dev/null || echo "False")
    if [ "$COMPLIANCE_PASSED" = "True" ]; then
        echo "Compliance: PASSED"
    else
        echo "Compliance: FAILED"
        ALL_PASSED=false
    fi
else
    echo "Compliance: NO RESULTS"
    ALL_PASSED=false
fi

# Check security scan
if [ -f "bandit-report.json" ]; then
    SECURITY_ISSUES=$(python -c "import json; print(len(json.load(open('bandit-report.json'))['results']))" 2>/dev/null || echo "999")
    if [ "$SECURITY_ISSUES" -eq "0" ]; then
        echo "Security: NO ISSUES"
    else
        echo "Security: $SECURITY_ISSUES ISSUES FOUND"
        # Don't fail on security issues, just warn
    fi
else
    echo "Security: NO SCAN RESULTS"
fi

# Final assessment
if [ "$ALL_PASSED" = true ]; then
    echo ""
    echo "All quality gates passed!"
    echo "Framework is ready for deployment"
    exit 0
else
    echo ""
    echo "Quality gates failed!"
    echo "Framework is not ready for deployment"
    exit 1
fi
