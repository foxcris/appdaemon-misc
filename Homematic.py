from datetime import datetime, timedelta
from Helper import BaseClass


class HomematicReconnect(BaseClass):

    def initialize(self):
        self._reconnecttimeout = 120
        self._reconnecthandle = self.run_at(
            self._reconnect_homematic,
            datetime.now() + timedelta(seconds=self._reconnecttimeout))
        self._resethandle = self.listen_state(self._reset_timeout)

    def _reconnect_homematic(self, dtime):
        self._log_debug("_reconnect_homematic")
        self.call_service("homematic/reconnect")

    def _reset_timeout(self, entityid, attribute, old, new, kwargs):
        interface = self.get_state(entityid, attribute="interface")
        if interface is not None and interface == "pigear":
            # self._log_debug("Reset Timeout")
            self.cancel_timer(self._reconnecthandle)
            self._reconnecthandle = self.run_at(
                self._reconnect_homematic,
                datetime.now() + timedelta(seconds=self._reconnecttimeout))


class HomematicBattery(BaseClass):

    def initialize(self):
        self._batterylimit = 2.3
        # if not self.entity_exists("input_number.homematic_batterylimit"):
        #    self.set_state("input_number.homematic_batterylimit",
        # state=self._batterylimit)
        self._resethandle = self.listen_state(self._check_battery)

    def _check_battery(self, entityid, attribute, old, new, kwargs):
        interface = self.get_state(entityid, attribute="interface")
        if interface is not None and interface == "pigear":
            if attribute == "battery" and new <= self._batterylimit:
                self._log_debug("Battery Empty")
                self.call_service("telegram_bot/send_message",
                                  message="Battery Warning!: \
                                  Battery of entity %s is %s" %
                                  (self.get_state(
                                      entityid, attribute="friendly_name"),
                                      new))
