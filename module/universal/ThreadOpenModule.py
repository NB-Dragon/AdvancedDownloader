#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Create Time: 2022/01/01 00:00
# Create User: NB-Dragon
import os
import platform
import queue
import subprocess
import threading


class ThreadOpenModule(threading.Thread):
    def __init__(self, switch_message):
        super().__init__()
        self._switch_message = switch_message
        self._message_queue = queue.Queue()
        self._run_status = True
        self._init_module_tool()

    def run(self) -> None:
        while self._should_thread_continue_to_execute():
            message_dict = self._message_queue.get()
            if message_dict is None: continue
            mission_uuid, message_type = message_dict["mission_uuid"], message_dict["message_type"]
            self._handle_message_detail(mission_uuid, message_type, message_dict["detail"])

    def append_message(self, message):
        self._message_queue.put(message)

    def is_command_installed(self):
        return self._module_tool["installed"]

    def send_stop_state(self):
        self._run_status = False
        self.append_message(None)

    def _init_module_tool(self):
        self._module_tool = dict()
        self._module_tool["method"] = self._combine_open_method()
        self._module_tool["installed"] = self._check_command_installed()

    def _should_thread_continue_to_execute(self):
        return self._run_status or self._message_queue.qsize()

    def _handle_message_detail(self, mission_uuid, message_type, message_detail):
        if message_type == "open":
            self._do_with_action_open(mission_uuid, message_detail["path"])
        else:
            abnormal_message = "Unknown message type of \"{}\"".format(message_type)
            self._send_universal_log(mission_uuid, "file", abnormal_message)

    def _do_with_action_open(self, mission_uuid, file_path):
        if os.path.exists(file_path):
            self._open_target_file(mission_uuid, file_path)
        else:
            abnormal_message = "File not found. Please start download first."
            self._send_universal_log(mission_uuid, "file", abnormal_message)

    def _open_target_file(self, mission_uuid, file_path):
        adapted_tips = "The current system is not yet adapted. Please open an issue if necessary."
        exception_tips = "Automatic opening failed. Please install desktop system and set the default program."
        current_platform = platform.system()
        if current_platform in self._module_tool["method"]:
            if self.is_command_installed():
                self._module_tool["method"][current_platform](file_path)
            else:
                self._send_universal_log(mission_uuid, "console", exception_tips)
        else:
            self._send_universal_log(mission_uuid, "console", adapted_tips)

    def _combine_open_method(self):
        return {"Linux": self._open_in_linux, "Darwin": self._open_in_mac, "Windows": self._open_in_windows}

    @staticmethod
    def _open_in_linux(file_path):
        subprocess.call(["xdg-open", file_path], stderr=subprocess.DEVNULL, stdout=subprocess.DEVNULL)

    @staticmethod
    def _open_in_mac(file_path):
        subprocess.call(["open", file_path], stderr=subprocess.DEVNULL, stdout=subprocess.DEVNULL)

    @staticmethod
    def _open_in_windows(file_path):
        os.startfile(file_path)

    def _check_command_installed(self):
        try:
            current_platform = platform.system()
            if current_platform in self._module_tool["method"]:
                if current_platform in ["Windows"]:
                    return True
                else:
                    self._module_tool["method"][current_platform]("")
                    return True
            else:
                return False
        except FileNotFoundError:
            return False

    def _send_universal_log(self, mission_uuid, message_type, content):
        message_dict = self._generate_action_signal_template("thread-log")
        message_detail = {"sender": "ThreadOpenModule", "content": content}
        message_dict["value"] = self._generate_signal_value(mission_uuid, message_type, message_detail)
        self._switch_message.append_message(message_dict)

    @staticmethod
    def _generate_action_signal_template(receiver):
        return {"receiver": receiver, "value": {}}

    @staticmethod
    def _generate_signal_value(mission_uuid, message_type, message_detail) -> dict:
        return {"mission_uuid": mission_uuid, "message_type": message_type, "detail": message_detail}
