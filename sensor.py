"""Support for Tibber sensors."""
from __future__ import annotations

import datetime
from datetime import timedelta
import logging
from random import randrange
from typing import Any, cast
from .tibber import RetryableHttpExceptionError,FatalHttpExceptionError

import aiohttp

from homeassistant.components.recorder import get_instance
from homeassistant.components.recorder.models import StatisticData, StatisticMetaData
from homeassistant.components.recorder.statistics import (
    async_add_external_statistics,
    get_last_statistics,
    statistics_during_period,
)
from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorEntityDescription,
    SensorStateClass,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import (
    EVENT_HOMEASSISTANT_STOP,
    PERCENTAGE,
    SIGNAL_STRENGTH_DECIBELS,
    EntityCategory,
    UnitOfElectricCurrent,
    UnitOfElectricPotential,
    UnitOfEnergy,
    UnitOfPower,
)
from homeassistant.core import Event, HomeAssistant, callback
from homeassistant.exceptions import PlatformNotReady
from homeassistant.helpers import device_registry as dr, entity_registry as er
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.entity_registry import async_get as async_get_entity_reg
from homeassistant.helpers.typing import StateType
from homeassistant.helpers.update_coordinator import (
    CoordinatorEntity,
    DataUpdateCoordinator,
    UpdateFailed,
)
from dataclasses import dataclass
from homeassistant.util import Throttle, dt as dt_util

from .const import DOMAIN as TIBBER_DOMAIN, MANUFACTURER
from . import tibber
from .coordinator import TibberDataCoordinator

_LOGGER = logging.getLogger(__name__)

ICON = "mdi:currency-usd"
SCAN_INTERVAL = timedelta(minutes=1)
MIN_TIME_BETWEEN_UPDATES = timedelta(minutes=5)
PARALLEL_UPDATES = 0


RT_SENSORS_UNIQUE_ID_MIGRATION = {
    "accumulated_consumption_last_hour": "accumulated consumption current hour",
    "accumulated_production_last_hour": "accumulated production current hour",
    "current_l1": "current L1",
    "current_l2": "current L2",
    "current_l3": "current L3",
    "estimated_hour_consumption": "Estimated consumption current hour",
}

RT_SENSORS_UNIQUE_ID_MIGRATION_SIMPLE = {
    # simple migration can be done by replacing " " with "_"
    "accumulated_consumption",
    "accumulated_cost",
    "accumulated_production",
    "accumulated_reward",
    "average_power",
    "last_meter_consumption",
    "last_meter_production",
    "max_power",
    "min_power",
    "power_factor",
    "power_production",
    "signal_strength",
    "voltage_phase1",
    "voltage_phase2",
    "voltage_phase3",
}

@dataclass(frozen=True, kw_only=True)
class TibberSensorEntityDescription (SensorEntityDescription):

    native_unit_of_measurement_key: str | None = None



