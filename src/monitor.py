"""Main monitoring loop with graceful shutdown support."""

import logging
import os
import signal
import sys
import time
from typing import Optional

import yaml

from .es_client import create_client
from .health_checks import (
    check_cluster_health,
    check_unassigned_shards,
    check_jvm_heap,
    check_disk_watermark,
    check_ilm_status,
    check_indexing_latency,
    check_search_latency,
    check_total_shard_count,
)
from .alerter import SlackAlerter, SNSAlerter

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s: %(message)s",
)
logger = logging.getLogger(__name__)

_shutdown_requested = False


def _handle_signal(signum: int, frame) -> None:
    global _shutdown_requested
    logger.info(f"Received signal {signum}, shutting down gracefully…")
    _shutdown_requested = True


def load_config(path: str = "config/clusters.yml") -> dict:
    with open(path) as f:
        return yaml.safe_load(f)


def run_checks(es, cluster_name: str, thresholds: dict) -> list:
    results = []
    results.append(check_cluster_health(es, cluster_name))
    results.append(check_unassigned_shards(es, cluster_name, thresholds.get("unassigned_shards", 0)))
    results.extend(check_jvm_heap(es, cluster_name, thresholds.get("heap_percent", 85)))
    results.extend(check_disk_watermark(es, cluster_name, thresholds.get("disk_watermark_percent", 80)))
    results.extend(check_ilm_status(es, cluster_name))
    results.extend(check_indexing_latency(es, cluster_name, thresholds.get("indexing_latency_ms", 100)))
    results.extend(check_search_latency(es, cluster_name, thresholds.get("search_latency_ms", 500)))
    results.append(check_total_shard_count(es, cluster_name, thresholds.get("total_shard_count", 1000)))
    return results


def _build_alerters(config: dict) -> list:
    alerters = []

    slack_url = os.environ.get(config.get("alerts", {}).get("slack", {}).get("webhook_url_env", ""))
    if slack_url:
        channel = config["alerts"]["slack"].get("channel", "#es-alerts")
        alerters.append(SlackAlerter(slack_url, channel))

    sns_arn = os.environ.get(config.get("alerts", {}).get("sns", {}).get("topic_arn_env", ""))
    if sns_arn:
        region = config["alerts"]["sns"].get("region", "us-east-1")
        alerters.append(SNSAlerter(sns_arn, region))

    return alerters


def run_once(config: dict, alerters: list) -> None:
    """Execute a single monitoring pass across all clusters."""
    for cluster_conf in config["clusters"]:
        if _shutdown_requested:
            break

        name = cluster_conf["name"]
        thresholds = cluster_conf.get("thresholds", {})

        logger.info(f"Checking cluster: {name}")
        try:
            es = create_client(cluster_conf)
            results = run_checks(es, name, thresholds)

            for r in results:
                icon = {"ok": "✅", "warning": "⚠️", "critical": "🔴"}[r.status]
                logger.info(f"  {icon} {r.check_name}: {r.message}")

            for alerter in alerters:
                alerter.send(results)

        except Exception as e:
            logger.error(f"  🔴 Failed to connect to {name}: {e}")


def main() -> None:
    signal.signal(signal.SIGTERM, _handle_signal)
    signal.signal(signal.SIGINT, _handle_signal)

    config = load_config()
    alerters = _build_alerters(config)
    interval: int = config.get("check_interval_seconds", 0)

    if interval > 0:
        logger.info(f"Running in loop mode (interval={interval}s). Send SIGTERM to stop.")
        while not _shutdown_requested:
            run_once(config, alerters)
            for _ in range(interval):
                if _shutdown_requested:
                    break
                time.sleep(1)
        logger.info("Shutdown complete.")
    else:
        run_once(config, alerters)
        logger.info("Done.")


if __name__ == "__main__":
    main()
