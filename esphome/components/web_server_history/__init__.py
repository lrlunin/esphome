from __future__ import annotations

import esphome.codegen as cg
from esphome.components import web_server, sensor

import esphome.config_validation as cv

from esphome.const import (
    CONF_AUTH,
    CONF_CSS_INCLUDE,
    CONF_CSS_URL,
    CONF_ENABLE_PRIVATE_NETWORK_ACCESS,
    CONF_ID,
    CONF_INCLUDE_INTERNAL,
    CONF_JS_INCLUDE,
    CONF_JS_URL,
    CONF_LOCAL,
    CONF_LOG,
    CONF_NAME,
    CONF_OTA,
    CONF_PASSWORD,
    CONF_SENSOR,
    CONF_LENGTH,
    CONF_UPDATE_INTERVAL,
    ENTITY_CATEGORY_CONFIG,
    CONF_PORT,
    CONF_USERNAME,
    CONF_VERSION,
    CONF_WEB_SERVER,
    CONF_WEB_SERVER_ID,
    PLATFORM_BK72XX,
    PLATFORM_ESP32,
    PLATFORM_ESP8266,
    PLATFORM_RTL87XX,
)
from esphome.core import CORE, coroutine_with_priority

AUTO_LOAD = ["json", "web_server_base"]

DEPENDENCIES = ["sensor"]

CONF_SORTING_GROUP_ID = "sorting_group_id"
CONF_SORTING_GROUPS = "sorting_groups"
CONF_SORTING_WEIGHT = "sorting_weight"

web_server_ns = cg.esphome_ns.namespace("web_server")

WebServer = web_server_ns.class_("WebServer", cg.Component, cg.Controller)
web_server_history_ns = cg.esphome_ns.namespace("web_server_history")

WebServerHistory = web_server_history_ns.class_("WebServerHistory", WebServer)
HistoryData = web_server_history_ns.class_("HistoryData")

FINAL_VALIDATE_SCHMEA = web_server.FINAL_VALIDATE_SCHEMA

sorting_group = web_server.sorting_group

WEBSERVER_HISTORY_SORTING_SCHEMA = cv.Schema(
    {
        cv.Optional(CONF_WEB_SERVER): cv.Schema(
            {
                cv.OnlyWith(CONF_WEB_SERVER_ID, "web_server_history"): cv.use_id(WebServer),
                cv.Optional(CONF_SORTING_WEIGHT): cv.All(
                    cv.requires_component("web_server_history"),
                    cv.float_,
                ),
                cv.Optional(CONF_SORTING_GROUP_ID): cv.All(
                    cv.requires_component("web_server_history"),
                    cv.use_id(cg.int_),
                ),
            }
        )
    }
)

HISTORY_DATA_SCHEMA = cv.Schema(
    {
        cv.GenerateID(): cv.declare_id(HistoryData),
        cv.Required(CONF_SENSOR): cv.use_id(sensor.Sensor),
        cv.Required(CONF_LENGTH): cv.positive_not_null_int,
        cv.Required(CONF_UPDATE_INTERVAL): cv.positive_time_period_milliseconds,
    }
)

CONFIG_SCHEMA = cv.All(
    cv.Schema(
        {
            cv.GenerateID(): cv.declare_id(WebServerHistory),
            cv.Optional(CONF_PORT, default=80): cv.port,
            cv.Optional(CONF_VERSION, default=2): cv.one_of(1, 2, 3, int=True),
            cv.Optional(CONF_CSS_URL): cv.string,
            cv.Optional(CONF_CSS_INCLUDE): cv.file_,
            cv.Optional(CONF_JS_URL): cv.string,
            cv.Optional(CONF_JS_INCLUDE): cv.file_,
            cv.Optional(CONF_ENABLE_PRIVATE_NETWORK_ACCESS, default=True): cv.boolean,
            cv.Optional(CONF_AUTH): cv.Schema(
                {
                    cv.Required(CONF_USERNAME): cv.All(
                        cv.string_strict, cv.Length(min=1)
                    ),
                    cv.Required(CONF_PASSWORD): cv.All(
                        cv.string_strict, cv.Length(min=1)
                    ),
                }
            ),
            cv.GenerateID(web_server.CONF_WEB_SERVER_BASE_ID): cv.use_id(
                web_server.web_server_base.WebServerBase
            ),
            cv.Optional(CONF_INCLUDE_INTERNAL, default=False): cv.boolean,
            cv.SplitDefault(
                CONF_OTA,
                esp8266=True,
                esp32_arduino=True,
                esp32_idf=False,
                bk72xx=True,
                rtl87xx=True,
            ): cv.boolean,
            cv.Optional(CONF_LOG, default=True): cv.boolean,
            cv.Optional(CONF_LOCAL): cv.boolean,
            cv.Optional(CONF_SORTING_GROUPS): cv.ensure_list(sorting_group),
            cv.Optional(ENTITY_CATEGORY_CONFIG) : cv.ensure_list(HISTORY_DATA_SCHEMA)
        }
    ).extend(cv.COMPONENT_SCHEMA),
    cv.only_on([PLATFORM_ESP32, PLATFORM_ESP8266, PLATFORM_BK72XX, PLATFORM_RTL87XX]),
    web_server.default_url,
    web_server.validate_local,
    web_server.validate_ota,
    web_server.validate_sorting_groups,
)

