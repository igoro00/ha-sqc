"""Config flow for SQC integration."""
from __future__ import annotations

import logging
import re
from typing import Any

import voluptuous as vol
import asyncio

from homeassistant import config_entries
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import HomeAssistantError

from .const import DOMAIN

from homeassistant.const import CONF_HOST, CONF_PIN

_LOGGER = logging.getLogger(__name__)

STEP_USER_DATA_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_HOST): str,
        vol.Required(CONF_PIN): str,
    }
)


async def validate_input(hass: HomeAssistant, data: dict[str, Any]) -> dict[str, Any]:
    """Validate the user input allows us to connect.

    Data has the keys from STEP_USER_DATA_SCHEMA with values provided by the user.
    """
    host = data[CONF_HOST]
    pin = data[CONF_PIN]

    # Validate PIN format (4 digits)
    if not re.match(r'^\d{4}$', pin):
        raise InvalidPin

    # Try to connect to the host
    
    try:
        # Add protocol if not specified
        if not host.startswith(('http://', 'https://')):
            host = f"http://{host}"
        
        
    except (Exception, asyncio.TimeoutError) as err:
        _LOGGER.error("Error connecting to %s: %s", host, err)
        raise CannotConnect from err

    # Return info that you want to store in the config entry.
    return {"title": f"SQC ({host})", "host": host, "pin": pin}


class ConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for SQC."""

    VERSION = 1

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ):
        """Handle the initial step."""
        errors: dict[str, str] = {}
        
        if user_input is not None:
            try:
                info = await validate_input(self.hass, user_input)
            except CannotConnect:
                errors["base"] = "cannot_connect"
            except InvalidPin:
                errors["pin"] = "invalid_pin"
            except Exception:  # pylint: disable=broad-except
                _LOGGER.exception("Unexpected exception")
                errors["base"] = "unknown"
            else:
                # Create unique ID based on host
                await self.async_set_unique_id(user_input[CONF_HOST])
                self._abort_if_unique_id_configured()
                
                return self.async_create_entry(
                    title=info["title"], 
                    data={
                        CONF_HOST: info["host"],
                        CONF_PIN: info["pin"]
                    }
                )

        return self.async_show_form(
            step_id="user", data_schema=STEP_USER_DATA_SCHEMA, errors=errors
        )


class CannotConnect(HomeAssistantError):
    """Error to indicate we cannot connect."""


class InvalidPin(HomeAssistantError):
    """Error to indicate the PIN format is invalid."""
