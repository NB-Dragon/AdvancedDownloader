#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Create Time: 2021/5/1 10:00
# Create User: NB-Dragon
import os
import platform
import queue
import subprocess
import threading
from tools.RuntimeOperator import RuntimeOperator


class ActionOpenReceiver(threading.Thread):
    def __init__(self, runtime_operator: RuntimeOperator, parent_queue: queue.Queue):
        super().__init__()
        self._runtime_operator = runtime_operator
        self._parent_queue = parent_queue
        self._mission_dict = dict()
        self._message_queue = queue.Queue()
        self._run_status = True
        self._open_method = self._find_system_open_method()

    def run(self) -> None:
        while self._run_status or self._message_queue.qsize():
            message_dict = self._message_queue.get()
            if message_dict:
                self._handle_message_detail(message_dict["mission_uuid"], message_dict["detail"])
        self._do_with_mission_open(None)

    def get_message_queue(self):
        return self._message_queue

    def send_stop_state(self):
        self._run_status = False
        self._message_queue.put(None)

    def _handle_message_detail(self, mission_uuid, mission_detail):
        handle_type = mission_detail.pop("type")
        if handle_type == "open":
            self._do_with_mission_open(mission_uuid)
        elif handle_type == "register":
            self._do_with_mission_register(mission_uuid, mission_detail["path"])
        elif handle_type == "finish":
            self._do_with_mission_finish(mission_uuid)

    def _do_with_mission_open(self, mission_uuid):
        adapted_tips = "The current system is not yet adapted, please submit an issue if necessary."
        exception_tips = "Automatic opening failed, please install desktop system and set the default program."
        try:
            if self._open_method:
                file_path = self._get_mission_file_path(mission_uuid)
                self._open_method(file_path)
            else:
                self._make_message_and_send(mission_uuid, adapted_tips)
        except FileNotFoundError:
            self._make_message_and_send(mission_uuid, exception_tips)

    def _do_with_mission_register(self, mission_uuid, file_path):
        self._mission_dict[mission_uuid] = file_path

    def _do_with_mission_finish(self, mission_uuid):
        self._mission_dict.pop(mission_uuid)

    def _get_mission_file_path(self, mission_uuid):
        if mission_uuid:
            return self._mission_dict[mission_uuid]
        else:
            return self._runtime_operator.get_static_donate_image_path()

    def _find_system_open_method(self):
        current_platform = platform.system()
        if current_platform == "Linux":
            return self._open_in_linux
        elif current_platform == "Darwin":
            return self._open_in_mac
        elif current_platform == "Windows":
            return self._open_in_windows
        else:
            return None

    @staticmethod
    def _open_in_linux(file_path):
        subprocess.call(["xdg-open", file_path], stderr=subprocess.DEVNULL)

    @staticmethod
    def _open_in_mac(file_path):
        subprocess.call(["open", file_path], stderr=subprocess.DEVNULL)

    @staticmethod
    def _open_in_windows(file_path):
        os.startfile(file_path)

    def _make_message_and_send(self, mission_uuid: str, detail):
        if self._run_status:
            message_dict = dict()
            message_dict["action"] = "print"
            detail_info = {"sender": "ActionOpenReceiver", "content": detail, "exception": False}
            message_dict["value"] = {"mission_uuid": mission_uuid, "detail": detail_info}
            self._parent_queue.put(message_dict)
