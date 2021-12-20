from datetime import time, datetime, timedelta
from helper.Helper import BaseClass


class BasementLights(BaseClass):
    def initialize(self):
        self._resettime = 900
        self._resethandle = None
        self._handle_motion_sensor = self.listen_state(
            self._motion_detected,
            "binary_sensor.basementstairs_motion_sensor_sensor")
        self._handle_motion_sensor_burglar = self.listen_state(
            self._motion_detected,
            "sensor.basementstairs_motion_sensor_burglar")
        self._handle_switch_basementpantry = self.listen_state(
            self._switch_basement_changed, "switch.basementpantry_2")
        self._handle_switch_basementstairsdownstairs = self.listen_state(
            self._switch_basementstairsdownstairs_changed,
            "switch.basementstairsdownstairs_2")
        # self._handle_motion_sensor = self.listen_state(
        #    self._get_all_events)

    def _get_all_events(self, entityid, attribute, old, new, kwargs):
        self._log_debug(
            "%s %s %s %s" % (entityid, attribute, old, new))

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
            self._resethandle = self.run_at(
                self._reset_lights,
                datetime.now() + timedelta(seconds=self._resettime))
        else:
            # state=="off"
            if self.get_state("switch.basementstairsdownstairs_2") == "on":
                self.call_service(
                    "switch/turn_off",
                    entity_id="switch.basementstairsdownstairs_2")
            # motion sensor künstlich zurück setzen
            if self.get_state(
                    "binary_sensor.basementstairs_motion_sensor_sensor"
                    ) == "on":
                self._log_debug("Manually reset motion sensor to state 'off'")
                self.set_state(
                    "binary_sensor.basementstairs_motion_sensor_sensor",
                    state="off")

    def _switch_basementstairsdownstairs_changed(self, entityid, attribute,
                                                 old, new, kwargs):
        self._log_debug("switch_basementstairsdownstairs_changed")
        if attribute == "state" and new == "on":
            # check if switch.basementpantry is on, if not turn it on
            if self.get_state("switch.basementpantry_2") == "off":
                self.call_service(
                    "switch/turn_on", entity_id="switch.basementpantry_2")
            if self._resethandle is not None:
                self.cancel_timer(self._resethandle)
            self._resethandle = self.run_at(
                self._reset_lights,
                datetime.now() + timedelta(seconds=self._resettime))
        else:
            # state=="off"
            if self.get_state("switch.basementpantry_2") == "on":
                self.call_service(
                    "switch/turn_off", entity_id="switch.basementpantry_2")
            # motion sensor künstlich zurück setzen
            if self.get_state(
                    "binary_sensor.basementstairs_motion_sensor_sensor"
                    ) == "on":
                self._log_debug("Manually reset motion sensor to state 'off'")
                self.set_state(
                    "binary_sensor.basementstairs_motion_sensor_sensor",
                    state="off")

    def _motion_detected(self, entityid, attribute, old, new, kwargs):
        self._log_debug("motion_detected")
        self._log_debug(
            "%s %s %s %s" % (entityid, attribute, old, new))
        if ((entityid == "binary_sensor.basementstairs_motion_sensor_sensor"
             and attribute == "state" and new == "on")
            or (
            entityid == "binary_sensor.basementstairs_motion_sensor_burglar"
                and attribute == "state" and new > 0)):
            # check if switch.basementstairsdownstairs_2 is on,
            # if not turn it on
            if self.get_state("switch.basementstairsdownstairs_2") == "off":
                self.call_service(
                    "switch/turn_on",
                    entity_id="switch.basementstairsdownstairs_2")
            # check if switch.basementpantry is on, if not turn it on
            if self.get_state("switch.basementpantry_2") == "off":
                self.call_service(
                    "switch/turn_on", entity_id="switch.basementpantry_2")

            self._reset_motion_handle()

    def _reset_motion_handle(self):
        if self._resethandle is not None:
            self.cancel_timer(self._resethandle)
        self._resethandle = self.run_at(
            self._reset_lights,
            datetime.now() + timedelta(seconds=self._resettime))

    def _reset_lights(self, dtime):
        self._log_debug("reset_lights")
        self._resethandle = None
        self.call_service(
            "switch/turn_off", entity_id="switch.basementstairsdownstairs_2")
        self.call_service("switch/turn_off", entity_id="switch.basementpantry_2")


