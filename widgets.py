# coding=utf-8
import json
from kivy import Logger
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.widget import Widget
from kivy.utils import get_color_from_hex
import datetime
from kivy.properties import NumericProperty, DictProperty
from kivy.properties import ObjectProperty
from kivy.properties import StringProperty
from kivy.animation import Animation


class MainWidget(BoxLayout):
    def __init__(self, **kwargs):
        super(MainWidget, self).__init__(**kwargs)
        self.devices = {}

    def add_device_widget(self, device_id, data):
        device = DeviceWidget()
        device.device_id = device_id
        self.devices[device_id] = device
        self.add_widget(device)

    def update(self, topic, payload):
        Logger.info("main: update for %s" % topic)

        if not self.devices:
            self.clear_widgets()

        payload = json.loads(payload)
        device_id = payload['deviceId']
        readings = payload['readings']
        if device_id not in self.devices:
            self.add_device_widget(device_id, readings)
        self.devices[device_id].update(readings)


class DeviceWidget(BoxLayout):
    device_id = StringProperty("ddd")

    name_label = ObjectProperty()
    sensor_container = ObjectProperty()
    history_container = ObjectProperty()

    def __init__(self, **kwargs):

        super(DeviceWidget, self).__init__(**kwargs)
        self.sensors = {}
        self.histories = {}

    def on_device_id(self, device, device_id):
        self.name_label.text = device_id

    def update(self, readings):
        for reading in readings:
            meaning = reading['meaning']
            if meaning not in self.sensors:
                sensor = SensorWidget()
                sensor.meaning = meaning
                self.sensors[meaning] = sensor
                self.sensor_container.add_widget(sensor)
            self.sensors[meaning].timestamp = reading['recorded']
            self.sensors[meaning].value = reading['value']

            if meaning not in self.histories:
                history_widget = SensorHistoryWidget()
                history_widget.meaning = meaning
                self.histories[meaning] = history_widget
                self.history_container.add_widget(history_widget)

            self.histories[meaning].add_value(reading['value'], reading['recorded'])


class SensorWidget(BoxLayout):
    meaning = StringProperty()
    value = NumericProperty()
    timestamp = NumericProperty()

    center_label = ObjectProperty()

    color = ObjectProperty([0, 0, 0, 1])

    angle = NumericProperty()

    MEANING_COLORS = {
        "temperature": get_color_from_hex("0088aaff"),
        "humidity": get_color_from_hex("00aa44ff"),
    }

    UNITS = {
        "temperature": u"°C",
        "humidity": "%",
    }

    VALUE_BORDERS = {
        "temperature": (20., 30.),
        "humidity": (0., 100.),
    }

    LABEL_PATTERN = "%s\n[b][size=20sp]%s %s[/size][/b]\n[color=918a6fff]%s sec ago[/color]"

    def update(self, sensor, value):
        read_time = datetime.datetime.fromtimestamp(self.timestamp / 1e3)

        read_ago = datetime.datetime.now() - read_time

        unit = self.UNITS.get(self.meaning, "")
        self.center_label.text = self.LABEL_PATTERN % (self.meaning, self.value, unit, int(read_ago.total_seconds()))
        self.color = self.MEANING_COLORS.get(self.meaning, (.5, 5, .5, 1))

        min_value, max_value = self.VALUE_BORDERS.get(self.meaning, (None, None))
        if min_value is None:
            self.angle = 360
        else:
            interval = max_value - min_value
            percentage = (float(self.value) - min_value) / interval
            Animation(angle=360 * percentage, d=.5, t='in_out_cubic').start(self)

    on_meaning = on_value = on_timestamp = update


class SensorHistoryWidget(Widget):
    values = DictProperty()
    meaning = StringProperty()

    def add_value(self, value, timestamp):
        pass
