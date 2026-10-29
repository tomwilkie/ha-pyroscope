"""Tests for Pyroscope setup and unload."""

from unittest.mock import MagicMock

from pytest_homeassistant_custom_component.common import MockConfigEntry

from homeassistant.config_entries import ConfigEntryState
from homeassistant.const import (
    CONF_PASSWORD,
    CONF_URL,
    CONF_USERNAME,
    __version__ as HA_VERSION,
)
from homeassistant.core import HomeAssistant

from custom_components.pyroscope.const import CONF_APPLICATION_NAME, DOMAIN


async def test_setup_and_unload(hass: HomeAssistant, mock_pyroscope: MagicMock) -> None:
    """Setup starts the profiler with defaults, unload stops it."""
    entry = MockConfigEntry(
        domain=DOMAIN,
        data={
            CONF_URL: "https://profiles.example.com",
            CONF_USERNAME: "123456",
            CONF_PASSWORD: "test-token",
            CONF_APPLICATION_NAME: "homeassistant",
        },
    )
    entry.add_to_hass(hass)

    assert await hass.config_entries.async_setup(entry.entry_id)
    await hass.async_block_till_done()
    assert entry.state is ConfigEntryState.LOADED
    mock_pyroscope.configure.assert_called_once_with(
        application_name="homeassistant",
        server_address="https://profiles.example.com",
        basic_auth_username="123456",
        basic_auth_password="test-token",
        sample_rate=100,
        mem_enabled=False,
        tags={"ha_version": HA_VERSION},
    )

    assert await hass.config_entries.async_unload(entry.entry_id)
    await hass.async_block_till_done()
    assert entry.state is ConfigEntryState.NOT_LOADED
    mock_pyroscope.shutdown.assert_called_once()


async def test_setup_without_auth(
    hass: HomeAssistant, mock_pyroscope: MagicMock
) -> None:
    """A server without auth gets empty credentials."""
    entry = MockConfigEntry(
        domain=DOMAIN,
        data={
            CONF_URL: "http://pyroscope.local:4040",
            CONF_APPLICATION_NAME: "homeassistant",
        },
    )
    entry.add_to_hass(hass)

    assert await hass.config_entries.async_setup(entry.entry_id)
    kwargs = mock_pyroscope.configure.call_args.kwargs
    assert kwargs["basic_auth_username"] == ""
    assert kwargs["basic_auth_password"] == ""
