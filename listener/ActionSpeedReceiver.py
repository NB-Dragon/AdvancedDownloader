#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Create Time: 2021/1/25 10:00
# Create User: NB-Dragon
import math
import time
import queue
import threading
from tool.RuntimeOperator import RuntimeOperator


class ActionSpeedReceiver(threading.Thread):
    def __init__(self, runtime_operator: RuntimeOperator, parent_queue: queue.Queue):
        super().__init__()
        self._runtime_operator = runtime_operator
        self._parent_queue = parent_queue
        self._mission_dict = dict()
        self._message_queue = queue.Queue()
        self._run_status = True
        self._start_time = 0

    def run(self) -> None:
        self._start_time = time.time()
        while self._run_status or self._message_queue.qsize():
            message_dict = self._message_queue.get()
            # {"mission_uuid": str, "detail": Any}
            if message_dict:
                self._handle_message_detail(message_dict["mission_uuid"], message_dict["detail"])
            self._broadcast_speed_content()

    def get_message_queue(self):
        return self._message_queue

    def send_stop_state(self):
        self._run_status = False
        self._message_queue.put(None)

    def _handle_message_detail(self, mission_uuid, mission_detail):
        handle_type = mission_detail.pop("type")
        if handle_type == "size":
            # mission_detail = {"type": "size", "length": int}
            self._do_with_mission_size(mission_uuid, mission_detail["length"])
        elif handle_type == "register":
            # mission_detail = {"type": "register", "download_info": dict}
            self._do_with_mission_register(mission_uuid, mission_detail["download_info"])
        elif handle_type == "finish":
            # mission_detail = {"type": "finish"}
            self._do_with_mission_finish(mission_uuid)

    def _do_with_mission_size(self, mission_uuid, length):
        self._mission_dict[mission_uuid]["update_size"] += length
        self._mission_dict[mission_uuid]["current_size"] += length

    def _do_with_mission_register(self, mission_uuid, download_info):
        mission_item = dict()
        mission_item["update_size"] = 0
        mission_item["current_size"] = self._calc_finish_file_size(download_info)
        mission_item["expect_size"] = download_info["file_info"]["filesize"]
        self._mission_dict[mission_uuid] = mission_item
        if len(self._mission_dict) == 1:
            self._start_time = time.time()

    def _do_with_mission_finish(self, mission_uuid):
        self._mission_dict.pop(mission_uuid)

    @staticmethod
    def _calc_finish_file_size(download_info):
        if download_info["file_info"]["range"] is False:
            return 0
        else:
            incomplete_size = sum([x[1] - x[0] + 1 for x in download_info["all_region"]])
            return download_info["file_info"]["filesize"] - incomplete_size

    def _broadcast_speed_content(self):
        end_time = time.time()
        if end_time - self._start_time >= 1:
            speed_and_progress_list = self._generate_mission_speed_and_progress(self._start_time, end_time)
            for speed_info_item in speed_and_progress_list:
                mission_uuid = speed_info_item.pop("mission_uuid")
                self._send_speed_info(mission_uuid, speed_info_item)
            self._start_time = time.time()

    def _generate_mission_speed_and_progress(self, start_time, end_time):
        speed_content_list = []
        for mission_uuid in self._mission_dict.keys():
            mission_item = self._mission_dict[mission_uuid]
            progress = self._get_progress_description(mission_item["current_size"], mission_item["expect_size"])
            speed = self._get_speed_description(mission_item["update_size"], start_time, end_time)
            result_item = {"mission_uuid": mission_uuid, "progress": progress, "speed": speed}
            speed_content_list.append(result_item)
            mission_item["update_size"] = 0
        return speed_content_list

    @staticmethod
    def _get_progress_description(current_size, expect_size):
        return "{:.2f}%".format(current_size / expect_size * 100) if expect_size else "unknown"

    def _get_speed_description(self, update_size, start_time, end_time):
        update_size_in_per_second = int(update_size // (end_time - start_time))
        return self._get_format_file_size(update_size_in_per_second)

    @staticmethod
    def _get_format_file_size(size):
        units = ["B", "KB", "MB", "GB", "TB", "PB", "EB", "ZB", "YB", "BB", "NB", "DB", "CB"]
        if size > 0:
            unit_step = int(math.log2(size) // 10)
            format_size = size / (1 << unit_step * 10)
            return "{:.2f}{}/s".format(format_size, units[unit_step])
        else:
            return "{:.2f}{}/s".format(size, units[0])

    def _send_speed_info(self, mission_uuid: str, detail: dict):
        message_dict = dict()
        message_dict["action"] = "print"
        detail_info = {"sender": "ActionSpeedReceiver", "content": detail, "exception": False}
        message_dict["value"] = {"mission_uuid": mission_uuid, "detail": detail_info}
        self._parent_queue.put(message_dict)
