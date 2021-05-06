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
        self._open_method_dict = self._init_system_open_dict()
        self._command_installed = self._check_command_installed()

    def run(self) -> None:
        while self._run_status or self._message_queue.qsize():
            message_dict = self._message_queue.get()
            if message_dict is None: continue
            self._handle_message_detail(message_dict["mission_uuid"], message_dict["detail"])
        self._do_with_mission_open(None)

    def get_message_queue(self):
        return self._message_queue

    def is_command_installed(self):
        return self._command_installed

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
        current_platform = platform.system()
        if current_platform in self._open_method_dict:
            if self._command_installed:
                self._open_method_dict[current_platform](self._get_mission_file_path(mission_uuid))
            else:
                self._make_message_and_send(mission_uuid, exception_tips)
        else:
            self._make_message_and_send(mission_uuid, adapted_tips)

    def _check_command_installed(self):
        try:
            current_platform = platform.system()
            if current_platform in self._open_method_dict:
                if current_platform in ["Windows"]:
                    return True
                else:
                    self._open_method_dict[current_platform]("")
                    return True
            else:
                return False
        except FileNotFoundError:
            return False

    def _do_with_mission_register(self, mission_uuid, file_path):
        self._mission_dict[mission_uuid] = file_path

    def _do_with_mission_finish(self, mission_uuid):
        self._mission_dict.pop(mission_uuid)

    def _get_mission_file_path(self, mission_uuid):
        if mission_uuid:
            return self._mission_dict[mission_uuid]
        else:
            return self._runtime_operator.get_static_donate_image_path()

    def _init_system_open_dict(self):
        open_method_dict = dict()
        open_method_dict["Linux"] = self._open_in_linux
        open_method_dict["Darwin"] = self._open_in_mac
        open_method_dict["Windows"] = self._open_in_windows
        return open_method_dict

    @staticmethod
    def _open_in_linux(file_path):
        subprocess.call(["xdg-open", file_path], stderr=subprocess.DEVNULL, stdout=subprocess.DEVNULL)

    @staticmethod
    def _open_in_mac(file_path):
        subprocess.call(["open", file_path], stderr=subprocess.DEVNULL, stdout=subprocess.DEVNULL)

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
