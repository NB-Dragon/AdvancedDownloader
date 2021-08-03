#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Create Time: 2021/1/25 10:00
# Create User: NB-Dragon
import os
import queue
import threading
from tools.RuntimeOperator import RuntimeOperator


class ActionWriterReceiver(threading.Thread):
    def __init__(self, runtime_operator: RuntimeOperator, parent_queue: queue.Queue):
        super().__init__()
        self._runtime_operator = runtime_operator
        self._message_queue = queue.Queue()
        self._run_status = True
        self._parent_queue = parent_queue
        self._mission_dict = dict()
        self._thread_lock_dict = dict()

    def run(self) -> None:
        while self._should_thread_continue_to_execute():
            message_dict = self._message_queue.get()
            if message_dict is None: continue
            signal_type, mission_uuid = message_dict["type"], message_dict["mission_uuid"]
            self._handle_message_detail(signal_type, mission_uuid, message_dict["detail"])

    def get_message_queue(self):
        return self._message_queue

    def send_stop_state(self):
        self._run_status = False
        self._message_queue.put(None)

    def _should_thread_continue_to_execute(self):
        return self._run_status or self._message_queue.qsize()

    def _handle_message_detail(self, signal_type, mission_uuid, message_detail):
        if signal_type == "write":
            content, length = message_detail["content"], len(message_detail["content"])
            self._send_speed_mission_size(mission_uuid, length)
            save_path, position = message_detail["save_path"], message_detail["position"]
            self._write_bytes_into_file(mission_uuid, save_path, position, content)
            self._send_info_write_down(mission_uuid, save_path, position, length)
        elif signal_type == "register":
            self._send_speed_mission_register(mission_uuid, message_detail["download_info"])
            self._do_with_mission_register(mission_uuid, message_detail["root_path"])
        elif signal_type == "finish":
            self._send_speed_mission_finish(mission_uuid)
            self._send_info_delete(mission_uuid, message_detail["delete_file"])
            self._do_with_mission_finish(mission_uuid)

    def _do_with_mission_register(self, mission_uuid, root_path):
        self._mission_dict[mission_uuid] = root_path

    def _do_with_mission_finish(self, mission_uuid):
        self._mission_dict.pop(mission_uuid)

    def _write_bytes_into_file(self, mission_uuid, save_path, position, content):
        sava_file_path = os.path.join(self._mission_dict[mission_uuid], save_path)
        writer = open(sava_file_path, 'r+b')
        writer.seek(position)
        writer.write(content)
        writer.close()

    def _send_speed_mission_size(self, mission_uuid, content_length):
        self._send_speed_mission_detail(mission_uuid, "size", {"length": content_length})

    def _send_speed_mission_register(self, mission_uuid, download_info):
        self._send_speed_mission_detail(mission_uuid, "register", {"download_info": download_info})

    def _send_speed_mission_finish(self, mission_uuid):
        self._send_speed_mission_detail(mission_uuid, "finish", None)

    def _send_speed_mission_detail(self, mission_uuid, message_type, detail):
        if self._run_status:
            signal_header = self._generate_action_signal_template("speed")
            signal_header["value"] = self._generate_signal_value(message_type, mission_uuid, detail)
            self._parent_queue.put(signal_header)

    def _send_info_write_down(self, mission_uuid, save_path, position, length):
        if self._run_status:
            signal_header = self._generate_action_signal_template("parent.mission.info")
            message_detail = {"sub_path": save_path, "position": position, "length": length}
            signal_header["value"] = self._generate_signal_value("update_section", mission_uuid, message_detail)

    def _send_info_delete(self, mission_uuid, delete_file: bool):
        if self._run_status:
            signal_header = self._generate_action_signal_template("parent.mission.info")
            message_detail = {"delete_file": delete_file}
            signal_header["value"] = self._generate_signal_value("delete", mission_uuid, message_detail)

    @staticmethod
    def _generate_action_signal_template(receiver):
        return {"action": "signal", "receiver": receiver, "value": None}

    @staticmethod
    def _generate_signal_value(signal_type, mission_uuid, mission_detail):
        return {"type": signal_type, "mission_uuid": mission_uuid, "detail": mission_detail}
