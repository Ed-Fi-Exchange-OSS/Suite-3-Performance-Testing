# Performance Comparison: 2025-10-25-12-11-async-commit vs Axel-30-minute-WARN-level

## Test Configuration
Both tests ran for 30 minutes with 10 concurrent users.

---

## Overall Performance Summary

| Metric | Baseline (Axel) | Current Test | Change | % Difference |
|--------|-----------------|--------------|--------|--------------|
| **Total Requests** | 134,322 | 104,708 | -29,614 | **-22.0%** ⬇️ |
| **Throughput (req/s)** | 74.66 | 58.20 | -16.46 | **-22.0%** ⬇️ |
| **Failure Count** | 0 | 0 | 0 | **0%** ✅ |
| **Median Response Time** | 5ms | 5ms | 0ms | **0%** ✅ |
| **Average Response Time** | 18.42ms | 21.85ms | +3.43ms | **+18.6%** ⬇️ |
| **95th Percentile** | 9ms | 10ms | +1ms | **+11.1%** ⬇️ |
| **98th Percentile** | 400ms | 430ms | +30ms | **+7.5%** ⬇️ |
| **99th Percentile** | 420ms | 450ms | +30ms | **+7.1%** ⬇️ |
| **Max Response Time** | 569ms | 980ms | +411ms | **+72.2%** ⬇️ |

### Key Findings

✅ **Excellent:** Median response time remains identical at 5ms - typical user experience unchanged
⚠️ **Concern:** 22% reduction in throughput (74.66 → 58.20 req/s)
⚠️ **Concern:** Worse tail latencies, especially max response time (+72%)
⚠️ **Concern:** 29,614 fewer requests processed in same time period

---

## Detailed Endpoint Analysis

### Critical Slowdowns (Endpoints with Significant Regressions)

#### 1. GET /data/ed-fi/localEducationAgencies (High Volume Endpoint)
| Metric | Baseline | Current | Change |
|--------|----------|---------|--------|
| Request Count | 4,458 | 4,221 | -237 (-5.3%) |
| Median | 410ms | 430ms | **+20ms (+4.9%)** ⬇️ |
| Average | 397.72ms | 420.22ms | **+22.5ms (+5.7%)** ⬇️ |
| Max | 569ms | 980ms | **+411ms (+72%)** ⬇️ |
| P99 | 440ms | 490ms | **+50ms (+11.4%)** ⬇️ |

**Analysis:** This is the slowest endpoint in both tests but shows significant regression in the current test, particularly in tail latencies.

#### 2. POST /data/ed-fi/calendars (Highest Volume Endpoint)
| Metric | Baseline | Current | Change |
|--------|----------|---------|--------|
| Request Count | 35,610 | 25,594 | **-10,016 (-28.1%)** ⬇️ |
| Median | 6ms | 6ms | 0ms ✅ |
| Average | 5.94ms | 5.65ms | +0.29ms (+4.9%) ✅ |
| Max | 194ms | 120ms | -74ms (+38.1%) ✅ |
| P99 | 11ms | 10ms | -1ms (+9.1%) ✅ |

**Analysis:** Despite 28% fewer requests, individual response times improved slightly. Lower throughput is the primary concern.

#### 3. DELETE /data/ed-fi/calendars/{id}
| Metric | Baseline | Current | Change |
|--------|----------|---------|--------|
| Request Count | 35,610 | 25,593 | -10,017 (-28.1%) |
| Median | 4ms | 4ms | 0ms ✅ |
| Average | 4.05ms | 3.71ms | **-0.34ms (-8.4%)** ✅ |
| Max | 312ms | 40ms | **-272ms (-87.2%)** ✅ |

**Analysis:** Significant improvement in max response time. Better consistency in current test.

#### 4. PUT /data/ed-fi/calendars/{id}
| Metric | Baseline | Current | Change |
|--------|----------|---------|--------|
| Request Count | 34,935 | 25,061 | -9,874 (-28.3%) |
| Median | 6ms | 6ms | 0ms ✅ |
| Average | 6.10ms | 5.83ms | **-0.27ms (-4.4%)** ✅ |
| Max | 80ms | 244ms | **+164ms (+205%)** ⬇️ |

**Analysis:** Median unchanged but max latency more than tripled.

---

### Endpoints with Concerning Max Latencies

Several endpoints show extreme outliers in the current test:

