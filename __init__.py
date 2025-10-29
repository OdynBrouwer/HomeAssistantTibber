"""Support for Tibber."""
import logging

import aiohttp
from .tibber import Tibber
from .tibber.exceptions import InvalidLoginError, RetryableHttpExceptionError, FatalHttpExceptionError

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import (
    CONF_ACCESS_TOKEN,
    CONF_NAME,
    EVENT_HOMEASSISTANT_STOP,
    Platform,
)
from homeassistant.core import Event, HomeAssistant
from homeassistant.exceptions import ConfigEntryNotReady
from homeassistant.helpers import discovery
from homeassistant.helpers.aiohttp_client import async_get_clientsession
import homeassistant.helpers.config_validation as cv
from homeassistant.helpers.typing import ConfigType
from homeassistant.util import dt as dt_util

from .const import (
    DATA_HASS_CONFIG,
    DOMAIN,
    CONF_SURCHARGE_PRICE_INCL,
    CONF_TAX_RATE,
    CONF_TAX_PER_KWH,
    DEFAULT_SURCHARGE_PRICE_INCL,
    DEFAULT_TAX_RATE,
    DEFAULT_TAX_PER_KWH,
)

PLATFORMS = [Platform.SENSOR]

CONFIG_SCHEMA = cv.removed(DOMAIN, raise_if_present=False)

_LOGGER = logging.getLogger(__name__)


async def async_setup(hass: HomeAssistant, config: ConfigType) -> bool:
    """Set up the Tibber component."""
    hass.data[DATA_HASS_CONFIG] = config
    return True


def create_tibber_connection(hass: HomeAssistant, entry: ConfigEntry) -> Tibber:
    """Create a new Tibber connection with the current config."""
    return Tibber(
        access_token=entry.data[CONF_ACCESS_TOKEN],
        websession=async_get_clientsession(hass),
        time_zone=dt_util.DEFAULT_TIME_ZONE,
        tax_rate=entry.options.get(CONF_TAX_RATE, DEFAULT_TAX_RATE),
        surcharge_price_incl=entry.options.get(CONF_SURCHARGE_PRICE_INCL, DEFAULT_SURCHARGE_PRICE_INCL),
        tax_per_kwh=entry.options.get(CONF_TAX_PER_KWH, DEFAULT_TAX_PER_KWH),
    )


async def async_update_options(hass: HomeAssistant, entry: ConfigEntry) -> None:
    """Handle options update."""
    # Create new connection with updated options
    tibber_connection = create_tibber_connection(hass, entry)
    
    # Update the connection in hass.data
    old_connection = hass.data[DOMAIN]
    await old_connection.rt_disconnect()  # Clean up old connection
    hass.data[DOMAIN] = tibber_connection
    
    # Reload integration to apply changes
    await hass.config_entries.async_reload(entry.entry_id)


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up a config entry."""
    # Initialize the Tibber connection with current config
    tibber_connection = create_tibber_connection(hass, entry)
    hass.data[DOMAIN] = tibber_connection
    # Reduce overly verbose logging from gql websocket transport which can
    # otherwise flood logs with debug/info messages. Keep at WARNING level.
    try:
        import logging as _logging

        _logging.getLogger("gql.transport.websockets").setLevel(_logging.WARNING)
    except Exception:
        # Best-effort: don't fail setup if setting logger level fails
        pass

    # Set up listener for option updates
    entry.async_on_unload(entry.add_update_listener(async_update_options))

    async def _close(event: Event) -> None:
        await tibber_connection.rt_disconnect()

    entry.async_on_unload(hass.bus.async_listen_once(EVENT_HOMEASSISTANT_STOP, _close))

    try:
        await tibber_connection.update_info()
    except (TimeoutError, aiohttp.ClientError, RetryableHttpExceptionError) as err:
        raise ConfigEntryNotReady("Unable to connect") from err
    except InvalidLoginError as exp:
        _LOGGER.error("Failed to login. %s", exp)
        return False
    except FatalHttpExceptionError:
        return False

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    # Set up notify platform
    hass.async_create_task(
        discovery.async_load_platform(
            hass,
            Platform.NOTIFY,
            DOMAIN,
            {CONF_NAME: DOMAIN},
            hass.data[DATA_HASS_CONFIG],
        )
    )
    return True


async def async_unload_entry(hass: HomeAssistant, config_entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    unload_ok = await hass.config_entries.async_unload_platforms(config_entry, PLATFORMS)
    if unload_ok:
        tibber_connection = hass.data[DOMAIN]
        await tibber_connection.rt_disconnect()
    return unload_ok
