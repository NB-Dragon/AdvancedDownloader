#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Create Time: 2022/01/01 00:00
# Create User: NB-Dragon
import queue
import threading
from module.analyzer.ResourceTool import ResourceTool


class ThreadAnalyzeModule(threading.Thread):
    def __init__(self, project_helper, switch_message):
        super().__init__()
        self._project_helper = project_helper
        self._switch_message = switch_message
        self._message_queue = queue.Queue()
        self._run_status = True
        self._init_module_tool()

    def run(self) -> None:
        while self._should_thread_continue_to_execute():
            message_dict = self._message_queue.get()
            if message_dict is None: continue
            message_type, message_detail = message_dict["message_type"], message_dict["message_detail"]
            self._handle_message_detail(message_dict["mission_uuid"], message_type, message_detail)

    def append_message(self, message):
        self._message_queue.put(message)

    def send_stop_state(self):
        self._run_status = False
        self.append_message(None)

    def _init_module_tool(self):
        self._module_tool = dict()
        self._module_tool["resource"] = ResourceTool(self._project_helper, self._switch_message)

    def _should_thread_continue_to_execute(self):
        return self._run_status or self._message_queue.qsize()

    def _handle_message_detail(self, mission_uuid, message_type, message_detail):
        if message_type == "analyze_request":
            self._do_with_analyze_request(mission_uuid, message_detail)
        else:
            abnormal_message = "Unknown message type of \"{}\"".format(message_type)
            self._send_universal_log(mission_uuid, "file", abnormal_message)

    def _do_with_analyze_request(self, mission_uuid, message_detail):
        response_detail = {"analyze_count": None, "mission_info": None, "download_info": None}
        download_info = self._module_tool["resource"].get_download_info(mission_uuid, message_detail["mission_info"])
        response_detail["analyze_count"] = message_detail["analyze_count"]
        response_detail["mission_info"] = message_detail["mission_info"]
        response_detail["download_info"] = download_info
        self._send_semantic_transform(mission_uuid, "analyze_response", response_detail)

    def _send_semantic_transform(self, mission_uuid, message_type, message_detail):
        message_dict = self._generate_action_signal_template("thread-transform")
        message_dict["value"] = self._generate_signal_value(mission_uuid, message_type, message_detail)
        self._switch_message.append_message(message_dict)

    def _send_universal_log(self, mission_uuid, message_type, content):
        message_dict = self._generate_action_signal_template("thread-log")
        message_detail = {"sender": "ThreadAnalyzeModule", "content": content}
        message_dict["value"] = self._generate_signal_value(mission_uuid, message_type, message_detail)
        self._switch_message.append_message(message_dict)

    @staticmethod
    def _generate_action_signal_template(receiver):
        return {"receiver": receiver, "value": {}}

    @staticmethod
    def _generate_signal_value(mission_uuid, message_type, message_detail) -> dict:
        return {"mission_uuid": mission_uuid, "message_type": message_type, "message_detail": message_detail}