class LivingRoomLights(BaseClass):
    def initialize(self):
        self._handle_light_livingroom = self.listen_state(
            self._light_livingroom_changed,
            "input_boolean.light_livingroom")
        self._handle_light_livingroom_cozy = self.listen_state(
            self._light_livingroom_cozy_changed,
            "input_boolean.light_livingroom_cozy")
        self._handle_light_livingroom_dimmed = self.listen_state(
            self._light_livingroom_dimmed_changed,
            "input_boolean.light_livingroom_dimmed")
        self._handle_light_livingroom_reading = self.listen_state(
            self._light_livingroom_reading_changed,
            "input_boolean.light_livingroom_reading")
        self._handle_automatic_lights_morning_on = self.run_daily(
            self._automatic_lights_morning_on, time(5, 30, 0))
        self._log_info("Time to turn on lights every day: {}"
                  .format(time(5, 30, 0)))
        self._handle_automatic_lights_morning_off = self.run_daily(
            self._automatic_lights_morning_off, time(7, 0, 0))
        self._log_info("Time to turn off lights every day: {}"
                  .format(time(7, 0, 0)))
        self._handle_automatic_lights_evening_on = self.run_at_sunset(
            self._automatic_lights_evening_on, offset=0)
        self._log_info("Time to turn on lights: {}"
                  .format(self.sunset()))
        self._handle_automatic_lights_evening_off = self.run_daily(
            self._automatic_lights_evening_off,
            time(23, 0, 0))
        self._log_info("Time to turn off lights every day: {}"
                  .format(time(23, 0, 0)))

    def _light_livingroom_changed(self, entityid, attribute, old, new, kwargs):
        if attribute == "state" and new == "on":
            if self.get_state("input_boolean.light_livingroom_cozy") == "on":
                self._log_info("Turn on Lights in Livingroom")
                self._turn_on_light_livingroom_cozy()
            elif (self.get_state(
                  "input_boolean.light_livingroom_dimmed") == "on"):
                self._turn_on_light_livingroom_dimmed()
            else:
                self._turn_on_light_livingroom_reading()
        if attribute == "state" and new == "off":
            self._log_info("Turn off Lights in Livingroom")
            self.call_service(
                "light/turn_off", entity_id="light.fireplace")
            self.call_service(
                "light/turn_off", entity_id="light.couch")

    def _light_livingroom_cozy_changed(self, entityid,
                                       attribute, old, new, kwargs):
        if attribute == "state" and new == "on":
            self._activate_scene("cozy")
        else:
            self._set_default_light_scene("cozy")

    def _light_livingroom_dimmed_changed(self, entityid,
                                         attribute, old, new, kwargs):
        if attribute == "state" and new == "on":
            self._activate_scene("dimmed")
        else:
            self._set_default_light_scene("dimmed")

    def _light_livingroom_reading_changed(self, entityid,
                                          attribute, old, new, kwargs):
        if attribute == "state" and new == "on":
            self._activate_scene("reading")
        else:
            self._set_default_light_scene("reading")

    def _set_default_light_scene(self, scene):
        cozy = self.get_state("input_boolean.light_livingroom_cozy") == "on"
        dimmed = self.get_state(
            "input_boolean.light_livingroom_dimmed") == "on"
        reading = self.get_state(
            "input_boolean.light_livingroom_reading") == "on"

        if not cozy and not dimmed and not reading:
            # set default
            self.call_service(
                "input_boolean/turn_on",
                entity_id="input_boolean.light_livingroom_{}".format(scene))

    def _activate_scene(self, scene):
        if scene == "cozy":
            if self.get_state("input_boolean.light_livingroom") == "on":
                self._turn_on_light_livingroom_cozy()
            self.call_service(
                "input_boolean/turn_off",
                entity_id="input_boolean.light_livingroom_dimmed")
            self.call_service(
                "input_boolean/turn_off",
                entity_id="input_boolean.light_livingroom_reading")
        elif scene == "dimmed":
            if self.get_state("input_boolean.light_livingroom") == "on":
                self._turn_on_light_livingroom_dimmed()
            self.call_service(
                "input_boolean/turn_off",
                entity_id="input_boolean.light_livingroom_cozy")
            self.call_service(
                "input_boolean/turn_off",
                entity_id="input_boolean.light_livingroom_reading")
        elif scene == "reading":
            if self.get_state("input_boolean.light_livingroom") == "on":
                self._turn_on_light_livingroom_reading()
            self.call_service(
                "input_boolean/turn_off",
                entity_id="input_boolean.light_livingroom_cozy")
            self.call_service(
                "input_boolean/turn_off",
                entity_id="input_boolean.light_livingroom_dimmed")

    def _turn_on_light_livingroom_cozy(self):
        self._log_info("Turn on light livingroom cozy")
        self.call_service(
            "input_boolean/turn_on",
            entity_id="input_boolean.light_livingroom_cozy")
        self.call_service(
            "light/turn_on", entity_id="light.fireplace",
            brightness=255, rgb_color=[255, 135, 29])
        self.call_service(
            "light/turn_off", entity_id="light.couch")

    def _turn_on_light_livingroom_dimmed(self):
        self._log_info("Turn on light livingroom dimmed")
        self.call_service(
            "input_boolean/turn_on",
            entity_id="input_boolean.light_livingroom_dimmed")
        self.call_service(
            "light/turn_on", entity_id="light.fireplace",
            brightness=255, rgb_color=[255, 135, 29])
        self.call_service(
            "light/turn_on", entity_id="light.couch",
            brightness=77, rgb_color=[255, 207, 120])

    def _turn_on_light_livingroom_reading(self):
        self._log_info("Turn on light livingroom reading")
        self.call_service(
            "input_boolean/turn_on",
            entity_id="input_boolean.light_livingroom_reading")
        self.call_service(
            "light/turn_on", entity_id="light.fireplace",
            brightness=254, rgb_color=[255, 135, 29])
        self.call_service(
            "light/turn_on", entity_id="light.couch",
            brightness=254, rgb_color=[255, 210, 129])

    def _automatic_lights_morning_on(self, kwargs):
        self.call_service(
            "input_boolean/turn_on",
            entity_id="input_boolean.light_livingroom")
        self._activate_scene("dimmed")

    def _automatic_lights_evening_on(self, kwargs):
        self.call_service(
            "input_boolean/turn_on",
            entity_id="input_boolean.light_livingroom")
        self._activate_scene("dimmed")
        self._handle_automatic_lights_evening_on = self.run_at_sunset(
            self._automatic_lights_evening_on, offset=0)
        self._log_info("Time to turn on lights: {}"
                  .format(self.sunset()))

    def _automatic_lights_morning_off(self, kwargs):
        self.call_service(
            "input_boolean/turn_off",
            entity_id="input_boolean.light_livingroom")

    def _automatic_lights_evening_off(self, kwargs):
        self.call_service(
            "input_boolean/turn_off",
            entity_id="input_boolean.light_livingroom")
