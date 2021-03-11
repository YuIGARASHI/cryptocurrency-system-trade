# -*- coding: utf-8 -*-

import logging
import os
import datetime
import sys
import time
from pytz import timezone
from line_handler import LineHandler


class Logger:
    def __init__(self):
        self.log_dir = "../logs"
        self.line_handler = LineHandler()

    def write_log(self, text):
        text = str(text)
        date_obj = datetime.datetime.now(timezone('Asia/Tokyo'))
        date_str = date_obj.strftime("%Y-%m-%d")
        file_path = self.log_dir + "/" + date_str + ".log"
        try:
            with open(file_path, "a") as f:
                f.write(date_obj.strftime("%Y/%m/%d %H:%M:%S") + "\t" + text + "\n")
                print(date_obj.strftime("%Y/%m/%d %H:%M:%S") + "\t" + text)
                self.line_handler.post_to_igarashi339(text)
        except:
            print("error:ログファイルへのアクセスに失敗しました。")
            sys.exit()


if __name__ == "__main__":
    logger = Logger()
    for i in range(10):
        logger.write_log("テスト")
        time.sleep(2)