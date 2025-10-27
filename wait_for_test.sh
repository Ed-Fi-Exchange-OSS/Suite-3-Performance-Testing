#!/bin/bash
# Wait for the test to complete
TEST_DIR="DmsTestResults/2025-10-26-16-41-no-replica-or-auth-columns-conf-tuned-npgsql-fix-new-index"

echo "Waiting for test to complete..."
while pgrep -f "edfi_performance_test.*2025-10-26-16-41" > /dev/null; do
    sleep 60
done

echo "Test completed!"
echo ""
echo "Final stats:"
tail -1 "$TEST_DIR/volume_stats.csv"
