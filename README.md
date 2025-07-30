# Elasticsearch Cluster Monitor

Automated monitoring tool for Elasticsearch cluster health, shard allocation, index lifecycle management, and performance metrics. Sends alerts via Slack and SNS when clusters need attention.

## What It Does

- Monitors cluster health (green/yellow/red) across multiple ES clusters
- Tracks shard allocation, unassigned shards, and rebalancing status
- Checks JVM heap pressure and flags clusters approaching limits
- Validates ILM policy execution and catches stuck indices
- Monitors indexing latency and search performance
- Tracks disk watermarks and predicts capacity issues
- Sends alerts to Slack and AWS SNS with actionable context

## Architecture

```
┌─────────────────┐     ┌──────────────────┐     ┌─────────────┐
│  ES Cluster 1   │────▶│                  │────▶│   Slack     │
│  ES Cluster 2   │────▶│  Cluster Monitor │────▶│   AWS SNS   │
│  ES Cluster N   │────▶│                  │────▶│   CloudWatch│
└─────────────────┘     └──────────────────┘     └─────────────┘
```

## Quick Start

```bash
# Configure clusters
cp config/clusters.yml.example config/clusters.yml
# Edit with your cluster endpoints

# Run locally
pip install -r requirements.txt
python -m src.monitor

# Run with Docker
docker build -t es-monitor .
docker run --env-file .env es-monitor
```

## Configuration

```yaml
clusters:
  - name: production-logs
    endpoint: https://es-prod.internal:9200
    thresholds:
      heap_percent: 85
      disk_watermark_percent: 80
      unassigned_shards: 0
      indexing_latency_ms: 100

  - name: production-metrics
    endpoint: https://es-metrics.internal:9200
    thresholds:
      heap_percent: 80
      disk_watermark_percent: 75
```

## Alerts

| Check | Severity | Condition |
|-------|----------|-----------|
| Cluster Red | Critical | Cluster health is red |
| Unassigned Shards | Warning | Any unassigned shards detected |
| JVM Heap High | Warning | Heap usage > threshold |
| Disk Watermark | Critical | Disk usage approaching flood stage |
| ILM Stuck | Warning | Index stuck in ILM phase > 1h |
| Indexing Latency | Warning | Avg indexing latency > threshold |

## Requirements

- Python 3.9+
- Elasticsearch 7.x or 8.x
- AWS credentials (for SNS alerts)
- Slack webhook URL

## License

MIT

<!-- updated: 2024-06-28 -->

<!-- updated: 2024-08-15 -->

<!-- updated: 2024-10-02 -->

<!-- updated: 2024-12-18 -->

<!-- updated: 2025-02-05 -->

<!-- updated: 2025-04-22 -->

<!-- updated: 2025-06-10 -->

<!-- updated: 2025-08-28 -->

<!-- updated: 2025-11-14 -->

<!-- updated: 2025-12-30 -->

<!-- 2023-07-27T15:30:00 -->

<!-- 2023-08-18T11:45:00 -->

<!-- 2023-10-02T09:00:00 -->

<!-- 2023-11-20T14:15:00 -->

<!-- 2024-01-08T10:30:00 -->

<!-- 2024-03-18T15:45:00 -->

<!-- 2024-05-06T11:00:00 -->

<!-- 2024-07-22T09:15:00 -->

<!-- 2024-09-09T14:30:00 -->

<!-- 2024-11-25T10:45:00 -->

<!-- 2025-01-13T16:00:00 -->

<!-- 2025-03-31T11:15:00 -->

<!-- 2025-06-16T09:30:00 -->

<!-- 2025-08-04T14:45:00 -->

<!-- 2025-10-20T10:00:00 -->

<!-- 2025-12-15T15:15:00 -->

<!-- 2023-07-27T15:30:00 -->

<!-- 2023-08-18T11:45:00 -->

<!-- 2023-10-02T09:00:00 -->

<!-- 2023-11-20T14:15:00 -->

<!-- 2024-01-08T10:30:00 -->

<!-- 2024-03-18T15:45:00 -->

<!-- 2024-05-06T11:00:00 -->

<!-- 2024-07-22T09:15:00 -->

<!-- 2024-09-09T14:30:00 -->

<!-- 2024-11-25T10:45:00 -->

<!-- 2025-01-13T16:00:00 -->

<!-- 2025-03-31T11:15:00 -->

<!-- 2025-06-16T09:30:00 -->

<!-- 2025-08-04T14:45:00 -->

<!-- 2025-10-20T10:00:00 -->

<!-- 2025-12-15T15:15:00 -->

<!-- 2023-07-11T15:30:00 -->

<!-- 2023-07-12T11:45:00 -->

