"""Elasticsearch client wrapper with connection pooling and retry."""

import os
import logging
from typing import Optional

from elasticsearch import Elasticsearch
from urllib3.util.retry import Retry
import boto3
from requests_aws4auth import AWS4Auth

logger = logging.getLogger(__name__)

DEFAULT_TIMEOUT = 30
MAX_RETRIES = 3
POOL_MAXSIZE = 10


def create_client(cluster_config: dict) -> Elasticsearch:
    """Create an Elasticsearch client with connection pooling.

    Supports ``aws_iam``, ``basic``, and unauthenticated connections.
    """
    endpoint: str = cluster_config["endpoint"]
    auth = cluster_config.get("auth", {})
    auth_type: str = auth.get("type", "none")
    timeout: int = cluster_config.get("timeout", DEFAULT_TIMEOUT)

    retry = Retry(total=MAX_RETRIES, backoff_factor=0.5,
                  status_forcelist=[502, 503, 504])

    if auth_type == "aws_iam":
        region = auth.get("region", "us-east-1")
        credentials = boto3.Session().get_credentials()
        awsauth = AWS4Auth(
            credentials.access_key,
            credentials.secret_key,
            region,
            "es",
            session_token=credentials.token,
        )
        return Elasticsearch(
            endpoint,
            http_auth=awsauth,
            use_ssl=True,
            verify_certs=True,
            timeout=timeout,
            max_retries=MAX_RETRIES,
            retry_on_timeout=True,
            maxsize=POOL_MAXSIZE,
        )

    if auth_type == "basic":
        username = os.environ[auth["username_env"]]
        password = os.environ[auth["password_env"]]
        return Elasticsearch(
            endpoint,
            basic_auth=(username, password),
            timeout=timeout,
            max_retries=MAX_RETRIES,
            retry_on_timeout=True,
            maxsize=POOL_MAXSIZE,
        )

    return Elasticsearch(
        endpoint,
        timeout=timeout,
        max_retries=MAX_RETRIES,
        retry_on_timeout=True,
        maxsize=POOL_MAXSIZE,
    )
