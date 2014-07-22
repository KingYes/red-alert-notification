#!/bin/python3
# Created by Yakir Sitbon <http://www.yakirs.net/>

import re
import urllib.request
import json
import time
import subprocess
import os

OREF_JSON_URL = 'http://www.oref.org.il/WarningMessages/alerts.json'
MINUTES_TO_WAIT = 2


class RedAlertNotification:
    def __init__(self):
        super().__init__()
        json_data = open('cities.json')
        self.area_db = json.load(json_data)
        json_data.close()

    def notify(self, title="", body=""):
        subprocess.Popen(['notify-send', '--expire-time=5000', '--hint=int:transient:1', '--urgency=critical', title, body])

    def beep(self):
        print("\a")

    def on_alert(self):
        pass

    def main_loop(self):
        n = set()
        while True:
            try:
                data = set(json.loads(
                    urllib.request.urlopen(OREF_JSON_URL).read().decode("utf-16"))['data'])

                if data - n != set():
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