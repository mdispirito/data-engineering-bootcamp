# Data Pipeline Maintenance Plan

## Team Structure & Pipeline Ownership

### Theoretical Team Composition
- **Engineer A** (Senior Data Engineer)
- **Engineer B** (Data Engineer)
- **Engineer C** (Data Engineer) 
- **Engineer D** (Junior Data Engineer)

### Pipeline Ownership Matrix

| Pipeline | Primary Owner | Secondary Owner | Business Area |
|----------|---------------|-----------------|---------------|
| Aggregate Profit (Investors) | Engineer A | Engineer B | Profit |
| Unit-level Profit (Experiments) | Engineer B | Engineer C | Profit |
| Aggregate Growth (Investors) | Engineer C | Engineer A | Growth |
| Daily Growth (Experiments) | Engineer D | Engineer C | Growth |
| Aggregate Engagement (Investors) | Engineer B | Engineer A | Engagement |

- Senior engineer (A) owns critical investor-facing pipelines
- Each engineer has 1-2 primary responsibilities to avoid overload
- Secondary ownership ensures knowledge sharing and backup coverage
- Junior engineer (D) starts with experimental pipeline to learn

## On-Call Schedule

### Rotation Schedule (2-week rotations)

| Week | Primary On-Call | Secondary On-Call |
|------|----------------|-------------------|
| 1  | Engineer A     | Engineer B        |
| 2  | Engineer C     | Engineer D        |
| 3  | Engineer B     | Engineer A        |
| 4  | Engineer D     | Engineer C        |

### Holiday Coverage

**Holiday Break (American Thanksgiving through New Years):**
- Split into 1 - 3 day shifts instead of full weeks
- Fill the schedule on a volunteer basis
    - Start by asking everyone to submit 5 days they prefer and 5 days they want to avoid
- Manager is responsible for resolving the final schedule

**Emergency Escalation:**
- Primary → Secondary → Team Lead → Manager
- Critical investor pipeline failures: immediate escalation
- Experimental pipeline failures: next business day resolution

## Runbooks for Investor-Facing Pipelines

### 1. Aggregate Profit Pipeline (Investors)

**Pipeline Overview:**
- **Frequency:** Daily (runs at 6 AM UTC)
- **Data Sources:** Revenue DB, Cost DB, External vendor APIs
- **Output:** Executive dashboard, monthly investor reports
- **SLA:** 99.5% uptime, <2 hour delay tolerance

**Potential Failure Scenarios:**

1. **Revenue Data Source Unavailable**
   - Symptoms: Pipeline timeout, missing revenue records
   - Impact: Incomplete profit calculations
   - Monitoring: Data freshness alerts, row count validation

2. **Cost Allocation Logic Changes**
   - Symptoms: Sudden profit margin changes (>10% variance)
   - Impact: Inaccurate profit reporting to investors
   - Monitoring: Variance detection alerts, data quality checks

3. **Currency Conversion API Failures**
   - Symptoms: Missing FX rates, default rate usage
   - Impact: Incorrect international profit calculations
   - Monitoring: API response monitoring, rate validation

4. **Data Processing Delays**
   - Symptoms: Pipeline running beyond 8 AM UTC
   - Impact: Late investor dashboard updates
   - Monitoring: Runtime duration alerts

### 2. Aggregate Growth Pipeline (Investors)

**Pipeline Overview:**
- **Frequency:** Daily (runs at 5 AM UTC)
- **Data Sources:** User activity DB, subscription DB, product analytics
- **Output:** Growth metrics dashboard, quarterly reports
- **SLA:** 99.5% uptime, <1 hour delay tolerance

**Potential Failure Scenarios:**

1. **User Activity Data Corruption**
   - Symptoms: Negative growth rates, impossible user counts
   - Impact: Misleading growth metrics to investors
   - Monitoring: Sanity checks, growth rate boundaries

2. **Subscription Database Connectivity Issues**
   - Symptoms: Connection timeouts, incomplete subscription data
   - Impact: Inaccurate subscriber growth calculations
   - Monitoring: Connection health checks, data completeness validation

3. **Duplicate User Records**
   - Symptoms: Inflated user growth numbers
   - Impact: Overstated growth metrics
   - Monitoring: Duplicate detection algorithms, user ID validation

4. **Time Zone Calculation Errors**
   - Symptoms: Inconsistent daily growth patterns
   - Impact: Incorrect growth trend reporting
   - Monitoring: UTC conversion validation, timestamp audits

### 3. Aggregate Engagement Pipeline (Investors)

**Pipeline Overview:**
- **Frequency:** Daily (runs at 7 AM UTC)
- **Data Sources:** Event tracking, session analytics, feature usage logs
- **Output:** Engagement KPI dashboard, monthly investor metrics
- **SLA:** 99.5% uptime, <90 minute delay tolerance

**Potential Failure Scenarios:**

1. **Event Tracking Data Loss**
   - Symptoms: Sudden drop in event volumes, missing event types
   - Impact: Understated engagement metrics
   - Monitoring: Event volume anomaly detection, event type completeness

2. **Session Timeout Logic Changes**
   - Symptoms: Dramatic changes in session duration metrics
   - Impact: Inaccurate engagement depth reporting
   - Monitoring: Session duration variance alerts, logic validation

3. **Bot Traffic Infiltration**
   - Symptoms: Unnaturally high engagement rates, suspicious patterns
   - Impact: Inflated engagement metrics
   - Monitoring: Bot detection algorithms, traffic pattern analysis

4. **Feature Usage Calculation Errors**
   - Symptoms: Feature adoption rates >100% or negative values
   - Impact: Incorrect feature engagement reporting
   - Monitoring: Percentage boundary checks, adoption rate validation

## Monitoring & Alerting Strategy

### Critical Alerts (Immediate Response)
- Investor pipeline failures
- Data quality issues affecting investor metrics
- SLA breaches on investor-facing pipelines

### Warning Alerts (Next Business Day)
- Experimental pipeline delays
- Data freshness issues on non-critical data
- Performance degradation within SLA

### Communication Plan
- **Slack channel:** #data-pipeline-alerts
- **Email escalation:** For >2 hour investor pipeline outages
- **Status page updates:** For planned maintenance affecting investor dashboards