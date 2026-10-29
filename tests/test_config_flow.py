"""Tests for the Pyroscope config and options flows."""

from unittest.mock import MagicMock

from pytest_homeassistant_custom_component.common import MockConfigEntry

from homeassistant.config_entries import SOURCE_USER
from homeassistant.const import CONF_PASSWORD, CONF_URL, CONF_USERNAME
from homeassistant.core import HomeAssistant
from homeassistant.data_entry_flow import FlowResultType

from custom_components.pyroscope.const import (
    CONF_APPLICATION_NAME,
    CONF_MEMORY_PROFILING,
    CONF_SAMPLE_RATE,
    DOMAIN,
)

USER_INPUT = {
    CONF_URL: "https://profiles.example.com",
    CONF_USERNAME: "123456",
    CONF_PASSWORD: "test-token",
    CONF_APPLICATION_NAME: "homeassistant",
}


async def test_user_flow(hass: HomeAssistant, mock_pyroscope: MagicMock) -> None:
    """A valid URL creates an entry titled with the service name."""
    result = await hass.config_entries.flow.async_init(
        DOMAIN, context={"source": SOURCE_USER}
    )
    assert result["type"] is FlowResultType.FORM

    result = await hass.config_entries.flow.async_configure(
        result["flow_id"], USER_INPUT
    )
    assert result["type"] is FlowResultType.CREATE_ENTRY
    assert result["title"] == "homeassistant"
    assert result["data"] == USER_INPUT


async def test_user_flow_invalid_url(hass: HomeAssistant) -> None:
    """A URL without a scheme is rejected."""
    result = await hass.config_entries.flow.async_init(
        DOMAIN, context={"source": SOURCE_USER}
    )
    result = await hass.config_entries.flow.async_configure(
        result["flow_id"], {**USER_INPUT, CONF_URL: "profiles.example.com"}
    )
    assert result["type"] is FlowResultType.FORM
    assert result["errors"] == {CONF_URL: "invalid_url"}


async def test_single_instance(hass: HomeAssistant) -> None:
    """A second entry is refused, because the profiler is process-wide."""
    MockConfigEntry(domain=DOMAIN, data=USER_INPUT).add_to_hass(hass)
    result = await hass.config_entries.flow.async_init(
        DOMAIN, context={"source": SOURCE_USER}
    )
    assert result["type"] is FlowResultType.ABORT
    assert result["reason"] == "single_instance_allowed"


async def test_options_flow(hass: HomeAssistant, mock_pyroscope: MagicMock) -> None:
    """Saving options reloads the entry with the new sample rate."""
    entry = MockConfigEntry(domain=DOMAIN, data=USER_INPUT)
    entry.add_to_hass(hass)
    await hass.config_entries.async_setup(entry.entry_id)
    await hass.async_block_till_done()

    result = await hass.config_entries.options.async_init(entry.entry_id)
    assert result["type"] is FlowResultType.FORM

    result = await hass.config_entries.options.async_configure(
        result["flow_id"], {CONF_SAMPLE_RATE: 50, CONF_MEMORY_PROFILING: True}
    )
    await hass.async_block_till_done()
    assert result["type"] is FlowResultType.CREATE_ENTRY
    assert entry.options == {CONF_SAMPLE_RATE: 50, CONF_MEMORY_PROFILING: True}

    mock_pyroscope.shutdown.assert_called_once()
    assert mock_pyroscope.configure.call_count == 2
    kwargs = mock_pyroscope.configure.call_args.kwargs
    assert kwargs["sample_rate"] == 50
    assert kwargs["mem_enabled"] is True
