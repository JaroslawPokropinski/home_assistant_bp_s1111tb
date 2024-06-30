from __future__ import annotations
import tinytuya
import logging

from homeassistant.components.climate import (
    ClimateEntity,
    HVACMode,
    ATTR_HVAC_MODE,
    ATTR_TEMPERATURE,
    ClimateEntityFeature
)
from homeassistant.const import UnitOfTemperature
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.typing import ConfigType, DiscoveryInfoType
import homeassistant

_LOGGER = logging.getLogger(__name__)

def setup_platform(
    hass: HomeAssistant,
    config: ConfigType,
    add_entities: AddEntitiesCallback,
    discovery_info: DiscoveryInfoType | None = None
) -> None:
    """Set up the sensor platform."""
    _LOGGER.warn(config)
    add_entities([AirConditionerEntity(config)])

class AirConditionerEntity(ClimateEntity):
    _attr_hvac_modes = [
        HVACMode.OFF,
        HVACMode.COOL
    ]
    _attr_temperature_unit = homeassistant.const.UnitOfTemperature.CELSIUS
    _attr_target_temperature_low = 18
    _attr_target_temperature_high = 32
    _attr_target_temperature_step = 1
        
    

    def __init__(self, config: ConfigType):
        _attr_name = config.get("name", "Air conditioner")
        self._attr_unique_id = config.get("device_id", "")
        self.device = tinytuya.OutletDevice(
            dev_id=config.get("device_id", ""),
            address=config.get("ip", ""),
            local_key=config.get("local_key", ""),
            version=3.3,
        )

        self._attr_hvac_mode = HVACMode.OFF
    

    def update(self) -> None:
        updated_status = self.device.status()
        if "Error" in updated_status:
            return
        # self._attr_state = HVACMode.COOL if updated_status["dps"]["1"] == True else HVACMode.OFF
        self._attr_hvac_mode = HVACMode.COOL if updated_status["dps"]["1"] == True else HVACMode.OFF
        self._attr_target_temperature = updated_status["dps"]["6"]

    @property
    def supported_features(self):
        return ClimateEntityFeature.TURN_ON | ClimateEntityFeature.TURN_OFF | ClimateEntityFeature.TARGET_TEMPERATURE

    def set_hvac_mode(self, hvac_mode) -> None:
        _LOGGER.warn(hvac_mode)
        self._attr_hvac_mode = hvac_mode
        if hvac_mode == HVACMode.OFF:
            self.device.turn_off()
        else:
            self.device.turn_on()

    def set_temperature(self, **kwargs: Any) -> None:
        _LOGGER.warn(kwargs)
        new_temp = kwargs.get(ATTR_TEMPERATURE, 32)
        self._attr_target_temperature = new_temp

        self.device.set_value("6", str(new_temp))


    def turn_on(self) -> None:
        self.device.turn_on()
        self._attr_hvac_mode = HVACMode.COOL

    def turn_off(self) -> None:
        self.device.turn_off()
        self._attr_hvac_mode = HVACMode.OFF
