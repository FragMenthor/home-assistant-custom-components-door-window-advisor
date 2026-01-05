from __future__ import annotations

import voluptuous as vol
from homeassistant import config_entries
from homeassistant.core import callback
from homeassistant.helpers import selector
"""from homeassistant.const import UnitOfTemperature, UnitOfHumidity"""

from .const import (
    DOMAIN,
    CONF_NAME,
    CONF_INDOOR_TEMP,
    CONF_OUTDOOR_TEMP,
    CONF_INDOOR_HUM,
    CONF_OUTDOOR_HUM,
    CONF_CONTACT,
    CONF_WIND_SPEED,
    CONF_TARGET_TEMP,
    CONF_TARGET_HUM,
    CONF_TOL_TEMP,
    CONF_TOL_HUM,
    CONF_STATE_OPEN,
    CONF_STATE_CLOSE,
    CONF_STATE_KEEP,
    CONF_ENTITY_TYPE,
    TYPE_DOOR,
    TYPE_WINDOW,
    DEFAULT_TARGET_TEMP,
    DEFAULT_TARGET_HUM,
    DEFAULT_TOL_TEMP,
    DEFAULT_TOL_HUM,
    DEFAULT_STATE_OPEN,
    DEFAULT_STATE_CLOSE,
    DEFAULT_STATE_KEEP,
)


class DoorWindowAdvisorConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Config flow for Door/Window Advisor."""

    VERSION = 1

    async def async_step_user(self, user_input=None):
        """Handle the initial step."""
        errors: dict[str, str] = {}

        if user_input is not None:
            await self.async_set_unique_id(user_input[CONF_NAME])
            self._abort_if_unique_id_configured()

            return self.async_create_entry(
                title=user_input[CONF_NAME],
                data=user_input,
            )

        schema = vol.Schema(
            {
                vol.Required(CONF_NAME): str,
                vol.Required(
                    CONF_ENTITY_TYPE, default=TYPE_WINDOW
                ): selector.SelectSelector(
                    selector.SelectSelectorConfig(
                        options=[
                            selector.SelectOptionDict(value=TYPE_DOOR, label="Porta"),
                            selector.SelectOptionDict(value=TYPE_WINDOW, label="Janela"),
                        ],
                        mode=selector.SelectSelectorMode.DROPDOWN,
                    )
                ),
                vol.Required(CONF_INDOOR_TEMP): selector.EntitySelector(
                    selector.EntitySelectorConfig(
                        domain="sensor",
                        device_class="temperature",
                    )
                ),
                vol.Required(CONF_OUTDOOR_TEMP): selector.EntitySelector(
                    selector.EntitySelectorConfig(
                        domain="sensor",
                        device_class="temperature",
                    )
                ),
                vol.Required(CONF_INDOOR_HUM): selector.EntitySelector(
                    selector.EntitySelectorConfig(
                        domain="sensor",
                        device_class="humidity",
                    )
                ),
                vol.Required(CONF_OUTDOOR_HUM): selector.EntitySelector(
                    selector.EntitySelectorConfig(
                        domain="sensor",
                        device_class="humidity",
                    )
                ),
                vol.Required(CONF_CONTACT): selector.EntitySelector(
                    selector.EntitySelectorConfig(
                        domain="binary_sensor",
                        device_class="door",
                    )
                ),
                vol.Optional(CONF_WIND_SPEED): selector.EntitySelector(
                    selector.EntitySelectorConfig(
                        domain="sensor",
                        device_class="wind_speed",
                    )
                ),
                vol.Required(
                    CONF_TARGET_TEMP, default=DEFAULT_TARGET_TEMP
                ): vol.All(vol.Coerce(float), vol.Range(min=10, max=30)),
                vol.Required(
                    CONF_TARGET_HUM, default=DEFAULT_TARGET_HUM
                ): vol.All(vol.Coerce(float), vol.Range(min=20, max=80)),
                vol.Required(
                    CONF_TOL_TEMP, default=DEFAULT_TOL_TEMP
                ): vol.All(vol.Coerce(float), vol.Range(min=0.5, max=10)),
                vol.Required(
                    CONF_TOL_HUM, default=DEFAULT_TOL_HUM
                ): vol.All(vol.Coerce(float), vol.Range(min=1, max=30)),
                vol.Optional(CONF_STATE_OPEN, default=DEFAULT_STATE_OPEN): str,
                vol.Optional(CONF_STATE_CLOSE, default=DEFAULT_STATE_CLOSE): str,
                vol.Optional(CONF_STATE_KEEP, default=DEFAULT_STATE_KEEP): str,
            }
        )

        return self.async_show_form(
            step_id="user",
            data_schema=schema,
            errors=errors,
        )

    @staticmethod
    @callback
    def async_get_options_flow(config_entry: config_entries.ConfigEntry):
        """Get the options flow for this config entry."""
        return DoorWindowAdvisorOptionsFlow(config_entry)


class DoorWindowAdvisorOptionsFlow(config_entries.OptionsFlow):
    """Options flow for Door/Window Advisor."""

    def __init__(self, config_entry: config_entries.ConfigEntry) -> None:
        self._config_entry = config_entry

    async def async_step_init(self, user_input=None):
        """Handle the options step."""
        if user_input is not None:
            return self.async_create_entry(title="", data=user_input)

        current_data = self._config_entry.data
        options_data = self._config_entry.options

        def _opt(key, default=None):
            if key in options_data:
                return options_data[key]
            return current_data.get(key, default)

        schema = vol.Schema(
            {
                vol.Required(
                    CONF_ENTITY_TYPE,
                    default=_opt(CONF_ENTITY_TYPE, TYPE_WINDOW),
                ): selector.SelectSelector(
                    selector.SelectSelectorConfig(
                        options=[
                            selector.SelectOptionDict(value=TYPE_DOOR, label="Porta"),
                            selector.SelectOptionDict(value=TYPE_WINDOW, label="Janela"),
                        ],
                        mode=selector.SelectSelectorMode.DROPDOWN,
                    )
                ),
                vol.Required(
                    CONF_INDOOR_TEMP,
                    default=_opt(CONF_INDOOR_TEMP),
                ): selector.EntitySelector(
                    selector.EntitySelectorConfig(
                        domain="sensor",
                        device_class="temperature",
                    )
                ),
                vol.Required(
                    CONF_OUTDOOR_TEMP,
                    default=_opt(CONF_OUTDOOR_TEMP),
                ): selector.EntitySelector(
                    selector.EntitySelectorConfig(
                        domain="sensor",
                        device_class="temperature",
                    )
                ),
                vol.Required(
                    CONF_INDOOR_HUM,
                    default=_opt(CONF_INDOOR_HUM),
                ): selector.EntitySelector(
                    selector.EntitySelectorConfig(
                        domain="sensor",
                        device_class="humidity",
                    )
                ),
                vol.Required(
                    CONF_OUTDOOR_HUM,
                    default=_opt(CONF_OUTDOOR_HUM),
                ): selector.EntitySelector(
                    selector.EntitySelectorConfig(
                        domain="sensor",
                        device_class="humidity",
                    )
                ),
                vol.Required(
                    CONF_CONTACT,
                    default=_opt(CONF_CONTACT),
                ): selector.EntitySelector(
                    selector.EntitySelectorConfig(
                        domain="binary_sensor",
                        device_class="door",
                    )
                ),
                vol.Optional(
                    CONF_WIND_SPEED,
                    default=_opt(CONF_WIND_SPEED),
                ): selector.EntitySelector(
                    selector.EntitySelectorConfig(
                        domain="sensor",
                        device_class="wind_speed",
                    )
                ),
                vol.Required(
                    CONF_TARGET_TEMP,
                    default=_opt(CONF_TARGET_TEMP, DEFAULT_TARGET_TEMP),
                ): vol.All(vol.Coerce(float), vol.Range(min=10, max=30)),
                vol.Required(
                    CONF_TARGET_HUM,
                    default=_opt(CONF_TARGET_HUM, DEFAULT_TARGET_HUM),
                ): vol.All(vol.Coerce(float), vol.Range(min=20, max=80)),
                vol.Required(
                    CONF_TOL_TEMP,
                    default=_opt(CONF_TOL_TEMP, DEFAULT_TOL_TEMP),
                ): vol.All(vol.Coerce(float), vol.Range(min=0.5, max=10)),
                vol.Required(
                    CONF_TOL_HUM,
                    default=_opt(CONF_TOL_HUM, DEFAULT_TOL_HUM),
                ): vol.All(vol.Coerce(float), vol.Range(min=1, max=30)),
                vol.Optional(
                    CONF_STATE_OPEN,
                    default=_opt(CONF_STATE_OPEN, DEFAULT_STATE_OPEN),
                ): str,
                vol.Optional(
                    CONF_STATE_CLOSE,
                    default=_opt(CONF_STATE_CLOSE, DEFAULT_STATE_CLOSE),
                ): str,
                vol.Optional(
                    CONF_STATE_KEEP,
                    default=_opt(CONF_STATE_KEEP, DEFAULT_STATE_KEEP),
                ): str,
            }
        )

        return self.async_show_form(
            step_id="init",
            data_schema=schema,
        )
