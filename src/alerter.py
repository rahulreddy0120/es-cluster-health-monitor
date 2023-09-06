"""Alert dispatching to Slack and SNS with retry support."""

import json
import logging
import time
from typing import Optional
from urllib.error import URLError
from urllib.request import Request, urlopen

import boto3

logger = logging.getLogger(__name__)

MAX_RETRIES = 3
RETRY_DELAY = 2


class SlackAlerter:
    """Send alert blocks to a Slack channel via incoming webhook."""

    def __init__(self, webhook_url: str, channel: str = "#es-alerts") -> None:
        self.webhook_url = webhook_url
        self.channel = channel

    def send(self, results: list) -> bool:
        """Post non-ok results to Slack. Returns True on success."""
        alerts = [r for r in results if r.status in ("warning", "critical")]
        if not alerts:
            return True

        blocks = self._build_blocks(alerts)
        payload = json.dumps({"channel": self.channel, "blocks": blocks}).encode()

        for attempt in range(1, MAX_RETRIES + 1):
            try:
                req = Request(self.webhook_url, data=payload,
                              headers={"Content-Type": "application/json"})
                urlopen(req, timeout=10)
                logger.info("Slack alert sent successfully")
                return True
            except URLError as e:
                logger.warning(f"Slack webhook attempt {attempt} failed: {e}")
                if attempt < MAX_RETRIES:
                    time.sleep(RETRY_DELAY * attempt)

        logger.error("Failed to send Slack alert after all retries")
        return False

    @staticmethod
    def _build_blocks(alerts: list) -> list[dict]:
        blocks: list[dict] = []
        for alert in alerts:
            emoji = "🔴" if alert.status == "critical" else "🟡"
            blocks.append({
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"{emoji} *{alert.cluster}* — {alert.check_name}\n{alert.message}",
                },
            })
        return blocks


class SNSAlerter:
    """Publish critical alerts to an SNS topic."""

    def __init__(self, topic_arn: str, region: str = "us-east-1") -> None:
        self.client = boto3.client("sns", region_name=region)
        self.topic_arn = topic_arn

    def send(self, results: list) -> bool:
        """Publish critical results to SNS. Returns True on success."""
        critical = [r for r in results if r.status == "critical"]
        if not critical:
            return True

        message = "\n".join(
            f"[{r.status.upper()}] {r.cluster} - {r.check_name}: {r.message}"
            for r in critical
        )

        try:
            self.client.publish(
                TopicArn=self.topic_arn,
                Subject="ES Cluster Alert - Critical",
                Message=message,
            )
            logger.info("SNS alert published")
            return True
        except Exception as e:
            logger.error(f"Failed to publish SNS alert: {e}")
            return False
