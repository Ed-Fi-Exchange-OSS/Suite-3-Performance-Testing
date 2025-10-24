# Performance Metrics Extraction Guide

## Quick Start

Extract metrics from your current test run:
```bash
node extract-metrics.js
```

This automatically reads from `DmsTestResults/volume_stats.csv`

## Compare Multiple Test Runs

After making performance tweaks, save each test result to a different directory and compare:

```bash
# Example: Compare baseline vs optimized
node extract-metrics.js \
  baseline/volume_stats.csv \
  optimized-v1/volume_stats.csv \
  optimized-v2/volume_stats.csv
```

## Output Formats

The script provides **three output formats**:

### 1. Human-Readable Summary
Shows detailed metrics for each test run with clear labels.

### 2. Comparison Table
When you provide multiple files, you get a side-by-side comparison:
```
WRITE OPERATIONS (POST/PUT/DELETE):
Run                           Median      P95         Requests
----------------------------------------------------------------------
Run 1                         6ms         8ms         20,082
Run 2                         5ms         7ms         20,100
Run 3                         4ms         6ms         20,150
```

### 3. CSV Format
Copy-paste directly into Excel or Google Sheets:
```csv
Run,Write_Median_ms,Write_P95_ms,Read_Median_ms,Read_P95_ms
Run 1,6,8,410,430
Run 2,5,7,380,410
Run 3,4,6,350,390
```

### 4. JSON Format (for charting)
When comparing multiple runs, you also get JSON suitable for Chart.js or other libraries:
```json
{
  "write": {
    "labels": ["Run 1", "Run 2", "Run 3"],
    "median": [6, 5, 4],
    "p95": [8, 7, 6]
  },
  "read": {
    "labels": ["Run 1", "Run 2", "Run 3"],
    "median": [410, 380, 350],
    "p95": [430, 410, 390]
  }
}
```

## Recommended Workflow

1. **Baseline Test**: Run performance tests and save results
   ```bash
   # After test completes
   cp -r DmsTestResults baseline-2024-01-24
   ```

2. **Make Performance Tweaks**: Optimize code, adjust configs, etc.

3. **Run New Test**: Execute tests again

4. **Compare Results**:
   ```bash
   node extract-metrics.js \
     baseline-2024-01-24/volume_stats.csv \
     DmsTestResults/volume_stats.csv
   ```

5. **Graph for Executives**: Copy the CSV output into Excel/Sheets and create a simple line chart

## What Gets Measured

- **Write Operations**: POST, PUT, DELETE requests
  - These are your data modification operations
  - Currently showing excellent 6ms median performance

- **Read Operations**: GET requests
  - Your query operations
  - Currently the GET `/localEducationAgencies` endpoint at 410ms median

- **Metrics**:
  - **Median**: What a typical user experiences
  - **95th Percentile**: What 95 out of 100 users experience

The script automatically:
- Weights metrics by request count (high-volume endpoints have more influence)
- Filters out authentication tokens and aggregated rows
- Separates reads from writes for clear comparison

## Executive Presentation Tips

**Simple soundbites**:
- "Write operations complete in 6 milliseconds for typical users"
- "95% of write operations finish in under 8 milliseconds"
- "After optimization, we reduced response times by 33%" (if you go 6ms → 4ms)

**For the graph**:
- Use two separate charts (Write vs Read)
- Label Y-axis as "Response Time (milliseconds)"
- Label X-axis as "Test Run" or date
- Show both Median and 95th percentile as separate lines
