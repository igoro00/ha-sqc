"""DataUpdateCoordinator for SQC."""
from __future__ import annotations

import asyncio
import aiohttp
import logging
import re
from datetime import timedelta
from typing import Any

from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from homeassistant.const import CONF_HOST, CONF_PIN

from .const import DOMAIN, DEFAULT_SCAN_INTERVAL

from types import MappingProxyType

from aiohttp.http_exceptions import BadHttpMessage



_LOGGER = logging.getLogger(__name__)


class SQCDataUpdateCoordinator(DataUpdateCoordinator):
    """Class to manage fetching data from the API."""

    def __init__(
        self,
        hass: HomeAssistant,
        config: MappingProxyType[str, Any],
    ) -> None:
        """Initialize."""
        self.host = config[CONF_HOST]
        self.pin = config[CONF_PIN]

        self.session = async_get_clientsession(hass)
        
        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
            update_interval=timedelta(seconds=DEFAULT_SCAN_INTERVAL),
        )
    
    async def _login(self) -> None:
        """Login to the SQC API with pin"""

        url = f"{self.host}"
        async with self.session.post(url, data={"pin": self.pin}, timeout=aiohttp.ClientTimeout(total=10)) as res:
            if res.status == 200:
                text = await res.text()
                if "PIN prawidłowy" in text:
                    _LOGGER.info("Login successful")
                    await asyncio.sleep(1)
                else:
                    text = await res.text()
                    raise UpdateFailed(f"Login failed: {text}")
        
    def _get_device_name(self) -> str:
        """Extract device name from HTML."""
        if self.data is not None:
            html = self.data.get("html")
            if html is not None:
                pattern = r"<title>(.+)</title>"
                match = re.search(pattern, html)
                if match:
                    return match.group(1)
        return "Unknown Device"
    
    def _get_device_info(self, entry_id) -> DeviceInfo:
        device_name = self._get_device_name()
        return { 
            "identifiers": {(DOMAIN, entry_id)},
            "name": device_name,
            "manufacturer": "SeaQuaComp",
            "model": device_name,
        }

    async def _async_update_data(self) -> dict[str, Any]:
        url = f"{self.host}/home"
        try:
            async with self.session.get(
                url, timeout=aiohttp.ClientTimeout(total=10)
            ) as resp:
                if resp.status != 200:
                    raise UpdateFailed(f"Bad status {resp.status}")

                data = await resp.text()
                if "<!DOCTYPE html>" not in data:
                    raise BadHttpMessage("Not logged in")

                return {
                    "html": data,
                    "online": True,
                    "last_updated": self.hass.loop.time(),
                }
        except BadHttpMessage as err:
            _LOGGER.warning("Not logged in, trying to login")
            await self._login()
            return await self._async_update_data()
        except aiohttp.ClientConnectorError as err:
            # host całkowicie niedostępny (np. odłączony od prądu)
            raise UpdateFailed(f"Host {self.host} not reachable: {err}") from err
        except asyncio.TimeoutError:
            raise UpdateFailed(f"Timeout while fetching from {self.host}")
        except aiohttp.ClientError as err:
            if "Expected HTTP/" in str(err):
                _LOGGER.warning("Not logged in, trying to login")
                await self._login()
                return await self._async_update_data()
            raise UpdateFailed(f"Comm error with {self.host}: {err}") from err