RT_SENSORS: tuple[SensorEntityDescription, ...] = (
    SensorEntityDescription(
        key="averagePower",
        translation_key="average_power",
        device_class=SensorDeviceClass.POWER,
        native_unit_of_measurement=UnitOfPower.WATT,
        suggested_display_precision=0,
    ),
    SensorEntityDescription(
        key="power",
        translation_key="power",
        device_class=SensorDeviceClass.POWER,
        state_class=SensorStateClass.MEASUREMENT,
        native_unit_of_measurement=UnitOfPower.WATT,
        suggested_display_precision=0,
    ),
    SensorEntityDescription(
        key="powerProduction",
        translation_key="power_production",
        device_class=SensorDeviceClass.POWER,
        state_class=SensorStateClass.MEASUREMENT,
        native_unit_of_measurement=UnitOfPower.WATT,
        suggested_display_precision=0,
    ),
    SensorEntityDescription(
        key="minPower",
        translation_key="min_power",
        device_class=SensorDeviceClass.POWER,
        native_unit_of_measurement=UnitOfPower.WATT,
        suggested_display_precision=0,
    ),
    SensorEntityDescription(
        key="maxPower",
        translation_key="max_power",
        device_class=SensorDeviceClass.POWER,
        native_unit_of_measurement=UnitOfPower.WATT,
        suggested_display_precision=0,
    ),
    SensorEntityDescription(
        key="accumulatedConsumption",
        translation_key="accumulated_consumption",
        device_class=SensorDeviceClass.ENERGY,
        native_unit_of_measurement=UnitOfEnergy.KILO_WATT_HOUR,
        state_class=SensorStateClass.TOTAL,
        suggested_display_precision=4,
    ),
    SensorEntityDescription(
        key="accumulatedConsumptionLastHour",
        translation_key="accumulated_consumption_last_hour",
        device_class=SensorDeviceClass.ENERGY,
        native_unit_of_measurement=UnitOfEnergy.KILO_WATT_HOUR,
        state_class=SensorStateClass.TOTAL_INCREASING,
        suggested_display_precision=4,
    ),
    SensorEntityDescription(
        key="estimatedHourConsumption",
        translation_key="estimated_hour_consumption",
        device_class=SensorDeviceClass.ENERGY,
        native_unit_of_measurement=UnitOfEnergy.KILO_WATT_HOUR,
        suggested_display_precision=4,
    ),
    SensorEntityDescription(
        key="accumulatedProduction",
        translation_key="accumulated_production",
        device_class=SensorDeviceClass.ENERGY,
        native_unit_of_measurement=UnitOfEnergy.KILO_WATT_HOUR,
        state_class=SensorStateClass.TOTAL,
        suggested_display_precision=4,
    ),
    SensorEntityDescription(
        key="accumulatedProductionLastHour",
        translation_key="accumulated_production_last_hour",
        device_class=SensorDeviceClass.ENERGY,
        native_unit_of_measurement=UnitOfEnergy.KILO_WATT_HOUR,
        state_class=SensorStateClass.TOTAL_INCREASING,
        suggested_display_precision=4,
    ),
    SensorEntityDescription(
        key="lastMeterConsumption",
        translation_key="last_meter_consumption",
        device_class=SensorDeviceClass.ENERGY,
        native_unit_of_measurement=UnitOfEnergy.KILO_WATT_HOUR,
        state_class=SensorStateClass.TOTAL_INCREASING,
        suggested_display_precision=4,
    ),
    SensorEntityDescription(
        key="lastMeterProduction",
        translation_key="last_meter_production",
        device_class=SensorDeviceClass.ENERGY,
        native_unit_of_measurement=UnitOfEnergy.KILO_WATT_HOUR,
        state_class=SensorStateClass.TOTAL_INCREASING,
        suggested_display_precision=4,
    ),
    SensorEntityDescription(
        key="voltagePhase1",
        translation_key="voltage_phase1",
        device_class=SensorDeviceClass.VOLTAGE,
        native_unit_of_measurement=UnitOfElectricPotential.VOLT,
        state_class=SensorStateClass.MEASUREMENT,
        suggested_display_precision=1,
    ),
    SensorEntityDescription(
        key="voltagePhase2",
        translation_key="voltage_phase2",
        device_class=SensorDeviceClass.VOLTAGE,
        native_unit_of_measurement=UnitOfElectricPotential.VOLT,
        state_class=SensorStateClass.MEASUREMENT,
        suggested_display_precision=1,
    ),
    SensorEntityDescription(
        key="voltagePhase3",
        translation_key="voltage_phase3",
        device_class=SensorDeviceClass.VOLTAGE,
        native_unit_of_measurement=UnitOfElectricPotential.VOLT,
        state_class=SensorStateClass.MEASUREMENT,
        suggested_display_precision=1,
    ),
    SensorEntityDescription(
        key="currentL1",
        translation_key="current_l1",
        device_class=SensorDeviceClass.CURRENT,
        native_unit_of_measurement=UnitOfElectricCurrent.AMPERE,
        state_class=SensorStateClass.MEASUREMENT,
        suggested_display_precision=2,
    ),
    SensorEntityDescription(
        key="currentL2",
        translation_key="current_l2",
        device_class=SensorDeviceClass.CURRENT,
        native_unit_of_measurement=UnitOfElectricCurrent.AMPERE,
        state_class=SensorStateClass.MEASUREMENT,
        suggested_display_precision=2,
    ),
    SensorEntityDescription(
        key="currentL3",
        translation_key="current_l3",
        device_class=SensorDeviceClass.CURRENT,
        native_unit_of_measurement=UnitOfElectricCurrent.AMPERE,
        state_class=SensorStateClass.MEASUREMENT,
        suggested_display_precision=2,
    ),
    SensorEntityDescription(
        key="signalStrength",
        translation_key="signal_strength",
        device_class=SensorDeviceClass.SIGNAL_STRENGTH,
        native_unit_of_measurement=SIGNAL_STRENGTH_DECIBELS,
        state_class=SensorStateClass.MEASUREMENT,
        entity_category=EntityCategory.DIAGNOSTIC,
        suggested_display_precision=0,
    ),
    SensorEntityDescription(
        key="accumulatedReward",
        translation_key="accumulated_reward",
        device_class=SensorDeviceClass.MONETARY,
        state_class=SensorStateClass.TOTAL,
        suggested_display_precision=4,
    ),
    SensorEntityDescription(
        key="accumulatedCost",
        translation_key="accumulated_cost",
        device_class=SensorDeviceClass.MONETARY,
        state_class=SensorStateClass.TOTAL,
        suggested_display_precision=4,
    ),
    SensorEntityDescription(
        key="powerFactor",
        translation_key="power_factor",
        device_class=SensorDeviceClass.POWER_FACTOR,
        native_unit_of_measurement=PERCENTAGE,
        state_class=SensorStateClass.MEASUREMENT,
        suggested_display_precision=2,
    ),
)

