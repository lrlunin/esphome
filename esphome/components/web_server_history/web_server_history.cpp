
#include "web_server_history.h"
#ifdef USE_WEBSERVER_HISTORY

namespace esphome {
namespace web_server_history {

static const char *const TAG = "web_server_history";

// #ifdef USE_WEBSERVER_PRIVATE_NETWORK_ACCESS
// static const char *const HEADER_PNA_NAME = "Private-Network-Access-Name";
// static const char *const HEADER_PNA_ID = "Private-Network-Access-ID";
// static const char *const HEADER_CORS_REQ_PNA = "Access-Control-Request-Private-Network";
// static const char *const HEADER_CORS_ALLOW_PNA = "Access-Control-Allow-Private-Network";
// #endif

void HistoryData::init() {
  this->samples_.resize(length_);
  this->last_sample_ = millis();
}
void HistoryData::take_sample(float data) {
  uint32_t tm = millis();
  uint32_t dt = tm - last_sample_;
  last_sample_ = tm;

  // Step data based on time
  this->period_ += dt;
  while (this->period_ >= this->update_time_) {
    this->samples_[this->count_] = data;
    this->period_ -= this->update_time_;
    this->count_ = (this->count_ + 1) % this->length_;
    ESP_LOGV(TAG, "Updating trace with value: %f", data);
  }
}
void WebServerHistory::setup() {
  // running additional setup for history datas
  for (auto &key_value: this->history_datas_) {
    sensor::Sensor* sensor = key_value.first;
    HistoryData* data = key_value.second;
    data->init();
    ESP_LOGI(TAG, "Initiated sensor id %s", sensor->get_object_id().c_str());
    ESP_LOGI(TAG, "data length %d, upd_time", data->get_update_time_ms(), data->get_length());
    sensor->add_on_state_callback([data, sensor](float state) {
      ESP_LOGI(TAG, "sensor_id: %s, State: %f", sensor->get_object_id().c_str(), state);
      data->take_sample(state);
    });
  }
  // call the parent class constructor
  WebServer::setup();
}
#ifdef USE_SENSOR
std::string WebServerHistory::sensor_json(sensor::Sensor *obj, float value, JsonDetail start_config) {
  return json::build_json([this, obj, value, start_config](JsonObject root) {
    std::string state;
    if (std::isnan(value)) {
      state = "NA";
    } else {
      state = value_accuracy_to_string(value, obj->get_accuracy_decimals());
      if (!obj->get_unit_of_measurement().empty())
        state += " " + obj->get_unit_of_measurement();
  }
  root["id"] = "sensor-" + obj->get_object_id();
  root["name"] = obj->get_name();
  if (this->history_datas_.find(obj) != this->history_datas_.end()) {
    HistoryData* data = this->history_datas_[obj];
    JsonArray values_array = root.createNestedArray("values");
    for (uint32_t i = data->get_length(); i > 0; i--) {
      values_array.add(data->get_value(i));
    }
  }
  else {
    // default behavior for not remebmered sensors
  }
  root["state"] = state;
  if (start_config == DETAIL_ALL) {
  if (this->sorting_entitys_.find(obj) != this->sorting_entitys_.end()) {
    root["sorting_weight"] = this->sorting_entitys_[obj].weight;
    if (this->sorting_groups_.find(this->sorting_entitys_[obj].group_id) != this->sorting_groups_.end()) {
      root["sorting_group"] = this->sorting_groups_[this->sorting_entitys_[obj].group_id].name;
    }
  }
  if (!obj->get_unit_of_measurement().empty())
    root["uom"] = obj->get_unit_of_measurement();
    }
  }
  );
}
#endif
}
}
#endif
