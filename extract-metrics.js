#!/usr/bin/env node

/**
 * Performance Metrics Extraction Script
 *
 * Extracts key metrics from Locust performance test results for executive reporting.
 * Focuses on Median and 95th percentile, separating reads from writes.
 *
 * Usage:
 *   node extract-metrics.js [path-to-volume_stats.csv]
 *   node extract-metrics.js DmsTestResults/volume_stats.csv
 *   node extract-metrics.js run1/volume_stats.csv run2/volume_stats.csv run3/volume_stats.csv
 */

const fs = require('fs');
const path = require('path');

// Parse CSV line into array, handling quoted values
function parseCSVLine(line) {
  const result = [];
  let current = '';
  let inQuotes = false;

  for (let i = 0; i < line.length; i++) {
    const char = line[i];

    if (char === '"') {
      inQuotes = !inQuotes;
    } else if (char === ',' && !inQuotes) {
      result.push(current.trim());
      current = '';
    } else {
      current += char;
    }
  }
  result.push(current.trim());
  return result;
}

// Parse volume_stats.csv file
function parseVolumeStats(filePath) {
  const content = fs.readFileSync(filePath, 'utf-8');
  const lines = content.trim().split('\n');

  if (lines.length < 2) {
    throw new Error('CSV file must have header and data rows');
  }

  const headers = parseCSVLine(lines[0]);
  const data = [];

  for (let i = 1; i < lines.length; i++) {
    const values = parseCSVLine(lines[i]);
    if (values.length === headers.length) {
      const row = {};
      headers.forEach((header, index) => {
        row[header] = values[index];
      });
      data.push(row);
    }
  }

  return data;
}

// Categorize operations
function categorizeOperation(type, name) {
  const upperType = type.toUpperCase();

  // Skip aggregated rows and token endpoint
  if (!name || name === 'Aggregated' || name.includes('token')) {
    return 'skip';
  }

  if (upperType === 'GET') {
    return 'read';
  } else if (['POST', 'PUT', 'DELETE'].includes(upperType)) {
    return 'write';
  }

  return 'skip';
}

// Calculate weighted metrics based on request counts
function calculateWeightedMetrics(operations) {
  if (operations.length === 0) {
    return null;
  }

  let totalRequests = 0;
  let weightedMedian = 0;
  let weightedP95 = 0;

  operations.forEach(op => {
    const requests = parseInt(op['Request Count']) || 0;
    const median = parseInt(op['Median Response Time']) || parseInt(op['50%']) || 0;
    const p95 = parseInt(op['95%']) || 0;

    totalRequests += requests;
    weightedMedian += median * requests;
    weightedP95 += p95 * requests;
  });

  if (totalRequests === 0) {
    return null;
  }

  return {
    median: Math.round(weightedMedian / totalRequests),
    p95: Math.round(weightedP95 / totalRequests),
    requestCount: totalRequests,
    operationCount: operations.length
  };
}

// Extract metrics from a single test run
function extractMetrics(filePath) {
  const data = parseVolumeStats(filePath);

  const writeOps = [];
  const readOps = [];

  data.forEach(row => {
    const category = categorizeOperation(row.Type, row.Name);

    if (category === 'write') {
      writeOps.push(row);
    } else if (category === 'read') {
      readOps.push(row);
    }
  });

  const writeMetrics = calculateWeightedMetrics(writeOps);
  const readMetrics = calculateWeightedMetrics(readOps);

  return {
    fileName: path.basename(path.dirname(filePath)) + '/' + path.basename(filePath),
    write: writeMetrics,
    read: readMetrics,
    timestamp: new Date().toISOString()
  };
}

// Format metrics for display
function formatMetrics(metrics) {
  console.log('\n' + '='.repeat(70));
  console.log(`File: ${metrics.fileName}`);
  console.log('='.repeat(70));

  if (metrics.write) {
    console.log('\n📝 WRITE OPERATIONS (POST/PUT/DELETE)');
    console.log(`   Median Response Time: ${metrics.write.median}ms`);
    console.log(`   95th Percentile:      ${metrics.write.p95}ms`);
    console.log(`   Total Requests:       ${metrics.write.requestCount.toLocaleString()}`);
    console.log(`   Operations Tested:    ${metrics.write.operationCount}`);
  } else {
    console.log('\n📝 WRITE OPERATIONS: No data found');
  }

  if (metrics.read) {
    console.log('\n📖 READ OPERATIONS (GET)');
    console.log(`   Median Response Time: ${metrics.read.median}ms`);
    console.log(`   95th Percentile:      ${metrics.read.p95}ms`);
    console.log(`   Total Requests:       ${metrics.read.requestCount.toLocaleString()}`);
    console.log(`   Operations Tested:    ${metrics.read.operationCount}`);
  } else {
    console.log('\n📖 READ OPERATIONS: No data found');
  }
}

