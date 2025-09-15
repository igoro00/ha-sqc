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

from homeassistant.const import CONF_HOST, CONF_PIN

from .const import DOMAIN, DEFAULT_SCAN_INTERVAL

from types import MappingProxyType


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
        
        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
            update_interval=timedelta(seconds=DEFAULT_SCAN_INTERVAL),
        )
    
    async def _login(self) -> bool:
        """Login to the SQC API with pin"""
        try:
            url = f"{self.host}"
            async with aiohttp.ClientSession() as session:
                async with session.post(url, data={"pin": self.pin}, timeout=aiohttp.ClientTimeout(total=10)) as res:
                    if res.status == 200:
                        text = await res.text()
                        if "PIN prawidłowy" in text:
                            _LOGGER.info("Login successful")
                            return True
                    else:
                        text = await res.text()
                        _LOGGER.error("Login failed: %s", text)
        except Exception as e:
            _LOGGER.error("Error logging in: %s", e)
        finally:
            return False
    
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
        """Update data via library."""
        try:
            async with asyncio.timeout(10):
                return await self._fetch_data()
        except Exception as exception:
            raise UpdateFailed(f"Error communicating with API: {exception}") from exception

    async def _fetch_data(self, iteration: int=0) -> dict[str, Any]:
        """Fetch data from the API."""
        url = f"{self.host}/home"
        try:
            if iteration > 5:
                _LOGGER.info("Retrying fetch data, attempt %d", iteration)
                raise UpdateFailed("Max retries reached")
            _LOGGER.debug("Fetching data from %s", url)
            async with aiohttp.ClientSession() as session:
                async with session.get(url, timeout=aiohttp.ClientTimeout(total=10)) as res:
                    if res.status == 200:
                        data = await res.text()
                        if "<!DOCTYPE html>" not in data:
                            _LOGGER.error("Not logged in, trying to login")
                            if not await self._login():
                                raise UpdateFailed("Login failed, cannot fetch data")
                            await asyncio.sleep(5)
                            return await self._fetch_data(iteration + 1)

                        return {
                            "html": data,
                            "online": True,
                            "last_updated": self.hass.loop.time(),
                        }
                    else:
                        _LOGGER.warning(
                            "API returned status %s for %s", res.status, url
                        )
                        return {
                            "html": "",
                            "online": False,
                            "last_updated": self.hass.loop.time(),
                        }
                    
        except Exception as err:
            _LOGGER.error("Error fetching data from %s: %s", self.host, err)
            return {
                "html": "",
                "online": False,
                "last_updated": self.hass.loop.time(),
                "error": str(err),
            }
