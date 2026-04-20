from __future__ import annotations

import logging
import os
from pathlib import Path
from typing import Any, Dict

import yaml

DEFAULT_LOG_FORMAT = "%(asctime)s | %(levelname)-8s | %(name)s | %(message)s"


def load_yaml_config(config_path: str = "config.yaml") -> Dict[str, Any]:
    path = Path(config_path)
    if not path.exists():
        raise FileNotFoundError(f"Config file not found: {config_path}")

    with path.open("r", encoding="utf-8") as file:
        return yaml.safe_load(file) or {}


def setup_logging(config_path: str = "config.yaml") -> None:
    config: Dict[str, Any] = {}
    try:
        config = load_yaml_config(config_path)
    except FileNotFoundError:
        # Keep logging setup resilient, even if config.yaml is not present yet.
        pass

    logging_config = config.get("logging", {}) if isinstance(config, dict) else {}
    level_name = str(
        os.getenv("LOG_LEVEL", logging_config.get("level", "INFO"))
    ).upper()
    log_format = str(os.getenv("LOG_FORMAT", logging_config.get("format", DEFAULT_LOG_FORMAT)))

    level = getattr(logging, level_name, logging.INFO)
    logging.basicConfig(
        level=level,
        format=log_format,
        datefmt="%Y-%m-%d %H:%M:%S",
        force=True,
    )

    # Third-party HTTP clients are noisy on DEBUG; keep them readable by default.
    logging.getLogger("urllib3").setLevel(logging.WARNING)
    logging.getLogger("httpx").setLevel(logging.WARNING)
