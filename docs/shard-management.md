# Elasticsearch Shard Management Guide

## Shard Allocation

### Check current allocation
```
GET _cat/shards?v&s=state
GET _cluster/allocation/explain
```

### Common unassigned shard reasons
- **INDEX_CREATED**: New index, shards being allocated
- **CLUSTER_RECOVERED**: Cluster restart, shards recovering
- **NODE_LEFT**: Node went down, replicas being reassigned
- **ALLOCATION_FAILED**: Disk full, too many shards per node

### Force allocation
```
POST _cluster/reroute
{
  "commands": [{
    "allocate_stale_primary": {
      "index": "my-index",
      "shard": 0,
      "node": "node-1",
      "accept_data_loss": true
    }
  }]
}
```

## ILM Troubleshooting

### Check ILM status
```
GET my-index-*/_ilm/explain
```

### Retry failed ILM step
```
POST my-index-000001/_ilm/retry
```

### Common ILM issues
- Index too large to force-merge (reduce max_num_segments)
- Shrink fails due to allocation filters
- Rollover not triggering (check conditions)

## Disk Watermarks

| Watermark | Default | Action |
|-----------|---------|--------|
| Low | 85% | No new shards allocated to node |
| High | 90% | Shards relocated away from node |
| Flood | 95% | Index set to read-only |

### Clear flood stage read-only
```
PUT _all/_settings
{
  "index.blocks.read_only_allow_delete": null
}
```
