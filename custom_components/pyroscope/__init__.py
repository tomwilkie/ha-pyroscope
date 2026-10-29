"""Continuous profiling of Home Assistant with Pyroscope."""

from __future__ import annotations

from typing import Any

import pyroscope

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import (
    CONF_PASSWORD,
    CONF_URL,
    CONF_USERNAME,
    __version__ as HA_VERSION,
)
from homeassistant.core import HomeAssistant

from .const import (
    CONF_APPLICATION_NAME,
    CONF_MEMORY_PROFILING,
    CONF_SAMPLE_RATE,
    DEFAULT_MEMORY_PROFILING,
    DEFAULT_SAMPLE_RATE,
)


def _start(config: dict[str, Any]) -> None:
    """Start the profiler. The SDK is process-global, so only one entry runs."""
    pyroscope.configure(
        application_name=config[CONF_APPLICATION_NAME],
        server_address=config[CONF_URL],
        basic_auth_username=config.get(CONF_USERNAME, ""),
        basic_auth_password=config.get(CONF_PASSWORD, ""),
        sample_rate=int(config.get(CONF_SAMPLE_RATE, DEFAULT_SAMPLE_RATE)),
        mem_enabled=config.get(CONF_MEMORY_PROFILING, DEFAULT_MEMORY_PROFILING),
        tags={"ha_version": HA_VERSION},
    )


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Start profiling when the entry is set up."""
    await hass.async_add_executor_job(_start, {**entry.data, **entry.options})
    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Stop profiling and flush the last upload."""
    await hass.async_add_executor_job(pyroscope.shutdown)
    return True
