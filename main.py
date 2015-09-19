#!/bin/python3
# Created by Yakir Sitbon <http://www.yakirs.net/>

import re
import urllib.request
import json
import time
import sys
import fcntl
from gi.repository import Notify

OREF_JSON_URL = 'http://www.oref.org.il/WarningMessages/Alert/alerts.json?v=1'
MINUTES_TO_WAIT = 2
NOTIFY_INSTANCE_ID = 'red_alert_notification'
PID_FILENAME = 'red-alert.pid'

Notify.init(NOTIFY_INSTANCE_ID)


class RedAlertNotification:
    def __init__(self):
        super().__init__()
        self.notification = Notify.Notification()
        self.notification.set_urgency(Notify.Urgency.CRITICAL)

        self.is_singleton_program = True

        self.last_id = '0'
        self.area_db = self._get_cities_data()

    @staticmethod
    def _get_cities_data():
        json_data = open('resources/cities.json')
        cities = json.load(json_data)
        json_data.close()

        return cities

    @staticmethod
    def beep():
        print("\a")

    def on_notification_closed(self, event, id, user_data):
        pass

    def notify(self, title="", body=""):
        """
        subprocess.Popen(
            ['notify-send', '--expire-time=2000', '--hint=int:transient:1', '--urgency=critical', title, body])
        """
        self.notification.clear_actions()
        self.notification.update(title, body, None)
        self.notification.add_action("close", "Close", self.on_notification_closed, None, None)
        self.notification.show()

    def on_alert(self):
        pass

    def main_loop(self):
        # Is Another Running?
        if self.is_singleton_program:
            pid_file = open(PID_FILENAME, 'w')

            try:
                fcntl.lockf(pid_file, fcntl.LOCK_EX | fcntl.LOCK_NB)
            except IOError:
                print('Another instance is already running, quitting.')
                sys.exit(1)

        while True:
            try:
                n = set()
                json_data = json.loads(urllib.request.urlopen(OREF_JSON_URL).read().decode("utf-16"))
                data = set(json_data['data'])

                if self.last_id != json_data['id']:
                    self.last_id = json_data['id']
                    cities = {}  # code to cities names
                    for item in data:
                        for city in item.split(','):
                            city_name = re.sub("\d+", "", city).strip()
                            code = re.sub("[^\d]+", "", city).strip()

                            city_codes = cities.get(code, [])
                            city_codes += self.area_db.get(city, [])
                            cities[code] = city_codes

                    if len(cities) > 0:
                        self.beep()
                        all_cities = [item for sublist in cities.values() for item in sublist]
                        self.notify(', '.join(data - n), ', '.join(all_cities))
                        print(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()) + "\t" + ', '.join(data - n))

                        self.on_alert()

                n = data

            except:
                pass

            time.sleep(MINUTES_TO_WAIT)

if __name__ == "__main__":
    instance = RedAlertNotification()
    instance.main_loop()