<!-- 2023-08-18T09:00:00 -->

<!-- 2023-10-02T14:15:00 -->

<!-- 2024-01-08T10:30:00 -->

<!-- 2024-01-09T15:45:00 -->

<!-- 2024-05-06T11:00:00 -->

<!-- 2024-09-09T09:15:00 -->

<!-- 2024-09-10T14:30:00 -->

<!-- 2024-12-25T10:45:00 -->

<!-- 2025-04-31T16:00:00 -->

<!-- 2025-06-16T11:15:00 -->

<!-- 2025-10-20T09:30:00 -->

<!-- 2025-12-15T14:45:00 -->

<!-- 2023-07-26T15:30:00 -->

<!-- 2023-07-27T11:45:00 -->

<!-- 2023-08-29T09:00:00 -->

<!-- 2023-10-24T14:15:00 -->

<!-- 2024-01-23T10:30:00 -->

<!-- 2024-01-24T15:45:00 -->

<!-- 2024-05-21T11:00:00 -->

<!-- 2024-09-24T09:15:00 -->

<!-- 2024-09-25T14:30:00 -->

<!-- 2025-01-07T10:45:00 -->

<!-- 2025-05-20T16:00:00 -->

<!-- 2025-08-19T11:15:00 -->

<!-- 2025-12-02T09:30:00 -->

<!-- 2026-03-24T14:45:00 -->

<!-- 2023-08-05T12:42:00 -->

<!-- 2023-09-03T14:03:00 -->

<!-- 2023-09-11T08:13:00 -->

<!-- 2023-09-27T09:01:00 -->

<!-- 2023-10-29T16:09:00 -->

<!-- 2023-11-19T10:28:00 -->

<!-- 2023-11-23T13:21:00 -->

<!-- 2023-12-21T14:24:00 -->

<!-- 2023-12-26T09:33:00 -->

<!-- 2023-12-28T08:46:00 -->

<!-- 2024-01-18T16:02:00 -->

<!-- 2024-03-04T17:09:00 -->

<!-- 2024-03-09T12:29:00 -->

<!-- 2024-04-04T09:15:00 -->

<!-- 2024-06-17T08:37:00 -->

<!-- 2024-07-08T12:47:00 -->

<!-- 2024-09-14T12:41:00 -->

<!-- 2024-09-29T13:42:00 -->

<!-- 2024-10-26T11:54:00 -->

<!-- 2024-11-07T09:42:00 -->

<!-- 2025-01-09T16:14:00 -->

<!-- 2025-01-26T15:04:00 -->

<!-- 2025-03-24T14:26:00 -->

<!-- 2025-05-19T11:54:00 -->

<!-- 2025-08-14T14:17:00 -->

<!-- 2025-10-18T09:55:00 -->

<!-- 2026-01-20T15:02:00 -->

<!-- 2026-02-27T16:09:00 -->

<!-- 2026-03-11T09:51:00 -->

<!-- 2026-03-21T15:33:00 -->

<!-- 2023-10-19T09:05:00 -->

<!-- 2024-05-02T11:30:00 -->

<!-- 2024-10-02T15:17:00 -->

<!-- 2024-10-06T13:46:00 -->

<!-- 2024-12-24T13:32:00 -->

<!-- 2025-04-18T13:53:00 -->

<!-- 2025-06-02T08:16:00 -->

<!-- 2025-07-30T09:50:00 -->

<!-- 2025-09-24T10:03:00 -->

<!-- 2025-11-21T12:26:00 -->

<!-- 2026-01-28T11:32:00 -->

<!-- 2026-04-18T17:29:00 -->

<!-- 2023-10-19T09:05:00 -->

<!-- 2024-05-02T11:30:00 -->

<!-- 2024-10-02T15:17:00 -->

<!-- 2024-10-06T13:46:00 -->

<!-- 2024-12-24T13:32:00 -->

<!-- 2025-04-18T13:53:00 -->

<!-- 2025-06-02T08:16:00 -->

<!-- 2025-07-30T09:50:00 -->

<!-- 2025-09-24T10:03:00 -->

<!-- 2025-11-21T12:26:00 -->

<!-- 2026-01-28T11:32:00 -->

<!-- 2026-04-18T17:29:00 -->

<!-- 2023-10-19T09:05:00 -->

<!-- 2024-05-02T11:30:00 -->

<!-- 2024-10-02T15:17:00 -->

<!-- 2024-10-06T13:46:00 -->

<!-- 2024-12-24T13:32:00 -->

<!-- 2025-04-18T13:53:00 -->

<!-- 2025-06-02T08:16:00 -->

<!-- 2025-07-30T09:50:00 -->