SENSORS: tuple[SensorEntityDescription, ...] = (
    SensorEntityDescription(
        key="hour_cheapest_top",
        translation_key="hour_cheapest_top",
    ),
    SensorEntityDescription(
        key="hour_cheapest_top_after_0000",
        translation_key="hour_cheapest_top_after_0000",
    ),
    SensorEntityDescription(
        key="hour_cheapest_top_after_0800",
        translation_key="hour_cheapest_top_after_0800",
    ),

    SensorEntityDescription(
        key="hour_cheapest_top_after_1800",
        translation_key="hour_cheapest_top_after_1800",
    ),


    


    TibberSensorEntityDescription(
        key="month_cost",
        translation_key="month_cost",
        device_class=SensorDeviceClass.MONETARY,
        native_unit_of_measurement_key = "currency",
        suggested_display_precision=4,
    ),
    SensorEntityDescription(
        key="peak_hour",
        translation_key="peak_hour",
        device_class=SensorDeviceClass.ENERGY,
        native_unit_of_measurement=UnitOfEnergy.KILO_WATT_HOUR,
        suggested_display_precision=4,
    ),
    SensorEntityDescription(
        key="peak_hour_time",
        translation_key="peak_hour_time",
        device_class=SensorDeviceClass.TIMESTAMP,
    ),
    SensorEntityDescription(
        key="month_cons",
        translation_key="month_cons",
        device_class=SensorDeviceClass.ENERGY,
        native_unit_of_measurement=UnitOfEnergy.KILO_WATT_HOUR,
        state_class=SensorStateClass.TOTAL_INCREASING,
        suggested_display_precision=4,
    ),
    
    TibberSensorEntityDescription(
        key="electricity_price",

        translation_key="electricity_price",
        device_class=SensorDeviceClass.MONETARY,

        native_unit_of_measurement_key = "price_unit",
        icon= ICON,
        suggested_display_precision=4,
    ),
    TibberSensorEntityDescription(
        key="electricity_price_excl",
        translation_key="electricity_price_excl",
        device_class=SensorDeviceClass.MONETARY,
        native_unit_of_measurement_key = "price_unit",
        icon= ICON,
        entity_category=EntityCategory.DIAGNOSTIC,
        entity_registry_enabled_default=False,
        suggested_display_precision=4,
    ),

    TibberSensorEntityDescription(
        key="electricity_price_excl_base",
        translation_key="electricity_price_excl_base",
        device_class=SensorDeviceClass.MONETARY,
        native_unit_of_measurement_key = "price_unit",
        icon= ICON,
        entity_category=EntityCategory.DIAGNOSTIC,
        entity_registry_enabled_default=False,
        suggested_display_precision=4,
    ),

    TibberSensorEntityDescription(
        key="electricity_price_energy_tax_excl",
        translation_key="electricity_price_energy_tax_excl",
        device_class=SensorDeviceClass.MONETARY,
        native_unit_of_measurement_key = "price_unit",
        icon= ICON,
        entity_category=EntityCategory.DIAGNOSTIC,
        entity_registry_enabled_default=False,
        suggested_display_precision=4,
    ),

    TibberSensorEntityDescription(
        key="electricity_price_energy_tax_incl",
        translation_key="electricity_price_energy_tax_incl",
        device_class=SensorDeviceClass.MONETARY,
        native_unit_of_measurement_key = "price_unit",
        icon= ICON,
        entity_category=EntityCategory.DIAGNOSTIC,
        entity_registry_enabled_default=False,
        suggested_display_precision=4,
    ),
    
    TibberSensorEntityDescription(
        key="electricity_price_purchasing_compensation_excl",
        translation_key="electricity_price_purchasing_compensation_excl",
        device_class=SensorDeviceClass.MONETARY,

        native_unit_of_measurement_key = "price_unit",
        icon= ICON,
        entity_category=EntityCategory.DIAGNOSTIC,
        entity_registry_enabled_default=False,
        suggested_display_precision=4,
    ),

    TibberSensorEntityDescription(
        key="electricity_price_purchasing_compensation_incl",
        translation_key="electricity_price_purchasing_compensation_incl",
        device_class=SensorDeviceClass.MONETARY,
        native_unit_of_measurement_key = "price_unit",
        icon= ICON,
        entity_category=EntityCategory.DIAGNOSTIC,
        entity_registry_enabled_default=False,
        suggested_display_precision=4,
    ),


    TibberSensorEntityDescription(
        key="electricity_price_calc",
        translation_key="electricity_price_calc",
        device_class=SensorDeviceClass.MONETARY,
        native_unit_of_measurement_key = "price_unit",
        icon= ICON,
        entity_category=EntityCategory.DIAGNOSTIC,
        entity_registry_enabled_default=False,
        suggested_display_precision=4,
    ),


    SensorEntityDescription(
        key="tax_rate",
        translation_key="tax_rate",
        icon= ICON,
        entity_category=EntityCategory.DIAGNOSTIC,
        entity_registry_enabled_default=False
    ),
    
    
    SensorEntityDescription(
        key="electricity_price_excl_cent",
        translation_key="electricity_price_excl_cent",
        device_class=SensorDeviceClass.MONETARY,
        icon= ICON,
        entity_category=EntityCategory.DIAGNOSTIC,
        entity_registry_enabled_default=False
    ),
    SensorEntityDescription(
        key="last_price_update",
        translation_key="last_price_update",
        device_class=SensorDeviceClass.TIMESTAMP,
    ),
    
    # Today price sensors
    TibberSensorEntityDescription(
        key="electricity_price_today_min",
        translation_key="electricity_price_today_min",
        device_class=SensorDeviceClass.MONETARY,
        native_unit_of_measurement_key="price_unit",
        icon=ICON,
        suggested_display_precision=4,
    ),
    TibberSensorEntityDescription(
        key="electricity_price_today_max",
        translation_key="electricity_price_today_max",
        device_class=SensorDeviceClass.MONETARY,
        native_unit_of_measurement_key="price_unit",
        icon=ICON,
        suggested_display_precision=4,
    ),
    TibberSensorEntityDescription(
        key="electricity_price_today_avg",
        translation_key="electricity_price_today_avg",
        device_class=SensorDeviceClass.MONETARY,
        native_unit_of_measurement_key="price_unit",
        icon=ICON,
        suggested_display_precision=4,
    ),
    
    # Tomorrow price sensors
    TibberSensorEntityDescription(
        key="electricity_price_tomorrow_min",
        translation_key="electricity_price_tomorrow_min",
        device_class=SensorDeviceClass.MONETARY,
        native_unit_of_measurement_key="price_unit",
        icon=ICON,
        suggested_display_precision=4,
    ),
    TibberSensorEntityDescription(
        key="electricity_price_tomorrow_max",
        translation_key="electricity_price_tomorrow_max",
        device_class=SensorDeviceClass.MONETARY,
        native_unit_of_measurement_key="price_unit",
        icon=ICON,
        suggested_display_precision=4,
    ),
    TibberSensorEntityDescription(
        key="electricity_price_tomorrow_avg",
        translation_key="electricity_price_tomorrow_avg",
        device_class=SensorDeviceClass.MONETARY,
        native_unit_of_measurement_key="price_unit",
        icon=ICON,
        suggested_display_precision=4,
    ),

)


