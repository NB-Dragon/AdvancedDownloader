#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Create Time: 2020/2/20 17:10
# Create User: hya-machine
import queue
import os
import threading
import time


class SpeedListener(threading.Thread):
    def __init__(self, mission_name, file_list, message_receiver: queue.Queue):
        super().__init__()
        self._mission_name = mission_name
        self._file_list = file_list
        self._message_receiver = message_receiver
        self._run_status = True
        self._file_info_register = self._init_file_info_register()

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

    # noinspection PyBroadException
    def _calculate_download_size_change(self, time_stamp):
        size_change_in_per_second = 0
        for file_name_item in self._file_info_register:
            try:
                current_size = os.path.getsize(file_name_item["file_name"])
                time_length = self._calculate_time_length(file_name_item["update_time"], time_stamp)
                size_length = current_size - file_name_item["size"]
                size_change_in_per_second += size_length // time_length
                file_name_item["size"] = current_size
                file_name_item["update_time"] = time_stamp
            except Exception:
                self._make_message_and_send({"type": "文件出现读写冲突:{}".format(file_name_item["file_name"])})
        return size_change_in_per_second

    @staticmethod
    def _calculate_time_length(pre_time, now_time):
        return 1 if pre_time == 0 else now_time - pre_time

    def _init_file_info_register(self):
        file_info_list = []
        for file_name in self._file_list:
            temp_dict = {"file_name": file_name, "size": 0, "update_time": 0}
            file_info_list.append(temp_dict)
        return file_info_list

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
