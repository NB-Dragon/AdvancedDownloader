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
            self._handle_all_kind_of_message(message_dict)

    def is_command_installed(self):
        return self._module_tool["installed"]

    def get_message_queue(self):
        return self._message_queue

    def send_stop_state(self):
        stop_message = {"signal_type": "stop", "signal_detail": None}
        self._message_queue.put(stop_message)

    def _apply_forward_message(self, response_message):
        self._switch_message.put(response_message)

    def _init_module_tool(self):
        self._module_tool = dict()
        self._module_tool["method"] = self._combine_open_method()
        self._module_tool["installed"] = self._check_command_installed()

    def _should_thread_continue_to_execute(self):
        return self._run_status or self._message_queue.qsize()

    def _handle_all_kind_of_message(self, message_dict):
        signal_type, signal_detail = message_dict["signal_type"], message_dict["signal_detail"]
        if signal_type == "execute":
            message_type, message_detail = signal_detail["message_type"], signal_detail["message_detail"]
            self._handle_message_detail(signal_detail["mission_uuid"], message_type, message_detail)
        elif signal_type == "stop":
            self._run_status = False
        else:
            abnormal_message = "Unknown signal type: {}".format(signal_type)
            self._send_universal_log(None, "file", abnormal_message)

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
        message_dict = self._generate_signal_template("thread-log")
        message_detail = {"sender": "ThreadOpenModule", "content": content}
        message_dict["content"] = self._generate_execute_detail(mission_uuid, message_type, message_detail)
        self._apply_forward_message(message_dict)

    @staticmethod
    def _generate_signal_template(receiver):
        return {"handle": "resend", "receiver": receiver, "content": {}}

    @staticmethod
    def _generate_execute_detail(mission_uuid, message_type, message_detail) -> dict:
        signal_detail = {"mission_uuid": mission_uuid, "message_type": message_type, "message_detail": message_detail}
        return {"signal_type": "execute", "signal_detail": signal_detail}