async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback
) -> None:
    """Set up the Tibber sensor."""

    tibber_connection = hass.data[TIBBER_DOMAIN]

    entity_registry = er.async_get(hass)
    device_registry = dr.async_get(hass)

    coordinator: TibberDataCoordinator | None = None
    entities: list[TibberSensor] = []
    for home in tibber_connection.get_homes(only_active=False):
        try:
            await home.update_info()
        except TimeoutError as err:
            _LOGGER.error("Timeout connecting to Tibber home: %s ", err)
            raise PlatformNotReady() from err
        except aiohttp.ClientError as err:
            _LOGGER.error("Error connecting to Tibber home: %s ", err)
            raise PlatformNotReady() from err

        if home.has_active_subscription:


            if coordinator is None:
                coordinator = TibberDataCoordinator(hass, tibber_connection)
            for entity_description in SENSORS:
                entities.append(TibberDataSensor(home, coordinator, entity_description))

        if home.has_real_time_consumption:
            await home.rt_subscribe(
                TibberRtDataCoordinator(
                    async_add_entities, home, hass
                ).async_set_updated_data
            )

        # migrate
        old_id = home.info["viewer"]["home"]["meteringPointData"]["consumptionEan"]
        if old_id is None:
            continue

        # migrate to new device ids
        old_entity_id = entity_registry.async_get_entity_id(
            "sensor", TIBBER_DOMAIN, old_id
        )
        if old_entity_id is not None:
            entity_registry.async_update_entity(
                old_entity_id, new_unique_id=home.home_id
            )

        # migrate to new device ids
        device_entry = device_registry.async_get_device(
            identifiers={(TIBBER_DOMAIN, old_id)}
        )
        if device_entry and entry.entry_id in device_entry.config_entries:
            device_registry.async_update_device(
                device_entry.id, new_identifiers={(TIBBER_DOMAIN, home.home_id)}
            )

    async_add_entities(entities, True)


