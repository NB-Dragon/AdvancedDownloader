#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Create Time: 2021/5/16 12:00
# Create User: NB-Dragon
import queue
import threading
from schema.AnalyzeController import AnalyzeController
from tools.RuntimeOperator import RuntimeOperator


class ActionAnalyzeReceiver(threading.Thread):
    def __init__(self, runtime_operator: RuntimeOperator, parent_queue: queue.Queue):
        super().__init__()
        self._runtime_operator = runtime_operator
        self._message_queue = queue.Queue()
        self._run_status = True
        self._parent_queue = parent_queue
        self._analyze_controller = AnalyzeController(runtime_operator, parent_queue)

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
        if signal_type == "request":
            self._do_with_mission_analyze(mission_uuid, message_detail)

    def _do_with_mission_analyze(self, mission_uuid, message_detail):
        analyze_result = self._analyze_download_info(mission_uuid, message_detail)
        self._send_request_result(mission_uuid, analyze_result)

    def _analyze_download_info(self, mission_uuid, message_detail):
        result_dict = {"analyze_tag": message_detail["analyze_tag"], "download_info": None}
        schema, mission_info = message_detail["schema"], message_detail["download_info"]
        current_analyzer = self._analyze_controller.get_analyzer_by_schema(schema)
        download_info = current_analyzer.get_download_info(mission_uuid, mission_info)
        result_dict["download_info"] = download_info
        return result_dict

    def _send_request_result(self, mission_uuid, detail):
        if self._run_status:
            signal_header = self._generate_action_signal_template("parent.info")
            signal_header["value"] = self._generate_signal_value("request_result", mission_uuid, detail)
            self._parent_queue.put(signal_header)

    @staticmethod
    def _generate_action_signal_template(receiver):
        return {"action": "signal", "receiver": receiver, "value": None}

    @staticmethod
    def _generate_signal_value(signal_type, mission_uuid, mission_detail):
        return {"type": signal_type, "mission_uuid": mission_uuid, "detail": mission_detail}
