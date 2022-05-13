#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Create Time: 2022/03/01 20:00
# Create User: NB-Dragon
import queue
import threading
from module.analyzer.ThreadAnalyzeModule import ThreadAnalyzeModule
from module.archiver.ThreadArchiveModule import ThreadArchiveModule
from module.semantic.ThreadTransformModule import ThreadTransformModule
from module.universal.ThreadInteractModule import ThreadInteractModule
from module.universal.ThreadLogModule import ThreadLogModule
from module.universal.ThreadOpenModule import ThreadOpenModule
from module.universal.ThreadSpeedModule import ThreadSpeedModule
from module.worker.ThreadControlModule import ThreadControlModule


class ThreadMessageModule(threading.Thread):
    def __init__(self, project_helper):
        super().__init__()
        self._project_helper = project_helper
        self._message_queue = queue.Queue()
        self._run_status = True
        self._init_all_module()

    def run(self) -> None:
        self._start_all_module()
        while self._should_thread_continue_to_execute():
            message_dict = self._message_queue.get()
            print(message_dict)
            if message_dict is None: continue
            message_receiver, message_value = message_dict["receiver"], message_dict["value"]
            self._handle_message_value(message_receiver, message_value)
        self._do_before_message_down()
        self._stop_all_message()

    def append_message(self, message):
        self._message_queue.put(message)

    def send_stop_state(self):
        self._run_status = False
        self.append_message(None)

    def _init_all_module(self):
        self._all_module = dict()
        self._all_module["thread-interact"] = ThreadInteractModule(self)
        self._all_module["thread-log"] = ThreadLogModule(self._project_helper.get_project_path("log"))
        self._all_module["thread-open"] = ThreadOpenModule(self)
        self._all_module["thread-speed"] = ThreadSpeedModule(self)
        self._all_module["thread-analyze"] = ThreadAnalyzeModule(self._project_helper, self)
        self._all_module["thread-archive"] = ThreadArchiveModule(self._project_helper, self)
        self._all_module["thread-transform"] = ThreadTransformModule(self._project_helper, self)
        self._all_module["thread-control"] = ThreadControlModule(self._project_helper, self)

    def _should_thread_continue_to_execute(self):
        return self._run_status or self._message_queue.qsize()

    def _handle_message_value(self, message_receiver, message_value):
        if message_receiver in self._all_module:
            self._all_module[message_receiver].append_message(message_value)
        else:
            abnormal_message = "Unknown receiver of \"{}\"".format(message_receiver)
            self._send_universal_log(None, "file", abnormal_message)

    def _start_all_module(self):
        for listener in self._all_module.values():
            listener.start()

    def _do_before_message_down(self):
        donate_image_path = self._project_helper.get_static_donate_path()
        if self._all_module["thread-open"].is_command_installed():
            response_detail = {"path": donate_image_path}
            self._send_universal_open(None, "open", response_detail)
        else:
            message_content = "The sponsored QR code image path is: {}".format(donate_image_path)
            self._send_universal_log(None, "console", message_content)

    def _stop_all_message(self):
        for listener in self._all_module.values():
            listener.send_stop_state()

    def _send_universal_open(self, mission_uuid, message_type, message_detail):
        message_value = self._generate_signal_value(mission_uuid, message_type, message_detail)
        self._all_module["thread-open"].append_message(message_value)

    def _send_universal_log(self, mission_uuid, message_type, content):
        message_detail = {"sender": "ThreadMessageModule", "content": content}
        message_value = self._generate_signal_value(mission_uuid, message_type, message_detail)
        self._all_module["thread-log"].append_message(message_value)

    @staticmethod
    def _generate_signal_value(mission_uuid, message_type, message_detail) -> dict:
        return {"mission_uuid": mission_uuid, "message_type": message_type, "message_detail": message_detail}