class TibberSensor(SensorEntity):
    """Representation of a generic Tibber sensor."""

    _attr_has_entity_name = True


    def __init__(
        self, *args: Any, tibber_home: tibber.TibberHome, **kwargs: Any
    ) -> None:
        """Initialize the sensor."""
        super().__init__(*args, **kwargs)
        self._tibber_home = tibber_home
        self._home_name = tibber_home.info["viewer"]["home"]["appNickname"]
        if self._home_name is None:
            self._home_name = tibber_home.info["viewer"]["home"]["address"].get(
                "address1", ""
            )
        self._device_name: None | str = None
        self._model: None | str = None

    @property
    def device_info(self) -> DeviceInfo:
        """Return the device_info of the device."""
        device_info = DeviceInfo(
            identifiers={(TIBBER_DOMAIN, self._tibber_home.home_id)},
            name=self._device_name,
            manufacturer=MANUFACTURER,
        )
        if self._model is not None:
            device_info["model"] = self._model
        return device_info



class TibberSensorElPrice(TibberSensor):
    """Representation of a Tibber sensor for el price."""

    _attr_state_class = SensorStateClass.MEASUREMENT
    _attr_translation_key = "electricity_price"

    def __init__(self, tibber_home: tibber.TibberHome) -> None:
        """Initialize the sensor."""
        super().__init__(tibber_home=tibber_home)
        self._last_updated: datetime.datetime | None = None
        self._spread_load_constant = randrange(5000)

        self._attr_available = False
        self._attr_extra_state_attributes = {
            "app_nickname": None,
            "grid_company": None,
            "estimated_annual_consumption": None,
            "price_level": None,
            "max_price": None,
            "avg_price": None,
            "min_price": None,
            "off_peak_1": None,
            "peak": None,
            "off_peak_2": None,
        }
        self._attr_icon = ICON
        self._attr_unique_id = self._tibber_home.home_id
        self._model = "Price Sensor"

        self._device_name = self._home_name



