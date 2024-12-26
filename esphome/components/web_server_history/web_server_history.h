#pragma once

#include "web_server.h"

#ifdef USE_WEBSERVER_HISTORY

// #include "esphome/core/controller.h"

namespace esphome {
namespace web_server_history {

using namespace esphome::web_server;

class HistoryData {
 public:
  void init();
  ~HistoryData();
  void set_name(std::string name) { name_ = std::move(name); }
  std::string get_name() { return name_; }
  uint32_t get_update_time_ms() { return update_time_; }
  void set_update_time_ms(uint32_t update_time_ms) { update_time_ = update_time_ms; }
  void take_sample(float data);
  void set_length(int length) { length_ = length; }
  int get_length() const { return length_; }
  float get_value(int idx) const { return samples_[(count_ + length_ - 1 - idx) % length_]; }
  std::vector<float> samples_;
 protected:
  uint32_t last_sample_;
  uint32_t period_{0};       /// in ms
  uint32_t update_time_;  /// in ms
  int length_;
  int count_{0};
  std::string name_{""};
};

class WebServerHistory : public WebServer {
  public:
    WebServerHistory(web_server_base::WebServerBase *base) : WebServer(base) {};
    void add_history_data(sensor::Sensor *sensor, HistoryData *hdata) { history_datas_[sensor] = hdata; };
    void setup();
    std::string sensor_json(sensor::Sensor *obj, float value, JsonDetail start_config);

  protected:
    std::map<sensor::Sensor*, HistoryData*> history_datas_;

};
}
}

#endif
