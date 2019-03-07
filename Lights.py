from datetime import datetime, timedelta
from Helper import BaseClass


class BasementLights(BaseClass):
    def initialize(self):
        self._resettime = 900
        self._resethandle = None
        self._handle_motion_sensor = self.listen_state(
            self._motion_detected,
            "binary_sensor.basementstairs_motion_sensor_sensor")
        self._handle_switch_basementpantry = self.listen_state(
            self._switch_basement_changed, "switch.basementpantry")
        self._handle_switch_basementstairsdownstairs = self.listen_state(
            self._switch_basementstairsdownstairs_changed,
            "switch.basementstairsdownstairs_2")

    def _switch_basement_changed(self, entityid, attribute, old, new, kwargs):
        self._log_debug("switch_basement_changed")
        if attribute == "state" and new == "on":
            # check if switch.basementstairsdownstairs_2 is on,
            # if not turn it on
            if self.get_state("switch.basementstairsdownstairs_2") == "off":
                self.call_service(
                    "switch/turn_on",
                    entity_id="switch.basementstairsdownstairs_2")
            if self._resethandle is not None:
                self.cancel_timer(self._resethandle)
            self._log_debug(datetime.now()
                            + timedelta(seconds=self._resettime))
            self.run_at(
                self._reset_lights,
                datetime.now() + timedelta(seconds=self._resettime))
        else:
            # state=="off"
            if self.get_state("switch.basementstairsdownstairs_2") == "on":
                self.call_service(
                    "switch/turn_off",
                    entity_id="switch.basementstairsdownstairs_2")

    def _switch_basementstairsdownstairs_changed(self, entityid, attribute,
                                                 old, new, kwargs):
        self._log_debug("switch_basementstairsdownstairs_changed")
        if attribute == "state" and new == "on":
            # check if switch.basementpantry is on, if not turn it on
            if self.get_state("switch.basementpantry") == "off":
                self.call_service(
                    "switch/turn_on", entity_id="switch.basementpantry")
            if self._resethandle is not None:
                self.cancel_timer(self._resethandle)
            self.run_at(
                self._reset_lights,
                datetime.now() + timedelta(seconds=self._resettime))
        else:
            # state=="off"
            if self.get_state("switch.basementpantry") == "on":
                self.call_service(
                    "switch/turn_off", entity_id="switch.basementpantry")

    def _motion_detected(self, entityid, attribute, old, new, kwargs):
        self._log_debug("motion_detected")
        self._log_debug(
            "%s %s %s %s" % (entityid, attribute, old, new))
        if attribute == "state" and new == "on":
            # check if switch.basementstairsdownstairs_2 is on,
            # if not turn it on
            if self.get_state("switch.basementstairsdownstairs_2") == "off":
                self.call_service(
                    "switch/turn_on",
                    entity_id="switch.basementstairsdownstairs_2")
            # check if switch.basementpantry is on, if not turn it on
            if self.get_state("switch.basementpantry") == "off":
                self.call_service(
                    "switch/turn_on", entity_id="switch.basementpantry")

            if self._resethandle is not None:
                self.cancel_timer(self._resethandle)
            self.run_at(
                self._reset_lights,
                datetime.now() + timedelta(seconds=self._resettime))

    def _reset_lights(self, dtime):
        self._log_debug("reset_lights")
        self._resethandle = None
        self.call_service(
            "switch/turn_off", entity_id="switch.basementstairsdownstairs_2")
        self.call_service("switch/turn_off", entity_id="switch.basementpantry")