class TibberDataSensor(TibberSensor, CoordinatorEntity["TibberDataCoordinator"]):
    """Representation of a Tibber sensor."""

    def __init__(
        self,
        tibber_home: tibber.TibberHome,
        coordinator: TibberDataCoordinator,
        entity_description: TibberSensorEntityDescription
    ) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator=coordinator, tibber_home=tibber_home)
        self.entity_description = entity_description

        self._attr_unique_id = (
            f"{self._tibber_home.home_id}_{self.entity_description.key}"
        )

        if entity_description is TibberSensorEntityDescription:
            if entity_description.native_unit_of_measurement_key:
                self._attr_native_unit_of_measurement = getattr(self._tibber_home, entity_description.native_unit_of_measurement_key) 

        elif entity_description.key == "electricity_price_excl":
            self._attr_native_unit_of_measurement = self._tibber_home.price_unit
        
        elif entity_description.key == "electricity_price_excl_cent":
            self._attr_native_unit_of_measurement = self._tibber_home.price_unit

        elif entity_description.key == "electricity_price":
            self._attr_available = False
            
            self._attr_native_unit_of_measurement = self._tibber_home.price_unit
            self._attr_extra_state_attributes = {
                "app_nickname": None,
                "grid_company": None,
                "estimated_annual_consumption": None,
                "price_level": None,
                "max_price": None,
                "avg_price": None,
                "min_price": None,
                "off_peak_1": None,
                "peak": None,
                "off_peak_2": None,
            }



        self._device_name = self._home_name

    @property
    def native_value(self) -> StateType:
        """Return the value of the sensor."""
        key = self.entity_description.key
        value = getattr(self._tibber_home, key)  # type: ignore[no-any-return]

        return value

    @callback
    def _handle_coordinator_update(self) -> None:
        """Handle updated data from the coordinator."""
        
        if self.entity_description.key == "electricity_price":
            _LOGGER.debug('Update electricity_price atributes')

            # Build a compact summary of price info to avoid storing huge attributes
            # Full `price_info` can be very large (quarter-hour entries) which causes
            # recorder to skip attribute storage and DB warnings. Provide a small
            # summary: source, current price and the next few upcoming entries.
            summary: dict[str, Any] = {}
            summary["source"] = getattr(self._tibber_home, "price_source", "unknown")

            # include currency at top level if available (stable for recorder)
            currency = getattr(self._tibber_home, "currency", None) or None
            summary["currency"] = currency

            # Build 'current' entry: prefer quarter-hour entry from _price_info,
            # fallback to _current_price_info which may come from the separate query.
            current: dict[str, Any] | None = None
            try:
                now = dt_util.now().astimezone(self._tibber_home._tibber_control.time_zone)
                # look for matching quarter-hour entry
                for startsAt, entry in (getattr(self._tibber_home, "_price_info", {}) or {}).items():
                    ts = entry.get("timestamp")
                    if not isinstance(ts, datetime.datetime):
                        continue
                    if ts <= now < (ts + datetime.timedelta(minutes=15)):
                        # found matching quarter-hour entry
                        current = {
                            "startsAt": startsAt,
                            "total": entry.get("total"),  # The total price (energy + taxes)
                            "energy": entry.get("energy"),  # Nord Pool spot price
                            # The tax part of the price (guarantee of origin certificate, 
                            # energy tax (Sweden only) and VAT). For NL: includes VAT on spot + fixed costs.
                            "tax": entry.get("tax"),
                            "level": self._tibber_home.price_level.get(startsAt),
                        }
                        break

                # fallback to _current_price_info
                if current is None:
                    cur = getattr(self._tibber_home, "_current_price_info", None)
                    if cur and isinstance(cur, dict):
                        starts = cur.get("startsAt")
                        level = None
                        if isinstance(starts, str):
                            level = self._tibber_home.price_level.get(starts)
                        current = {
                            "startsAt": starts,
                            "total": cur.get("total"),  # The total price (energy + taxes)
                            "energy": cur.get("energy"),  # Nord Pool spot price
                            # The tax part (guarantee of origin, energy tax (Sweden only), VAT)
                            "tax": cur.get("tax"),
                            "level": cur.get("level") or level,
                        }
            except Exception:
                current = None
            summary["current"] = current

            # collect next up to 6 upcoming quarter entries from _price_info
            upcoming: list[dict[str, Any]] = []
            try:
                now = dt_util.now().astimezone(self._tibber_home._tibber_control.time_zone)
                entries: list[tuple[datetime.datetime, str]] = []
                for startsAt, entry in (getattr(self._tibber_home, "_price_info", {}) or {}).items():
                    ts = entry.get("timestamp")
                    if not isinstance(ts, datetime.datetime):
                        continue
                    if ts >= now:
                        entries.append((ts, startsAt))
                entries.sort()
                for ts, startsAt in entries[:6]:
                    entry = self._tibber_home._price_info.get(startsAt, {})
                    upcoming.append(
                        {
                            "startsAt": startsAt,
                            "total": entry.get("total"),  # The total price (energy + taxes)
                            "energy": entry.get("energy"),  # Nord Pool spot price
                            # The tax part (guarantee of origin, energy tax (Sweden only), VAT)
                            "tax": entry.get("tax"),
                            "level": self._tibber_home.price_level.get(startsAt),
                        }
                    )
            except Exception:
                upcoming = []

            summary["upcoming"] = upcoming

            # Collect full today, tomorrow, next_24h and next_48h data for graphs
            today_all: list[dict[str, Any]] = []
            tomorrow_all: list[dict[str, Any]] = []
            next_24h: list[dict[str, Any]] = []
            next_48h: list[dict[str, Any]] = []
            
            try:
                now = dt_util.now().astimezone(self._tibber_home._tibber_control.time_zone)
                today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
                tomorrow_start = today_start + datetime.timedelta(days=1)
                tomorrow_end = tomorrow_start + datetime.timedelta(days=1)
                next_24h_end = now + datetime.timedelta(hours=24)
                next_48h_end = now + datetime.timedelta(hours=48)
                
                # Sort all price entries by timestamp
                all_entries: list[tuple[datetime.datetime, str]] = []
                for startsAt, entry in (getattr(self._tibber_home, "_price_info", {}) or {}).items():
                    ts = entry.get("timestamp")
                    if not isinstance(ts, datetime.datetime):
                        continue
                    all_entries.append((ts, startsAt))
                all_entries.sort()
                
                # Collect prices and calculate stats
                today_prices: list[float] = []
                tomorrow_prices: list[float] = []
                
                for ts, startsAt in all_entries:
                    entry = self._tibber_home._price_info.get(startsAt, {})
                    price_data = {
                        "startsAt": startsAt,
                        "total": entry.get("total"),
                        "energy": entry.get("energy"),
                        "tax": entry.get("tax"),
                        "level": self._tibber_home.price_level.get(startsAt),
                    }
                    
                    # Today entries
                    if today_start <= ts < tomorrow_start:
                        today_all.append(price_data)
                        if entry.get("total") is not None:
                            today_prices.append(entry.get("total"))
                    
                    # Tomorrow entries
                    elif tomorrow_start <= ts < tomorrow_end:
                        tomorrow_all.append(price_data)
                        if entry.get("total") is not None:
                            tomorrow_prices.append(entry.get("total"))
                    
                    # Next 24h (rolling window from now)
                    if now <= ts < next_24h_end:
                        next_24h.append(price_data)
                    
                    # Next 48h (rolling window from now)
                    if now <= ts < next_48h_end:
                        next_48h.append(price_data)
                
                # Add statistics
                stats: dict[str, Any] = {}
                if today_prices:
                    stats["today_min"] = round(min(today_prices), 5)
                    stats["today_max"] = round(max(today_prices), 5)
                    stats["today_avg"] = round(sum(today_prices) / len(today_prices), 5)
                
                if tomorrow_prices:
                    stats["tomorrow_min"] = round(min(tomorrow_prices), 5)
                    stats["tomorrow_max"] = round(max(tomorrow_prices), 5)
                    stats["tomorrow_avg"] = round(sum(tomorrow_prices) / len(tomorrow_prices), 5)
                    stats["tomorrow_available"] = True
                else:
                    stats["tomorrow_available"] = False
                
                summary["stats"] = stats
                
            except Exception as e:
                _LOGGER.debug("Error building extended price data: %s", e)
                today_all = []
                tomorrow_all = []
                next_24h = []
                next_48h = []
                summary["stats"] = {}
            
            summary["today_all"] = today_all
            summary["tomorrow_all"] = tomorrow_all
            summary["next_24h"] = next_24h
            summary["next_48h"] = next_48h

            # attach compact summary (not the full price_info dict)
            # merge into existing attributes dict (avoid item assignment typing issues)
            self._attr_extra_state_attributes = {
                **(self._attr_extra_state_attributes or {}),
                "price_info_summary": summary,
            }
        
        self.async_write_ha_state()

