#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Create Time: 2021/5/16 12:00
# Create User: NB-Dragon
import queue
import threading
import urllib.parse
from manager.analyser.HTTPAnalyser import HTTPAnalyser
from tools.RuntimeOperator import RuntimeOperator


class MissionAnalyseReceiver(threading.Thread):
    def __init__(self, runtime_operator: RuntimeOperator, parent_queue: queue.Queue):
        super().__init__()
        self._runtime_operator = runtime_operator
        self._message_queue = queue.Queue()
        self._run_status = True
        self._parent_queue = parent_queue
        self._init_all_analyser()

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
        if signal_type == "analyse":
            analyse_result = self._analyse_download_info(mission_uuid, message_detail)
            self._send_mission_analyse_result(mission_uuid, analyse_result)

    def _analyse_download_info(self, mission_uuid, message_detail):
        mission_info = message_detail["mission_info"]
        link_parse_result = urllib.parse.urlparse(mission_info["download_link"])
        schema = link_parse_result.scheme
        result_dict = {"analyse_tag": message_detail["analyse_tag"] + 1, "analyse_result": None}
        if schema in self._all_analyser:
            download_info = self._all_analyser[schema].get_download_info(mission_info, mission_uuid)
            result_dict["analyse_result"] = download_info
        return result_dict

    def _init_all_analyser(self):
        self._all_analyser = dict()
        self._all_analyser["http"] = HTTPAnalyser("http", self._runtime_operator, self._parent_queue)
        self._all_analyser["https"] = HTTPAnalyser("https", self._runtime_operator, self._parent_queue)

    def _send_mission_analyse_result(self, mission_uuid: str, detail: dict):
        message_dict = {"action": "signal", "receiver": "mission_info", "value": None}
        message_detail = {"type": "analyse", "mission_uuid": mission_uuid, "detail": detail}
        message_dict["value"] = message_detail
        self._parent_queue.put(message_dict)
