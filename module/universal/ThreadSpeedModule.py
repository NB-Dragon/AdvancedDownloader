#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Create Time: 2022/01/01 00:00
# Create User: NB-Dragon
import queue
import threading
import time
from network.NetworkTrafficHelper import NetworkTrafficHelper


class ThreadSpeedModule(threading.Thread):
    def __init__(self, switch_message):
        super().__init__()
        self._switch_message = switch_message
        self._message_queue = queue.Queue()
        self._run_status = True
        self._init_module_tool()
        self._mission_dict = dict()
        self._start_time = None
        self._end_time = None

    def run(self) -> None:
        self._update_start_time()
        while self._should_thread_continue_to_execute():
            message_dict = self._message_queue.get()
            if message_dict is None: continue
            message_type, message_detail = message_dict["message_type"], message_dict["message_detail"]
            self._handle_message_detail(message_dict["mission_uuid"], message_type, message_detail)
            self._broadcast_speed_content()

    def append_message(self, message):
        self._message_queue.put(message)

    def send_stop_state(self):
        self._run_status = False
        self.append_message(None)

    def _init_module_tool(self):
        self._module_tool = dict()
        self._module_tool["traffic"] = NetworkTrafficHelper()

    def _should_thread_continue_to_execute(self):
        return self._run_status or self._message_queue.qsize()

    def _handle_message_detail(self, mission_uuid, message_type, message_detail):
        if message_type == "register":
            self._do_with_action_register(mission_uuid, message_detail)
        elif message_type == "change":
            self._do_with_action_change(mission_uuid, message_detail)
        elif message_type == "delete":
            self._do_with_action_delete(mission_uuid, message_detail)
        else:
            abnormal_message = "Unknown message type of \"{}\"".format(message_type)
            self._send_universal_log(mission_uuid, "file", abnormal_message)

    def _do_with_action_register(self, mission_uuid, message_detail):
        mission_item = {"update_size": 0, "current_size": 0, "expect_size": 0}
        download_info = message_detail["download_info"]
        section_info = download_info["section_info"]
        mission_item["current_size"] = self._module_tool["traffic"].get_current_finish_size(section_info)
        mission_item["expect_size"] = download_info["total_size"]
        self._mission_dict[mission_uuid] = mission_item

    def _do_with_action_change(self, mission_uuid, message_detail):
        if mission_uuid in self._mission_dict:
            length = message_detail["size"]
            self._mission_dict[mission_uuid]["update_size"] += length
            self._mission_dict[mission_uuid]["current_size"] += length

    def _do_with_action_delete(self, mission_uuid, message_detail):
        if mission_uuid in self._mission_dict:
            self._mission_dict.pop(mission_uuid)

    def _broadcast_speed_content(self):
        self._update_end_time()
        speed_and_progress_list = self._generate_speed_and_progress()
        for speed_and_progress_item in speed_and_progress_list:
            mission_uuid = speed_and_progress_item.pop("mission_uuid")
            self._send_universal_log(mission_uuid, "console", speed_and_progress_item)

    def _generate_speed_and_progress(self):
        current_time_length = self._get_time_length()
        if current_time_length >= 1:
            self._update_start_time()
            return self._module_tool["traffic"].get_speed_and_progress(self._mission_dict, current_time_length)
        else:
            return []

    def _update_start_time(self):
        self._start_time = time.time()

    def _update_end_time(self):
        self._end_time = time.time()

    def _get_time_length(self):
        if isinstance(self._start_time, float) and isinstance(self._end_time, float):
            return self._end_time - self._start_time
        else:
            return 0

    def _send_universal_log(self, mission_uuid, message_type, content):
        message_dict = self._generate_action_signal_template("thread-log")
        message_detail = {"sender": "ThreadSpeedModule", "content": content}
        message_dict["value"] = self._generate_signal_value(mission_uuid, message_type, message_detail)
        self._switch_message.append_message(message_dict)

    @staticmethod
    def _generate_action_signal_template(receiver):
        return {"receiver": receiver, "value": {}}

    @staticmethod
    def _generate_signal_value(mission_uuid, message_type, message_detail) -> dict:
        return {"mission_uuid": mission_uuid, "message_type": message_type, "message_detail": message_detail}
