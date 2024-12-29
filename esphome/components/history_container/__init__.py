from __future__ import annotations

import esphome.codegen as cg
from esphome.components import sensor
import esphome.config_validation as cv
from esphome.const import CONF_ID, CONF_LENGTH, CONF_NAME, CONF_SENSOR
from esphome.core import coroutine_with_priority

MULTI_CONF = True
DEPENDENCIES = ["sensor"]

history_container_ns = cg.esphome_ns.namespace("history_container")
HistoryContainer = history_container_ns.class_("HistoryContainer", cg.Component)

CONFIG_SCHEMA = cv.Schema(
    {
        cv.Required(CONF_ID): cv.declare_id(HistoryContainer),
        cv.Required(CONF_SENSOR): cv.use_id(sensor.Sensor),
        cv.Required(CONF_NAME): cv.string,
        cv.Optional(CONF_LENGTH, default=20): cv.positive_not_null_int,
    }
).extend(cv.COMPONENT_SCHEMA)


@coroutine_with_priority(40.0)
async def to_code(config):
    cg.add_define("USE_HISTORY_CONTAINER")
    sens = await cg.get_variable(config[CONF_SENSOR])

    container = cg.new_Pvariable(config[CONF_ID])
    cg.add(cg.App.register_history_container(container))
    await cg.register_component(container, config)

    cg.add(container.set_sensor(sens))
    cg.add(container.set_name(config[CONF_NAME]))
    cg.add(container.set_length(config[CONF_LENGTH]))
