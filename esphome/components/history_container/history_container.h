#pragma once

#include "esphome/core/component.h"
#include "esphome/core/entity_base.h"
#include "esphome/components/sensor/sensor.h"

#ifdef USE_HISTORY_CONTAINER

namespace esphome {
namespace history_container {

struct data_point {
  uint32_t time;
  float value;
};

// we create a container for history data FOR EACH sensor
class HistoryContainer : public Component, public EntityBase {
 public:
  void init();
  HistoryContainer() = default;
  ~HistoryContainer() = default;
  void set_name(std::string name) { name_ = std::move(name); }
  std::string get_name() { return name_; }
  void set_sensor(sensor::Sensor *sensor) { sensor_ = sensor; }
  sensor::Sensor *get_sensor() { return sensor_; }
  uint32_t get_update_time_ms() { return update_time_; }
  void take_sample(float value);
  void set_length(int length) { length_ = length; }
  int get_length() const { return length_; }
  data_point get_value(int idx) const { return samples_[(count_ + length_ - 1 - idx) % length_]; }

  void add_on_state_callback(std::function<void(float)> &&callback);

 protected:
  uint32_t last_sample_;
  uint32_t period_{0};    /// in ms
  uint32_t update_time_;  /// in ms
  int length_;
  int count_{0};
  std::vector<data_point> samples_;
  std::string name_{""};
  sensor::Sensor *sensor_{nullptr};

  void setup() override;
  void loop() override;

  void dump_config() override;
};

}  // namespace history_container
}  // namespace esphome
#endif
