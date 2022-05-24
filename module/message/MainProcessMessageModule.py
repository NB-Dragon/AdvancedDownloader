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


class MainProcessMessageModule(threading.Thread):
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
            self._handle_all_kind_of_message(message_dict)
        self._do_before_message_down()
        self._stop_all_message()

    def get_message_queue(self):
        return self._message_queue

    def send_stop_message(self):
        stop_message = {"handle": "stop", "receiver": None, "content": None}
        self._message_queue.put(stop_message)

    def _init_all_module(self):
        self._all_module = dict()
        self._all_module["thread-log"] = ThreadLogModule(self._project_helper)
        self._all_module["thread-open"] = ThreadOpenModule(self._message_queue)
        self._all_module["thread-speed"] = ThreadSpeedModule(self._message_queue)
        self._all_module["thread-interact"] = ThreadInteractModule(self._message_queue)
        self._all_module["thread-analyze"] = ThreadAnalyzeModule(self._project_helper, self._message_queue)
        self._all_module["thread-archive"] = ThreadArchiveModule(self._project_helper, self._message_queue)
        self._all_module["thread-transform"] = ThreadTransformModule(self._project_helper, self._message_queue)
        self._all_module["thread-control"] = ThreadControlModule(self._project_helper, self._message_queue)

    def _start_all_module(self):
        for listener in self._all_module.values():
            listener.start()

    def _should_thread_continue_to_execute(self):
        return self._run_status or self._message_queue.qsize()

    def _handle_all_kind_of_message(self, message_dict):
        if message_dict["handle"] == "resend":
            message_receiver, message_content = message_dict["receiver"], message_dict["content"]
            self._handle_message_content(message_receiver, message_content)
        elif message_dict["handle"] == "stop":
            self._run_status = False
        else:
            abnormal_message = "Unknown handle type: {}".format(message_dict["handle"])
            self._send_universal_log(None, "file", abnormal_message)

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

    def _handle_message_content(self, message_receiver, message_content):
        if message_receiver in self._all_module:
            self._all_module[message_receiver].get_message_queue().put(message_content)
        else:
            abnormal_message = "Unknown receiver: {}".format(message_receiver)
            self._send_universal_log(None, "file", abnormal_message)

    def _send_universal_open(self, mission_uuid, message_type, message_detail):
        message_value = self._generate_execute_detail(mission_uuid, message_type, message_detail)
        self._all_module["thread-open"].get_message_queue().put(message_value)

    def _send_universal_log(self, mission_uuid, message_type, content):
        message_detail = {"sender": "MainProcessMessageModule", "content": content}
        message_value = self._generate_execute_detail(mission_uuid, message_type, message_detail)
        self._all_module["thread-log"].get_message_queue().put(message_value)

    @staticmethod
    def _generate_execute_detail(mission_uuid, message_type, message_detail) -> dict:
        signal_detail = {"mission_uuid": mission_uuid, "message_type": message_type, "message_detail": message_detail}
        return {"signal_type": "execute", "signal_detail": signal_detail}