| Endpoint | Baseline Max | Current Max | Difference |
|----------|--------------|-------------|------------|
| POST /data/ed-fi/learningStandards | 10ms | 366ms | **+356ms** ⬇️ |
| POST /data/ed-fi/schools | 200ms | 397ms | **+197ms** ⬇️ |
| POST /data/ed-fi/locations | 23ms | 248ms | **+225ms** ⬇️ |
| POST /data/ed-fi/assessments | 33ms | 195ms | **+162ms** ⬇️ |
| PUT /data/ed-fi/assessments/{id} | 9ms | 185ms | **+176ms** ⬇️ |

---

### Positive Changes

#### Authentication Token Performance
| Metric | Baseline | Current | Change |
|--------|----------|---------|--------|
| POST /connect/token/ (Median) | 220ms | 140ms | **-80ms (-36.4%)** ✅ |
| Average | 219.5ms | 134.5ms | **-85ms (-38.7%)** ✅ |

**Analysis:** Authentication improved significantly, likely due to optimization or caching.

---

## Response Time Distribution Comparison

### Percentile Analysis
| Percentile | Baseline | Current | Change |
|------------|----------|---------|--------|
| 50% (Median) | 5ms | 5ms | 0ms ✅ |
| 66% | 6ms | 6ms | 0ms ✅ |
| 75% | 7ms | 6ms | **-1ms** ✅ |
| 80% | 7ms | 6ms | **-1ms** ✅ |
| 90% | 8ms | 7ms | **-1ms** ✅ |
| 95% | 9ms | 10ms | **+1ms** ⬇️ |
| 98% | 400ms | 430ms | **+30ms** ⬇️ |
| 99% | 420ms | 450ms | **+30ms** ⬇️ |
| 99.9% | 440ms | 480ms | **+40ms** ⬇️ |

**Analysis:** Performance is better or equal for 90% of requests, but degrades significantly for the top 5-10% of slowest requests.

---

## Root Cause Hypotheses

### 1. Throughput Reduction (-22%)
Possible causes:
- **Database contention:** Slower queries blocking other operations
- **Resource constraints:** CPU, memory, or I/O bottlenecks
- **Configuration change:** Connection pool size, worker threads, or async commit settings
- **Code change:** Less efficient algorithm or additional processing

### 2. Worse Tail Latencies (P98-P100)
Possible causes:
- **Garbage collection pauses:** More frequent or longer GC cycles
- **Database lock contention:** Occasional blocking on writes
- **Async commit timing:** If async commit is enabled, occasional flushes may cause spikes
- **Resource exhaustion:** Memory pressure or swap activity

### 3. Better 75th-90th Percentile Performance
Possible causes:
- **Optimization tradeoff:** Faster common path at expense of occasional slow operations
- **Caching benefits:** Better cache hit rates for typical requests
- **Async commit:** Faster write acknowledgment for most requests

---

## Recommendations

### Immediate Actions
1. **Investigate throughput drop:** Profile CPU, memory, and I/O utilization
2. **Analyze slow queries:** Check database logs for queries >100ms
3. **Review configuration:** Verify async commit settings and connection pool size
4. **Monitor GC activity:** Check for increased garbage collection pauses

### Performance Testing
1. **Run longer test:** 60-minute test to identify trend stability
2. **Vary load:** Test with 5, 15, 20 users to find scaling limits
3. **Isolate endpoints:** Run targeted tests on GET /localEducationAgencies
4. **A/B comparison:** Run baseline and current configurations side-by-side

### Optimization Targets
1. **Priority 1:** GET /localEducationAgencies (430ms median, 4,221 requests)
2. **Priority 2:** Investigate max latency spikes (980ms outliers)
3. **Priority 3:** Restore throughput to 74+ req/s baseline

---

## Conclusion

The current test shows **mixed results** compared to the baseline:

**Positive:**
- ✅ Median response time unchanged (5ms)
- ✅ 90% of requests at or better than baseline
- ✅ Authentication significantly faster (-36%)
- ✅ Zero failures maintained

**Negative:**
- ⚠️ 22% reduction in throughput (critical regression)
- ⚠️ Worse tail latencies (P95-P100)
- ⚠️ Max response time increased 72%
- ⚠️ 29,614 fewer requests processed

**Overall Assessment:** The system is **slower** overall despite maintaining good median performance. The throughput reduction and tail latency degradation suggest a performance regression that requires investigation before production deployment.

**Recommendation:** **Do not deploy** until throughput regression is understood and resolved.