// Output comparison table for multiple runs
function outputComparisonTable(allMetrics) {
  console.log('\n\n' + '='.repeat(70));
  console.log('COMPARISON ACROSS TEST RUNS');
  console.log('='.repeat(70));

  console.log('\nWRITE OPERATIONS (POST/PUT/DELETE):');
  console.log('-'.repeat(70));
  console.log('Run'.padEnd(30) + 'Median'.padEnd(12) + 'P95'.padEnd(12) + 'Requests');
  console.log('-'.repeat(70));

  allMetrics.forEach((metrics, index) => {
    const label = `Run ${index + 1}`.padEnd(30);
    if (metrics.write) {
      const median = `${metrics.write.median}ms`.padEnd(12);
      const p95 = `${metrics.write.p95}ms`.padEnd(12);
      const requests = metrics.write.requestCount.toLocaleString();
      console.log(label + median + p95 + requests);
    } else {
      console.log(label + 'No data');
    }
  });

  console.log('\nREAD OPERATIONS (GET):');
  console.log('-'.repeat(70));
  console.log('Run'.padEnd(30) + 'Median'.padEnd(12) + 'P95'.padEnd(12) + 'Requests');
  console.log('-'.repeat(70));

  allMetrics.forEach((metrics, index) => {
    const label = `Run ${index + 1}`.padEnd(30);
    if (metrics.read) {
      const median = `${metrics.read.median}ms`.padEnd(12);
      const p95 = `${metrics.read.p95}ms`.padEnd(12);
      const requests = metrics.read.requestCount.toLocaleString();
      console.log(label + median + p95 + requests);
    } else {
      console.log(label + 'No data');
    }
  });
}

// Output JSON for programmatic use / charting libraries
function outputJSON(allMetrics) {
  const chartData = {
    write: {
      labels: [],
      median: [],
      p95: []
    },
    read: {
      labels: [],
      median: [],
      p95: []
    }
  };

  allMetrics.forEach((metrics, index) => {
    const label = `Run ${index + 1}`;

    if (metrics.write) {
      chartData.write.labels.push(label);
      chartData.write.median.push(metrics.write.median);
      chartData.write.p95.push(metrics.write.p95);
    }

    if (metrics.read) {
      chartData.read.labels.push(label);
      chartData.read.median.push(metrics.read.median);
      chartData.read.p95.push(metrics.read.p95);
    }
  });

  console.log('\n\n' + '='.repeat(70));
  console.log('JSON OUTPUT (for charting libraries)');
  console.log('='.repeat(70));
  console.log(JSON.stringify(chartData, null, 2));
}

// Main execution
function main() {
  const args = process.argv.slice(2);

  if (args.length === 0) {
    // Default to DmsTestResults/volume_stats.csv
    const defaultPath = path.join(__dirname, 'DmsTestResults', 'volume_stats.csv');
    if (fs.existsSync(defaultPath)) {
      args.push(defaultPath);
    } else {
      console.error('Usage: node extract-metrics.js <path-to-volume_stats.csv> [more-files...]');
      console.error('');
      console.error('Examples:');
      console.error('  node extract-metrics.js DmsTestResults/volume_stats.csv');
      console.error('  node extract-metrics.js run1/volume_stats.csv run2/volume_stats.csv');
      process.exit(1);
    }
  }

  const allMetrics = [];

  // Process each file
  args.forEach(filePath => {
    try {
      const metrics = extractMetrics(filePath);
      allMetrics.push(metrics);
      formatMetrics(metrics);
    } catch (error) {
      console.error(`\nError processing ${filePath}:`, error.message);
    }
  });

  // If multiple files, show comparison
  if (allMetrics.length > 1) {
    outputComparisonTable(allMetrics);
    outputJSON(allMetrics);
  }

  // Output CSV format for easy Excel import
  if (allMetrics.length > 0) {
    console.log('\n\n' + '='.repeat(70));
    console.log('CSV FORMAT (copy to Excel/Google Sheets)');
    console.log('='.repeat(70));
    console.log('Run,Write_Median_ms,Write_P95_ms,Read_Median_ms,Read_P95_ms');
    allMetrics.forEach((metrics, index) => {
      const writeMedian = metrics.write ? metrics.write.median : '';
      const writeP95 = metrics.write ? metrics.write.p95 : '';
      const readMedian = metrics.read ? metrics.read.median : '';
      const readP95 = metrics.read ? metrics.read.p95 : '';
      console.log(`Run ${index + 1},${writeMedian},${writeP95},${readMedian},${readP95}`);
    });
  }
}

// Run the script
if (require.main === module) {
  main();
}

module.exports = { extractMetrics, parseVolumeStats };
