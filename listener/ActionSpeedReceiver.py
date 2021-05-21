#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Create Time: 2021/1/25 10:00
# Create User: NB-Dragon
import math
import queue
import threading
import time
from controller.AnalyzeController import AnalyzeController
from tools.RuntimeOperator import RuntimeOperator


class ActionSpeedReceiver(threading.Thread):
    def __init__(self, runtime_operator: RuntimeOperator, parent_queue: queue.Queue):
        super().__init__()
        self._runtime_operator = runtime_operator
        self._message_queue = queue.Queue()
        self._run_status = True
        self._parent_queue = parent_queue
        self._analyze_controller = AnalyzeController(runtime_operator, parent_queue)
        self._mission_dict = dict()
        self._start_time = 0

    def run(self) -> None:
        self._start_time = time.time()
        while self._should_thread_continue_to_execute():
            message_dict = self._message_queue.get()
            if message_dict is None: continue
            signal_type, mission_uuid = message_dict["type"], message_dict["mission_uuid"]
            self._handle_message_detail(signal_type, mission_uuid, message_dict["detail"])
            self._broadcast_speed_content()

    def get_message_queue(self):
        return self._message_queue

    def send_stop_state(self):
        self._run_status = False
        self._message_queue.put(None)

    def _should_thread_continue_to_execute(self):
        return self._run_status or self._message_queue.qsize()

    def _handle_message_detail(self, signal_type, mission_uuid, message_detail):
        if signal_type == "size":
            self._do_with_mission_size(mission_uuid, message_detail)
        elif signal_type == "register":
            self._do_with_mission_register(mission_uuid, message_detail)
        elif signal_type == "finish":
            self._do_with_mission_finish(mission_uuid)

    def _do_with_mission_size(self, mission_uuid, message_detail):
        length = message_detail["length"]
        self._mission_dict[mission_uuid]["update_size"] += length
        self._mission_dict[mission_uuid]["current_size"] += length

    def _do_with_mission_register(self, mission_uuid, message_detail):
        mission_item = {"start_time": time.time(), "update_size": 0, "current_size": 0, "expect_size": 0}
        schema, download_info = message_detail["schema"], message_detail["download_info"]
        schema_analyzer = self._analyze_controller.get_analyzer(schema)
        mission_item["current_size"] = schema_analyzer.get_current_finish_size(download_info)
        mission_item["expect_size"] = download_info["filesize"]
        self._mission_dict[mission_uuid] = mission_item

    def _do_with_mission_finish(self, mission_uuid):
        self._mission_dict.pop(mission_uuid)

    def _broadcast_speed_content(self):
        end_time = time.time()
        if end_time - self._start_time >= 1:
            speed_and_progress_list = self._generate_mission_speed_and_progress(end_time)
            for speed_info_item in speed_and_progress_list:
                mission_uuid = speed_info_item.pop("mission_uuid")
                self._make_message_and_send(mission_uuid, speed_info_item)
            self._start_time = time.time()
            for mission_uuid in self._mission_dict.keys():
                self._mission_dict[mission_uuid]["update_size"] = 0
                self._mission_dict[mission_uuid]["start_time"] = self._start_time

    def _generate_mission_speed_and_progress(self, end_time):
        speed_content_list = []
        for mission_uuid in self._mission_dict.keys():
            mission_item = self._mission_dict[mission_uuid]
            progress = self._get_progress_description(mission_item["current_size"], mission_item["expect_size"])
            speed = self._get_speed_description(mission_item["update_size"], mission_item["start_time"], end_time)
            result_item = {"mission_uuid": mission_uuid, "progress": progress, "speed": speed}
            speed_content_list.append(result_item)
        return speed_content_list

    @staticmethod
    def _get_progress_description(current_size, expect_size):
        return "{:.2f}%".format(current_size / expect_size * 100) if expect_size else "unknown"

    def _get_speed_description(self, update_size, start_time, end_time):
        time_interval = end_time - start_time
        update_size_in_per_second = int(update_size // time_interval) if time_interval else 0
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

    def _make_message_and_send(self, mission_uuid: str, detail):
        if self._run_status:
            signal_header = self._generate_action_signal_template("print")
            signal_header["value"] = self._generate_print_value(mission_uuid, detail, False)
            self._parent_queue.put(signal_header)

    @staticmethod
    def _generate_action_signal_template(receiver):
        return {"action": "signal", "receiver": receiver, "value": None}

    @staticmethod
    def _generate_print_value(mission_uuid, content, exception: bool):
        message_type = "exception" if exception else "normal"
        message_detail = {"sender": "ActionSpeedReceiver", "content": content}
        return {"type": message_type, "mission_uuid": mission_uuid, "detail": message_detail}
