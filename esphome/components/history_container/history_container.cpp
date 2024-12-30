#include "history_container.h"

#ifdef USE_HISTORY_CONTAINER
#include "esphome/core/log.h"
#include <vector>

namespace esphome {
namespace history_container {

static const char *const TAG = "history_container";

void HistoryContainer::init() {
  ESP_LOGI(TAG, "Init history container %s", this->get_name().c_str());
  // init the samples with the datapairs of {time: 0, value : NAN}
  this->samples_.resize(this->length_, data_point{0, NAN});
  this->last_sample_ = millis();
  this->sensor_->add_on_state_callback([this](float state) { this->take_sample(state); });
}

void HistoryContainer::take_sample(float value) {
  /*
  we would like to have last sample time to be 0 and all other ascending
  dt in ms
  */

  // time of this sample
  uint32_t tm = millis();
  // time difference between this and the last sample
  uint32_t dt = tm - this->last_sample_;

  // shifting all samples by dt
  for (data_point &dp : this->samples_) {
    dp.time += dt;
  }
  // append this sample as last with time 0
  this->samples_[this->count_].value = value;
  this->samples_[this->count_].time = 0;
  this->count_ = (this->count_ + 1) % this->length_;
  ESP_LOGI(TAG, "History update with value: %f", value);
  this->last_sample_ = tm;
  this->on_update_callback_.call();
}

void HistoryContainer::add_on_update_callback(std::function<void()> &&callback) {
  this->on_update_callback_.add(std::move(callback));
}

void HistoryContainer::setup() { this->init(); }

void HistoryContainer::loop() {}

void HistoryContainer::dump_config() {
  ESP_LOGCONFIG(TAG, "History Container '%s':", this->get_name().c_str());
  ESP_LOGCONFIG(TAG, "  Length: %d", this->length_);
  ESP_LOGCONFIG(TAG, "  Sensor: %s", this->sensor_->get_name().c_str());
  ESP_LOGCONFIG(TAG, "  Icon: %s", this->get_icon().c_str());
  ESP_LOGCONFIG(TAG, "  Unit of Measurement: %s", this->get_unit_of_measurement().c_str());
}

}  // namespace history_container
}  // namespace esphome
#endif  // USE_HISTORY_CONTAINER