class TibberSensorRT(TibberSensor, CoordinatorEntity["TibberRtDataCoordinator"]):
    """Representation of a Tibber sensor for real time consumption."""

    def __init__(
        self,
        tibber_home: tibber.TibberHome,
        description: SensorEntityDescription,
        initial_state: float,
        coordinator: TibberRtDataCoordinator,
    ) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator=coordinator, tibber_home=tibber_home)
        self.entity_description = description
        self._model = "Tibber Pulse"
        self._device_name = f"{self._model} {self._home_name}"

        self._attr_native_value = initial_state
        self._attr_unique_id = f"{self._tibber_home.home_id}_rt_{description.key}"

        if description.key in ("accumulatedCost", "accumulatedReward"):
            # RT sensor: prefer currency from live measurement data first,
            # then try getting it from home info, finally fall back to 'EUR'.
            # This ensures a stable unit for recorder/statistics.
            if live_measurement := coordinator.get_live_measurement():
                currency = live_measurement.get("currency")
                if currency:
                    self._attr_native_unit_of_measurement = currency
                    _LOGGER.debug(
                        "RT sensor %s using currency from live measurement: %s",
                        description.key,
                        currency,
                    )
                    return

            # Try getting from home info (may be None)
            currency = tibber_home.currency
            if currency:
                self._attr_native_unit_of_measurement = currency
                _LOGGER.debug(
                    "RT sensor %s using currency from home info: %s",
                    description.key,
                    currency,
                )
                return

            # Fallback to EUR to keep unit stable for recorder
            self._attr_native_unit_of_measurement = "EUR"
            _LOGGER.debug(
                "RT sensor %s using fallback currency: EUR",
                description.key,
            )
            # when Tibber does not provide a currency to avoid unit=None which
            # suppresses long term statistics.
            self._attr_native_unit_of_measurement = tibber_home.currency or "EUR"

    @property
    def available(self) -> bool:
        """Return True if entity is available."""
        return self._tibber_home.rt_subscription_running

    @callback
    def _handle_coordinator_update(self) -> None:
        if not (live_measurement := self.coordinator.get_live_measurement()):
            return
        state = live_measurement.get(self.entity_description.key)
        if state is None:
            return
        if self.entity_description.key in (
            "accumulatedConsumption",
            "accumulatedProduction",
        ):
            # Value is reset to 0 at midnight, but not always strictly increasing
            # due to hourly corrections.
            # If device is offline, last_reset should be updated when it comes
            # back online if the value has decreased
            ts_local = dt_util.parse_datetime(live_measurement["timestamp"])
            if ts_local is not None:
                if self.last_reset is None or (
                    # native_value is float
                    state < 0.5 * self.native_value  # type: ignore[operator]
                    and (
                        ts_local.hour == 0
                        or (ts_local - self.last_reset) > timedelta(hours=24)
                    )
                ):
                    self._attr_last_reset = dt_util.as_utc(
                        ts_local.replace(hour=0, minute=0, second=0, microsecond=0)
                    )
        if self.entity_description.key == "powerFactor":
            state *= 100.0
        self._attr_native_value = state
        self.async_write_ha_state()


