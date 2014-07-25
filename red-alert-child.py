#!/bin/python3
# Created by Yakir Sitbon <http://www.yakirs.net/>

import os
import main


class RedAlertNotificationChild(main.RedAlertNotification):
    def is_smplayer_running(self):
        buffer = os.popen('ps -eo pcpu,pid,user,comm | grep -i "smplayer"$ | sed  "s/ smplayer$//m"').read()
        return 0 != len(buffer)

    def do_smplayer_pause(self):
        os.system('smplayer -send-action pause_and_frame_step')

    def on_alert(self):
        if self.is_smplayer_running():
            self.do_smplayer_pause()

if __name__ == "__main__":
    instance = RedAlertNotificationChild()
    instance.main_loop()