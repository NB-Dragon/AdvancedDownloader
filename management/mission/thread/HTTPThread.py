#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Create Time: 2021/8/01 10:00
# Create User: NB-Dragon
import threading
from core.decoder.HTTPHeaderAnalyzer import HTTPHeaderAnalyzer
from core.other.SectionMaker import SectionMaker
from tools.RuntimeOperator import RuntimeOperator


class HTTPThread(threading.Thread):
    def __init__(self, schema_name, mission_message_queue, runtime_operator: RuntimeOperator):
        super().__init__()
        self._schema_name = schema_name
        self._mission_message_queue = mission_message_queue
        self._section_maker = SectionMaker()
        self._http_header_analyzer = HTTPHeaderAnalyzer(runtime_operator)
        self._mission_uuid = None
        self._mission_info = None
        self._download_info = None
        self._run_status = True

    def init_mission_config(self, mission_uuid, mission_info, download_info):
        self._mission_uuid = mission_uuid
        self._mission_info = mission_info
        self._download_info = download_info

    def send_stop_state(self):
        self._run_status = False

    def start_download_mission(self):
        self._create_thread_for_section()
        self._track_thread_until_complete()
        self._return_download_message()

    def _return_download_message(self):
        section_list = self._get_all_section_list()
        if len(section_list):
            self._send_mission_progress_stop("passive")
        else:
            self._send_mission_progress_stop("initiative")

    def _get_all_section_list(self):
        result_list = []
        for file_item_detail in self._download_info["file_dict"].values():
            result_list.extend(file_item_detail["section"])
        return result_list

    def _send_mission_progress_stop(self, mission_status):
        self._send_mission_progress("stop", self._mission_uuid, {"reason": mission_status})

    def _send_mission_progress(self, signal_type, mission_uuid, mission_detail):
        message_dict = self._generate_action_signal_template("progress")
        message_dict["value"] = self._generate_signal_value(signal_type, mission_uuid, mission_detail)
        self._mission_message_queue.put(message_dict)

    @staticmethod
    def _generate_action_signal_template(receiver):
        return {"receiver": receiver, "value": None}

    @staticmethod
    def _generate_signal_value(signal_type, mission_uuid, mission_detail):
        return {"type": signal_type, "mission_uuid": mission_uuid, "detail": mission_detail}
