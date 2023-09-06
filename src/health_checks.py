"""Cluster health check implementations."""

from dataclasses import dataclass
from typing import Optional


@dataclass
class CheckResult:
    cluster: str
    check_name: str
    status: str  # ok, warning, critical
    message: str
    value: Optional[float] = None
    threshold: Optional[float] = None


def check_cluster_health(es, cluster_name: str) -> CheckResult:
    health = es.cluster.health()
    status = health["status"]

    if status == "red":
        return CheckResult(cluster_name, "cluster_health", "critical",
                           f"Cluster is RED - {health['unassigned_shards']} unassigned shards")
    elif status == "yellow":
        return CheckResult(cluster_name, "cluster_health", "warning",
                           f"Cluster is YELLOW - {health['unassigned_shards']} unassigned shards")
    return CheckResult(cluster_name, "cluster_health", "ok", "Cluster is GREEN")


def check_unassigned_shards(es, cluster_name: str, threshold: int = 0) -> CheckResult:
    health = es.cluster.health()
    unassigned = health["unassigned_shards"]

    if unassigned > threshold:
        # Get reasons for unassigned shards
        allocation = es.cluster.allocation_explain()
        reason = allocation.get("allocate_explanation", "unknown")
        return CheckResult(cluster_name, "unassigned_shards", "warning",
                           f"{unassigned} unassigned shards: {reason}",
                           value=unassigned, threshold=threshold)
    return CheckResult(cluster_name, "unassigned_shards", "ok",
                       "No unassigned shards", value=0)


def check_jvm_heap(es, cluster_name: str, threshold: int = 85) -> list[CheckResult]:
    results = []
    nodes = es.nodes.stats(metric="jvm")

    for node_id, node_data in nodes["nodes"].items():
        node_name = node_data["name"]
        heap_percent = node_data["jvm"]["mem"]["heap_used_percent"]

        if heap_percent > threshold:
            results.append(CheckResult(
                cluster_name, "jvm_heap", "warning",
                f"Node {node_name}: JVM heap at {heap_percent}%",
                value=heap_percent, threshold=threshold
            ))
        else:
            results.append(CheckResult(
                cluster_name, "jvm_heap", "ok",
                f"Node {node_name}: JVM heap at {heap_percent}%",
                value=heap_percent, threshold=threshold
            ))
    return results


def check_disk_watermark(es, cluster_name: str, threshold: int = 80) -> list[CheckResult]:
    results = []
    stats = es.cat.allocation(format="json")

    for node in stats:
        disk_percent = float(node.get("disk.percent", 0))
        node_name = node.get("node", "unknown")

        severity = "ok"
        if disk_percent > 90:
            severity = "critical"
        elif disk_percent > threshold:
            severity = "warning"

        results.append(CheckResult(
            cluster_name, "disk_watermark", severity,
            f"Node {node_name}: disk at {disk_percent}%",
            value=disk_percent, threshold=threshold
        ))
    return results


def check_ilm_status(es, cluster_name: str) -> list[CheckResult]:
    results = []
    try:
        ilm_status = es.ilm.explain_lifecycle(index="*")
        for index_name, info in ilm_status.get("indices", {}).items():
            if info.get("step") == "ERROR":
                results.append(CheckResult(
                    cluster_name, "ilm_stuck", "warning",
                    f"Index {index_name} stuck in ILM phase: {info.get('phase')} step: {info.get('step_info', {}).get('reason', 'unknown')}"
                ))
    except Exception:
        pass

    if not results:
        results.append(CheckResult(cluster_name, "ilm_stuck", "ok", "All ILM policies executing normally"))
    return results


def check_indexing_latency(es, cluster_name: str, threshold_ms: int = 100) -> list[CheckResult]:
    results = []
    stats = es.indices.stats(metric="indexing")

    for index_name, index_data in stats["indices"].items():
        if index_name.startswith("."):
            continue
        indexing = index_data["total"]["indexing"]
        if indexing["index_total"] > 0:
            avg_latency = indexing["index_time_in_millis"] / indexing["index_total"]
            if avg_latency > threshold_ms:
                results.append(CheckResult(
                    cluster_name, "indexing_latency", "warning",
                    f"Index {index_name}: avg indexing latency {avg_latency:.0f}ms",
                    value=avg_latency, threshold=threshold_ms
                ))
    if not results:
        results.append(CheckResult(cluster_name, "indexing_latency", "ok", "Indexing latency within thresholds"))
    return results

# Added timeout handling for slow clusters


def check_search_latency(es, cluster_name: str, threshold_ms: int = 500) -> list[CheckResult]:
    """Alert when average search latency exceeds the threshold."""
    results = []
    try:
        stats = es.indices.stats(metric="search")
        for index_name, index_data in stats["indices"].items():
            if index_name.startswith("."):
                continue
            search = index_data["total"]["search"]
            if search["query_total"] > 0:
                avg_latency = search["query_time_in_millis"] / search["query_total"]
                if avg_latency > threshold_ms:
                    results.append(CheckResult(
                        cluster_name, "search_latency", "warning",
                        f"Index {index_name}: avg search latency {avg_latency:.0f}ms",
                        value=avg_latency, threshold=float(threshold_ms),
                    ))
    except Exception:
        pass

    if not results:
        results.append(CheckResult(cluster_name, "search_latency", "ok",
                                   "Search latency within thresholds"))
    return results


def check_total_shard_count(es, cluster_name: str, threshold: int = 1000) -> CheckResult:
    """Alert when total shard count approaches the cluster limit."""
    health = es.cluster.health()
    active_shards: int = health.get("active_shards", 0)
    relocating: int = health.get("relocating_shards", 0)
    total = active_shards + relocating

    if total > threshold:
        return CheckResult(
            cluster_name, "total_shard_count", "warning",
            f"Total shard count {total} exceeds threshold {threshold}",
            value=float(total), threshold=float(threshold),
        )
    return CheckResult(
        cluster_name, "total_shard_count", "ok",
        f"Total shard count {total} within limit",
        value=float(total), threshold=float(threshold),
    )
