#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Create Time: 2021/5/16 12:00
# Create User: NB-Dragon
import json
import os
import queue
import shutil
import threading
from tools.RuntimeOperator import RuntimeOperator


class MissionInfoReceiver(threading.Thread):
    def __init__(self, runtime_operator: RuntimeOperator, parent_queue: queue.Queue):
        super().__init__()
        self._runtime_operator = runtime_operator
        self._message_queue = queue.Queue()
        self._run_status = True
        self._parent_queue = parent_queue
        self._mission_info_dict = dict()

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
        if signal_type == "register":
            self._do_with_mission_register(mission_uuid, message_detail)
        elif signal_type == "update":
            self._do_with_mission_update(mission_uuid, message_detail)
        elif signal_type == "delete":
            self._do_with_mission_delete(mission_uuid, message_detail)
        elif signal_type == "open":
            self._do_with_mission_open(mission_uuid)
        elif signal_type == "data":
            self._do_with_mission_data(mission_uuid)
        elif signal_type == "request_result":
            self._do_with_mission_request_result(mission_uuid, message_detail)

    def _do_with_mission_register(self, mission_uuid, message_detail):
        if "mission_info" in message_detail and "download_info" in message_detail:
            mission_info, download_info = message_detail["mission_info"], message_detail["download_info"]
            self._mission_info_dict[mission_uuid] = dict()
            self._mission_info_dict[mission_uuid]["schema"] = message_detail["schema"]
            self._mission_info_dict[mission_uuid]["mission_info"] = self._get_standard_mission_info(mission_info)
            self._mission_info_dict[mission_uuid]["download_info"] = json.loads(json.dumps(download_info))

    def _do_with_mission_update(self, mission_uuid, message_detail):
        if mission_uuid in self._mission_info_dict:
            if "download_info" in message_detail:
                self._update_download_info(mission_uuid, message_detail["download_info"])
            if "mission_info" in message_detail:
                self._update_mission_info(mission_uuid, message_detail["mission_info"])

    def _do_with_mission_delete(self, mission_uuid, message_detail):
        if mission_uuid in self._mission_info_dict:
            if message_detail["delete_file"]:
                self._delete_file_or_directory(mission_uuid)
            self._mission_info_dict.pop(mission_uuid)

    def _do_with_mission_open(self, mission_uuid):
        if mission_uuid in self._mission_info_dict:
            if self._mission_info_dict[mission_uuid]["download_info"]:
                old_save_path = self._mission_info_dict[mission_uuid]["mission_info"]["save_path"]
                old_full_path = self._get_current_full_save_path(mission_uuid, old_save_path)
                self._send_open_message("open", mission_uuid, {"path": old_full_path})

    def _do_with_mission_data(self, mission_uuid):
        if mission_uuid in self._mission_info_dict:
            if self._mission_info_dict[mission_uuid]["download_info"] is None:
                self._request_mission_analyze(mission_uuid, 1)
            else:
                self._send_thread_action("data_result", mission_uuid, self._mission_info_dict[mission_uuid])

    def _do_with_mission_request_result(self, mission_uuid, message_detail):
        if mission_uuid in self._mission_info_dict:
            if message_detail["download_info"]:
                self._update_download_info(mission_uuid, message_detail["download_info"])
            if message_detail["download_info"] is None and message_detail["analyze_tag"] < 3:
                self._request_mission_analyze(mission_uuid, message_detail["analyze_tag"] + 1)
            else:
                self._send_thread_action("data_result", mission_uuid, self._mission_info_dict[mission_uuid])

    def _get_standard_mission_info(self, mission_info):
        standard_mission_info = self._generate_default_mission_info()
        for key, value in mission_info.items():
            if key in standard_mission_info:
                standard_mission_info[key] = value
        return standard_mission_info

    def _update_mission_info(self, mission_uuid, mission_info: dict):
        if "save_path" in mission_info:
            self._rename_file_or_directory(mission_uuid, mission_info["save_path"])
        for key, value in mission_info.items():
            if key in self._mission_info_dict[mission_uuid]:
                self._mission_info_dict[mission_uuid][key] = value

    def _update_download_info(self, mission_uuid, download_info: dict):
        regenerate_download_info = json.loads(json.dumps(download_info))
        self._mission_info_dict[mission_uuid]["download_info"] = regenerate_download_info

    def _delete_file_or_directory(self, mission_uuid):
        if self._mission_info_dict[mission_uuid]["download_info"]:
            save_path = self._mission_info_dict[mission_uuid]["mission_info"]["save_path"]
            old_full_path = self._get_current_full_save_path(mission_uuid, save_path)
            if os.path.exists(old_full_path):
                shutil.rmtree(old_full_path)

    def _rename_file_or_directory(self, mission_uuid, new_path):
        if self._mission_info_dict[mission_uuid]["download_info"]:
            old_save_path = self._mission_info_dict[mission_uuid]["mission_info"]["save_path"]
            old_full_path = self._get_current_full_save_path(mission_uuid, old_save_path)
            new_full_path = self._get_current_full_save_path(mission_uuid, new_path)
            os.rename(old_full_path, new_full_path)

    def _get_current_full_save_path(self, mission_uuid, save_path):
        file_name = self._mission_info_dict[mission_uuid]["download_info"]["filename"]
        return os.path.join(save_path, file_name)

    def _request_mission_analyze(self, mission_uuid, analyze_tag):
        mission_info = self._mission_info_dict[mission_uuid]["mission_info"]
        mission_schema = self._mission_info_dict[mission_uuid]["schema"]
        analyze_item = {"schema": mission_schema, "analyze_tag": analyze_tag, "mission_info": mission_info}
        self._send_analyze_action("request", mission_uuid, analyze_item)

    def _generate_default_mission_info(self):
        standard_mission_info = dict()
        standard_mission_info["download_link"] = None
        standard_mission_info["save_path"] = self._runtime_operator.get_code_entrance_path()
        standard_mission_info["thread_num"] = 1
        standard_mission_info["headers"] = None
        standard_mission_info["proxy"] = None
        standard_mission_info["open_after_finish"] = False
        return standard_mission_info

    def _send_analyze_action(self, signal_type, mission_uuid, mission_detail):
        message_dict = self._generate_action_signal_template("message.analyze")
        message_dict["value"] = self._generate_signal_value(signal_type, mission_uuid, mission_detail)
        self._parent_queue.put(message_dict)

    def _send_open_message(self, signal_type, mission_uuid, mission_detail):
        message_dict = self._generate_action_signal_template("message.open")
        message_dict["value"] = self._generate_signal_value(signal_type, mission_uuid, mission_detail)
        self._parent_queue.put(message_dict)

    def _send_thread_action(self, signal_type, mission_uuid, mission_detail):
        message_dict = self._generate_action_signal_template("thread")
        message_dict["value"] = self._generate_signal_value(signal_type, mission_uuid, mission_detail)
        self._parent_queue.put(message_dict)

    @staticmethod
    def _generate_action_signal_template(receiver):
        return {"action": "signal", "receiver": receiver, "value": None}

    @staticmethod
    def _generate_signal_value(signal_type, mission_uuid, mission_detail):
        return {"type": signal_type, "mission_uuid": mission_uuid, "detail": mission_detail}
