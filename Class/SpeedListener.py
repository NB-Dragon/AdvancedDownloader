#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Create Time: 2020/2/20 17:10
# Create User: hya-machine
import os
import math
import time
import queue
import threading


class SpeedListener(threading.Thread):
    def __init__(self, message_receiver: queue.Queue):
        super().__init__()
        self._message_receiver = message_receiver
        self._mission_name = ""
        self._file_info_list = []
        self._run_status = True

    def set_mission_name(self, mission_name):
        self._mission_name = mission_name

    def set_listen_file_list(self, file_list):
        self._file_info_list = [{"file_name": file_name, "size": 0, "update_time": 0} for file_name in file_list]

    def run(self) -> None:
        start_time = time.time()
        self._calculate_download_size_change(start_time)
        while self._run_status:
            end_time = time.time()
            sum_time = end_time - start_time
            if sum_time >= 1:
                start_time = end_time
                speed_size = self._calculate_download_size_change(start_time)
                speed_description = self._get_format_file_size(speed_size)
                self._make_message_and_send(speed_description)

    def send_stop_state(self):
        self._run_status = False

    def _calculate_download_size_change(self, time_stamp):
        size_change_in_per_second = 0
        for file_name_item in self._file_info_list:
            try:
                current_size = os.path.getsize(file_name_item["file_name"])
                time_length = self._calculate_time_length(file_name_item["update_time"], time_stamp)
                size_length = current_size - file_name_item["size"]
                size_change_in_per_second += size_length // time_length
                file_name_item["size"] = current_size
                file_name_item["update_time"] = time_stamp
            except FileNotFoundError:
                self._make_message_and_send({"type": "文件出现读写冲突:{}".format(file_name_item["file_name"])})
            except Exception as e:
                self._make_message_and_send({"type": "文件异常", "info": e})
        return int(size_change_in_per_second)

    @staticmethod
    def _calculate_time_length(pre_time, now_time):
        return 1 if pre_time == 0 else now_time - pre_time

    @staticmethod
    def _get_format_file_size(size):
        units = ["B", "KB", "MB", "GB", "TB", "PB", "EB", "ZB", "YB", "BB", "NB", "DB", "CB"]
        if size > 0:
            unit_step = int(math.log2(size) // 10)
            format_size = size / (1 << unit_step * 10)
            return "{:.2f}{}/s".format(format_size, units[unit_step])
        else:
            return "{:.2f}{}/s".format(size, units[0])

    def _make_message_and_send(self, content):
        message = {"sender": "SpeedListener", "title": self._mission_name, "result": content}
        self._message_receiver.put(message)