@coroutine_with_priority(40.0)
async def to_code(config):
    paren = await cg.get_variable(config[web_server.CONF_WEB_SERVER_BASE_ID])

    var = cg.new_Pvariable(config[CONF_ID], paren)
    await cg.register_component(var, config)

    version = config[CONF_VERSION]

    cg.add(paren.set_port(config[CONF_PORT]))
    cg.add_define("USE_WEBSERVER_HISTORY")
    cg.add_define("LMAO_BOTTOM_TEXT_ONE")
    cg.add_define("USE_WEBSERVER")
    cg.add_define("USE_WEBSERVER_PORT", config[CONF_PORT])
    cg.add_define("USE_WEBSERVER_VERSION", version)

    if version >= 2:
        # Don't compress the index HTML as the data sizes are almost the same.
        web_server.add_resource_as_progmem("INDEX_HTML", web_server.build_index_html(config), compress=False)
    else:
        cg.add(var.set_css_url(config[CONF_CSS_URL]))
        cg.add(var.set_js_url(config[CONF_JS_URL]))
    cg.add(var.set_allow_ota(config[CONF_OTA]))
    cg.add(var.set_expose_log(config[CONF_LOG]))
    if config[CONF_ENABLE_PRIVATE_NETWORK_ACCESS]:
        cg.add_define("USE_WEBSERVER_PRIVATE_NETWORK_ACCESS")
    if CONF_AUTH in config:
        cg.add(paren.set_auth_username(config[CONF_AUTH][CONF_USERNAME]))
        cg.add(paren.set_auth_password(config[CONF_AUTH][CONF_PASSWORD]))
    if CONF_CSS_INCLUDE in config:
        cg.add_define("USE_WEBSERVER_CSS_INCLUDE")
        path = CORE.relative_config_path(config[CONF_CSS_INCLUDE])
        with open(file=path, encoding="utf-8") as css_file:
            web_server.add_resource_as_progmem("CSS_INCLUDE", css_file.read())
    if CONF_JS_INCLUDE in config:
        cg.add_define("USE_WEBSERVER_JS_INCLUDE")
        path = CORE.relative_config_path(config[CONF_JS_INCLUDE])
        with open(file=path, encoding="utf-8") as js_file:
            web_server.add_resource_as_progmem("JS_INCLUDE", js_file.read())
    cg.add(var.set_include_internal(config[CONF_INCLUDE_INTERNAL]))
    if CONF_LOCAL in config and config[CONF_LOCAL]:
        cg.add_define("USE_WEBSERVER_LOCAL")

    if (sorting_group_config := config.get(CONF_SORTING_GROUPS)) is not None:
        web_server.add_sorting_groups(var, sorting_group_config)

    # create HistoryDatas for each of listed sensor
    for conf_trace in config[ENTITY_CATEGORY_CONFIG]:
        history_data = cg.new_Pvariable(conf_trace[CONF_ID])
        
        # creating a sensor object
        sens_obj = await cg.get_variable(conf_trace[CONF_SENSOR])
        cg.add(history_data.set_name(conf_trace[CONF_SENSOR].id))
        cg.add(history_data.set_length(conf_trace[CONF_LENGTH]))
        cg.add(history_data.set_update_time_ms(conf_trace[CONF_UPDATE_INTERVAL]))
        cg.add(var.add_history_data(sens_obj, history_data))
