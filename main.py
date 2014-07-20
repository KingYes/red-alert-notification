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


def notify(title="", body=""):
    subprocess.Popen(['notify-send', '--icon=error', title, body])


def beep():
    print("\a")


def is_smplayer_running():
    buffer = os.popen('ps -eo pcpu,pid,user,comm | grep -i "smplayer"$ | sed  "s/ smplayer$//m"').read()
    return 0 != len(buffer)


def do_smplayer_pause():
    os.system('smplayer -send-action pause_and_frame_step')

json_data = open('cities.json')
area_db = json.load(json_data)
json_data.close()

n = set()
while True:
    data = set(json.loads(
        urllib.request.urlopen(OREF_JSON_URL).read().decode("utf-16"))['data'])

    if data - n != set():
        cities = {}  # code to cities names
        for item in data:
            for city in item.split(','):
                city_name = re.sub("\d+", "", city).strip()
                code = re.sub("[^\d]+", "", city).strip()

                city_codes = cities.get(code, [])
                city_codes += area_db.get(city, [])
                cities[code] = city_codes

        if len(cities) > 0:
            beep()
            all_cities = [item for sublist in cities.values() for item in sublist]
            notify(', '.join(all_cities))
            #notify(', '.join(data - n))
            print(time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime()) + "\t" + ', '.join(data - n))

            if is_smplayer_running():
                do_smplayer_pause()

    n = data
    time.sleep(MINUTES_TO_WAIT)