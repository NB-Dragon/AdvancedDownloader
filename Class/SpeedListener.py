#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Create Time: 2020/2/20 17:10
# Create User: hya-machine
import queue
import re
import os
import threading
import time


class SpeedListener(threading.Thread):
    def __init__(self, mission_name, file_list, message_receiver: queue.Queue):
        super().__init__()
        self._mission_name = mission_name
        self._file_list = file_list
        self._message_receiver = message_receiver
        self._file_filter = re.compile("\\.part\\d+$")
        self._run_status = True

    def run(self) -> None:
        start_time = time.time()
        start_position = self._calculate_current_download_size()
        while self._run_status:
            end_time = time.time()
            sum_time = end_time - start_time
            if sum_time >= 1:
                start_time = end_time
                end_position = self._calculate_current_download_size()
                speed_size = (end_position - start_position) // sum_time
                speed_description = self._get_format_file_size(speed_size)
                start_position = end_position
                self._make_message_and_send(speed_description)

    def send_stop_state(self):
        self._run_status = False

    def _calculate_current_download_size(self):
        current_size = 0
        for file_name in self._file_list:
            if os.path.exists(file_name):
                current_size += os.path.getsize(file_name)
            else:
                self._make_message_and_send("文件不存在：{}".format(file_name))
        return current_size

    def _make_message_and_send(self, content):
        message = {"sender": "SpeedListener", "title": self._mission_name, "result": content}
        self._message_receiver.put(message)

    @staticmethod
    def _get_format_file_size(size):
        units = ["B", "KB", "MB", "GB", "TB", "PB", "EB", "ZB", "YB", "BB", "NB", "DB", "CB"]
        unit_step = 0
        while size >= 1024:
            size /= 1024
            unit_step += 1
        return "{:.2f}{}/s".format(size, units[unit_step])
