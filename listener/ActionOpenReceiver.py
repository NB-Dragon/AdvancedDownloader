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
        self._message_queue = queue.Queue()
        self._run_status = True
        self._parent_queue = parent_queue
        self._open_method_dict = self._init_system_open_dict()
        self._command_installed = self._check_command_installed()

    def run(self) -> None:
        while self._should_thread_continue_to_execute():
            message_dict = self._message_queue.get()
            if message_dict is None: continue
            self._handle_message_detail(message_dict["detail"])
        self._open_target_file(self._runtime_operator.get_static_donate_image_path())

    def get_message_queue(self):
        return self._message_queue

    def is_command_installed(self):
        return self._command_installed

    def send_stop_state(self):
        self._run_status = False
        self._message_queue.put(None)

    def _should_thread_continue_to_execute(self):
        return self._run_status or self._message_queue.qsize()

    def _handle_message_detail(self, mission_detail):
        handle_type = mission_detail.pop("type")
        if handle_type == "open":
            self._do_with_mission_open(mission_detail["path"])

    def _do_with_mission_open(self, file_path):
        if os.path.exists(file_path):
            self._open_target_file(file_path)
        else:
            file_tips = "File not found. Please start download first."
            self._make_message_and_send(file_tips)

    def _open_target_file(self, file_path):
        adapted_tips = "The current system is not yet adapted. Please open an issue if necessary."
        exception_tips = "Automatic opening failed. Please install desktop system and set the default program."
        current_platform = platform.system()
        if current_platform in self._open_method_dict:
            if self._command_installed:
                self._open_method_dict[current_platform](file_path)
            else:
                self._make_message_and_send(exception_tips)
        else:
            self._make_message_and_send(adapted_tips)

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

    def _make_message_and_send(self, detail):
        if self._run_status:
            message_dict = dict()
            message_dict["action"] = "print"
            detail_info = {"sender": "ActionOpenReceiver", "content": detail, "exception": False}
            message_dict["value"] = {"mission_uuid": None, "detail": detail_info}
            self._parent_queue.put(message_dict)
