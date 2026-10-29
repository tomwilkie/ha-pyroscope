"""Config flow for the Pyroscope integration."""

from __future__ import annotations

from typing import Any

import voluptuous as vol
from yarl import URL

from homeassistant.config_entries import (
    ConfigEntry,
    ConfigFlow,
    ConfigFlowResult,
    OptionsFlowWithReload,
)
from homeassistant.const import CONF_PASSWORD, CONF_URL, CONF_USERNAME
from homeassistant.core import callback
from homeassistant.helpers.selector import (
    BooleanSelector,
    NumberSelector,
    NumberSelectorConfig,
    NumberSelectorMode,
    TextSelector,
    TextSelectorConfig,
    TextSelectorType,
)

from .const import (
    CONF_APPLICATION_NAME,
    CONF_MEMORY_PROFILING,
    CONF_SAMPLE_RATE,
    DEFAULT_APPLICATION_NAME,
    DEFAULT_MEMORY_PROFILING,
    DEFAULT_SAMPLE_RATE,
    DOMAIN,
)

USER_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_URL): TextSelector(
            TextSelectorConfig(type=TextSelectorType.URL)
        ),
        vol.Optional(CONF_USERNAME): TextSelector(),
        vol.Optional(CONF_PASSWORD): TextSelector(
            TextSelectorConfig(type=TextSelectorType.PASSWORD)
        ),
        vol.Required(
            CONF_APPLICATION_NAME, default=DEFAULT_APPLICATION_NAME
        ): TextSelector(),
    }
)

OPTIONS_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_SAMPLE_RATE, default=DEFAULT_SAMPLE_RATE): NumberSelector(
            NumberSelectorConfig(min=1, max=1000, step=1, mode=NumberSelectorMode.BOX)
        ),
        vol.Required(
            CONF_MEMORY_PROFILING, default=DEFAULT_MEMORY_PROFILING
        ): BooleanSelector(),
    }
)


def _valid_url(url: str) -> bool:
    """Return True for an absolute http or https URL."""
    try:
        parsed = URL(url)
    except ValueError:
        return False
    return parsed.scheme in ("http", "https") and bool(parsed.host)


class PyroscopeConfigFlow(ConfigFlow, domain=DOMAIN):
    """Collect the Pyroscope server and credentials."""

    VERSION = 1

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Handle the initial step."""
        errors: dict[str, str] = {}
        if user_input is not None:
            if _valid_url(user_input[CONF_URL]):
                return self.async_create_entry(
                    title=user_input[CONF_APPLICATION_NAME], data=user_input
                )
            errors[CONF_URL] = "invalid_url"

        return self.async_show_form(
            step_id="user",
            data_schema=self.add_suggested_values_to_schema(USER_SCHEMA, user_input),
            errors=errors,
        )

    @staticmethod
    @callback
    def async_get_options_flow(config_entry: ConfigEntry) -> PyroscopeOptionsFlow:
        """Return the options flow."""
        return PyroscopeOptionsFlow()


class PyroscopeOptionsFlow(OptionsFlowWithReload):
    """Tune sampling. Saving reloads the entry, which restarts the profiler."""

    async def async_step_init(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Manage the options."""
        if user_input is not None:
            return self.async_create_entry(data=user_input)

        return self.async_show_form(
            step_id="init",
            data_schema=self.add_suggested_values_to_schema(
                OPTIONS_SCHEMA, self.config_entry.options
            ),
        )