class TibberRtDataCoordinator(DataUpdateCoordinator):  # pylint: disable=hass-enforce-coordinator-module
    """Handle Tibber realtime data."""

    def __init__(
        self,
        async_add_entities: AddEntitiesCallback,
        tibber_home: tibber.TibberHome,
        hass: HomeAssistant,
    ) -> None:
        """Initialize the data handler."""
        self._async_add_entities = async_add_entities
        self._tibber_home = tibber_home
        self.hass = hass
        self._added_sensors: set[str] = set()
        super().__init__(
            hass,
            _LOGGER,
            name=tibber_home.info["viewer"]["home"]["address"].get(
                "address1", "Tibber"
            ),
        )

        self._async_remove_device_updates_handler = self.async_add_listener(
            self._add_sensors
        )
        self.entity_registry = er.async_get(hass)
        hass.bus.async_listen_once(EVENT_HOMEASSISTANT_STOP, self._handle_ha_stop)

    @callback
    def _handle_ha_stop(self, _event: Event) -> None:
        """Handle Home Assistant stopping."""
        self._async_remove_device_updates_handler()

    @callback
    def _migrate_unique_id(self, sensor_description: SensorEntityDescription) -> None:
        """Migrate unique id if needed."""
        home_id = self._tibber_home.home_id
        translation_key = sensor_description.translation_key
        description_key = sensor_description.key
        entity_id: str | None = None
        if translation_key in RT_SENSORS_UNIQUE_ID_MIGRATION_SIMPLE:
            entity_id = self.entity_registry.async_get_entity_id(
                "sensor",
                TIBBER_DOMAIN,
                f"{home_id}_rt_{translation_key.replace('_', ' ')}",
            )
        elif translation_key in RT_SENSORS_UNIQUE_ID_MIGRATION:
            entity_id = self.entity_registry.async_get_entity_id(
                "sensor",
                TIBBER_DOMAIN,
                f"{home_id}_rt_{RT_SENSORS_UNIQUE_ID_MIGRATION[translation_key]}",
            )
        elif translation_key != description_key:
            entity_id = self.entity_registry.async_get_entity_id(
                "sensor",
                TIBBER_DOMAIN,
                f"{home_id}_rt_{translation_key}",
            )

        if entity_id is None:
            return

        new_unique_id = f"{home_id}_rt_{description_key}"

        _LOGGER.debug(
            "Migrating unique id for %s to %s",
            entity_id,
            new_unique_id,
        )
        try:
            self.entity_registry.async_update_entity(
                entity_id, new_unique_id=new_unique_id
            )
        except ValueError as err:
            _LOGGER.error(err)

    @callback
    def _add_sensors(self) -> None:
        """Add sensor."""
        if not (live_measurement := self.get_live_measurement()):
            return

        new_entities = []
        for sensor_description in RT_SENSORS:
            if sensor_description.key in self._added_sensors:
                continue
            state = live_measurement.get(sensor_description.key)
            if state is None:
                continue

            self._migrate_unique_id(sensor_description)
            entity = TibberSensorRT(
                self._tibber_home,
                sensor_description,
                state,
                self,
            )
            new_entities.append(entity)
            self._added_sensors.add(sensor_description.key)
        if new_entities:
            self._async_add_entities(new_entities)

    def get_live_measurement(self) -> Any:
        """Get live measurement data."""
        if errors := self.data.get("errors"):
            _LOGGER.error(errors[0])
            return None
        return self.data.get("data", {}).get("liveMeasurement")
