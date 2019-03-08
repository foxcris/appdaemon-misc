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
            self._resethandle = self.run_at(
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
            self._resethandle = self.run_at(
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
            self._resethandle = self.run_at(
                self._reset_lights,
                datetime.now() + timedelta(seconds=self._resettime))

    def _reset_lights(self, dtime):
        self._log_debug("reset_lights")
        self._resethandle = None
        self.call_service(
            "switch/turn_off", entity_id="switch.basementstairsdownstairs_2")
        self.call_service("switch/turn_off", entity_id="switch.basementpantry")


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
        self._handle_automatic_lights_morning_on = self.run_at_sunrise(
            self._automatic_lights_morning_on, offset=0)
        self._handle_automatic_lights_morning_off = self.run_at_sunrise(
            self._automatic_lights_morning_off, offset=7200)
        self._handle_automatic_lights_evening_on = self.run_at_sunset(
            self._automatic_lights_evening_on, offset=0)
        self._handle_automatic_lights_evening_off = self.run_daily(
            self._automatic_lights_evening_off,
            datetime.today() + timedelta(hours=23))

    def _light_livingroom_changed(self, entityid, attribute, old, new, kwargs):
        if attribute == "state" and new == "on":
            if self.get_state("input_boolean.light_livingroom_cozy") == "on":
                self._log("Turn on Lights in Livingroom")
                self._turn_on_light_livingroom_cozy()
            elif (self.get_state(
                  "input_boolean.light_livingroom_dimmed") == "on"):
                self._turn_on_light_livingroom_dimmed()
            else:
                self._turn_on_light_livingroom_reading()
        if attribute == "state" and new == "off":
            self._log("Turn off Lights in Livingroom")
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
        self._log("Turn on light livingroom cozy")
        self.call_service(
            "input_boolean/turn_on",
            entity_id="input_boolean.light_livingroom_cozy")
        self.call_service(
            "light/turn_on", entity_id="light.fireplace",
            brightness=255, rgb_color=[255, 135, 29])
        self.call_service(
            "light/turn_off", entity_id="light.couch")

    def _turn_on_light_livingroom_dimmed(self):
        self._log("Turn on light livingroom dimmed")
        self.call_service(
            "input_boolean/turn_on",
            entity_id="input_boolean.light_livingroom_dimmed")
        self.call_service(
            "light/turn_on", entity_id="light.fireplace",
            brightness=77, rgb_color=[255, 135, 29])
        self.call_service(
            "light/turn_on", entity_id="light.couch",
            brightness=77, rgb_color=[255, 207, 120])

    def _turn_on_light_livingroom_reading(self):
        self._log("Turn on light livingroom reading")
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
        self._activate_scene("cozy")
        self._handle_automatic_lights_morning_on = self.run_at_sunrise(
            self._automatic_lights_morning_on, offset=0)

    def _automatic_lights_evening_on(self, kwargs):
        self.call_service(
            "input_boolean/turn_on",
            entity_id="input_boolean.light_livingroom")
        self._activate_scene("cozy")
        self._handle_automatic_lights_evening_on = self.run_at_sunset(
            self._automatic_lights_evening_on, offset=0)

    def _automatic_lights_morning_off(self, kwargs):
        self.call_service(
            "input_boolean/turn_off",
            entity_id="input_boolean.light_livingroom")
        self._handle_automatic_lights_morning_off = self.run_at_sunrise(
            self._automatic_lights_morning_off, offset=7200)

    def _automatic_lights_evening_off(self, kwargs):
        self.call_service(
            "input_boolean/turn_off",
            entity_id="input_boolean.light_livingroom")
        self._handle_automatic_lights_evening_off = self.run_daily(
            self._automatic_lights_evening_off,
            datetime.today() + timedelta(hours=23))
