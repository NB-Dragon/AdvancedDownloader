#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Create Time: 2021/5/16 12:00
# Create User: NB-Dragon
import json
import os
import queue
import shutil
import threading
import urllib.parse
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
            self._update_mission_progress()

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
        elif signal_type == "delete":
            self._do_with_mission_delete(mission_uuid, message_detail)
        elif signal_type == "open":
            self._do_with_mission_open(mission_uuid, message_detail)
        elif signal_type == "update_mission_config":
            self._do_with_mission_update_mission_config(mission_uuid, message_detail)
        elif signal_type == "update_download_name":
            self._do_with_mission_update_download_name(mission_uuid, message_detail)
        elif signal_type == "update_section":
            self._do_with_mission_update_section(mission_uuid, message_detail)
        elif signal_type == "request":
            self._do_with_mission_request(mission_uuid)
        elif signal_type == "request_result":
            self._do_with_mission_request_result(mission_uuid, message_detail)

    def _do_with_mission_register(self, mission_uuid, message_detail):
        if "mission_info" in message_detail and "download_info" in message_detail:
            mission_info, download_info = message_detail["mission_info"], message_detail["download_info"]
            if mission_info.get("download_link"):
                self._mission_info_dict[mission_uuid] = dict()
                self._mission_info_dict[mission_uuid]["schema"] = message_detail["schema"]
                self._mission_info_dict[mission_uuid]["mission_info"] = self._get_standard_mission_info(mission_info)
                self._mission_info_dict[mission_uuid]["download_info"] = json.loads(json.dumps(download_info))

    def _do_with_mission_delete(self, mission_uuid, message_detail):
        if mission_uuid in self._mission_info_dict:
            if message_detail["delete_file"]:
                self._delete_file_or_directory(mission_uuid)
            self._mission_info_dict.pop(mission_uuid)

    def _do_with_mission_open(self, mission_uuid, message_detail):
        if mission_uuid in self._mission_info_dict:
            if self._mission_info_dict[mission_uuid]["download_info"]:
                old_save_path = self._get_target_save_path(mission_uuid, message_detail["sub_path"])
                self._send_open_message("open", mission_uuid, {"path": old_save_path})

    def _do_with_mission_update_mission_config(self, mission_uuid, message_detail):
        if mission_uuid in self._mission_info_dict:
            if "save_path" in message_detail["mission_info"]:
                download_root_path = self._get_download_root_path(mission_uuid)
                old_save_path = self._get_target_save_path(mission_uuid, download_root_path)
                new_save_path = os.path.join(message_detail["mission_info"]["save_path"], download_root_path)
                if os.path.exists(old_save_path):
                    self._rename_file(mission_uuid, old_save_path, new_save_path)
            for key, value in message_detail["mission_info"].items():
                if key in self._mission_info_dict[mission_uuid]["mission_info"]:
                    self._mission_info_dict[mission_uuid]["mission_info"][key] = value

    def _do_with_mission_update_download_name(self, mission_uuid, message_detail):
        if mission_uuid in self._mission_info_dict:
            if self._mission_info_dict[mission_uuid]["download_info"]:
                sub_path, target_path = message_detail["sub_path"], message_detail["target_path"]
                self._rename_file_or_directory(mission_uuid, sub_path, target_path)
                self._update_download_info_sub_path(mission_uuid, sub_path, target_path)

    def _do_with_mission_update_section(self, mission_uuid, message_detail):
        if mission_uuid in self._mission_info_dict:
            if self._mission_info_dict[mission_uuid]["download_info"]:
                start_position, length = message_detail["start_position"], message_detail["length"]
                self._update_download_section(mission_uuid, message_detail["sub_path"], start_position, length)

    def _do_with_mission_request(self, mission_uuid):
        if mission_uuid in self._mission_info_dict:
            if self._mission_info_dict[mission_uuid]["download_info"]:
                self._send_thread_action("request_result", mission_uuid, self._mission_info_dict[mission_uuid])
            else:
                self._request_mission_analyze(mission_uuid, 1)

    def _do_with_mission_request_result(self, mission_uuid, message_detail):
        if mission_uuid in self._mission_info_dict:
            if message_detail["download_info"]:
                self._mission_info_dict[mission_uuid]["download_info"] = message_detail["download_info"]
            if message_detail["download_info"] or message_detail["analyze_tag"] == 3:
                self._send_thread_action("request_result", mission_uuid, self._mission_info_dict[mission_uuid])
            else:
                self._request_mission_analyze(mission_uuid, message_detail["analyze_tag"] + 1)

    def _update_mission_progress(self):
        self._runtime_operator.set_mission_state(self._mission_info_dict)

    def _get_standard_mission_info(self, mission_info):
        standard_mission_info = self._generate_default_mission_info()
        for key, value in mission_info.items():
            if key in standard_mission_info:
                standard_mission_info[key] = value
        quote_link = self._get_url_after_quote(standard_mission_info["download_link"])
        standard_mission_info["download_link"] = quote_link
        return standard_mission_info

    def _delete_file_or_directory(self, mission_uuid):
        if self._mission_info_dict[mission_uuid]["download_info"]:
            download_root_path = self._get_download_root_path(mission_uuid)
            old_save_path = self._get_target_save_path(mission_uuid, download_root_path)
            if os.path.isdir(old_save_path):
                shutil.rmtree(old_save_path)
            elif os.path.exists(old_save_path):
                os.remove(old_save_path)

    def _rename_file_or_directory(self, mission_uuid, sub_path, target_path):
        old_save_path = self._get_target_save_path(mission_uuid, sub_path)
        new_save_path = self._get_target_save_path(mission_uuid, target_path)
        if os.path.exists(old_save_path):
            self._rename_file(mission_uuid, old_save_path, new_save_path)

    def _update_download_info_sub_path(self, mission_uuid, sub_path, target_path):
        download_info_file_dict = self._mission_info_dict[mission_uuid]["download_info"]["file_dict"]
        for relative_path in download_info_file_dict.keys():
            if relative_path.startswith(sub_path):
                new_path = "{}{}".format(target_path, relative_path.split(sub_path, 1)[1])
                download_info_file_dict[new_path] = download_info_file_dict.pop(relative_path)

    def _update_download_section(self, mission_uuid, sub_path, start_position, length):
        download_info = self._mission_info_dict[mission_uuid]["download_info"]
        current_file_section = download_info["file_dict"][sub_path]["section"]
        match_section = self._pop_match_section(start_position, current_file_section)
        match_section[0] += length
        if len(match_section) == 1 or match_section[0] <= match_section[1]:
            current_file_section.append(match_section)
            current_file_section.sort(key=lambda x: x[0])

    @staticmethod
    def _pop_match_section(start_position, section_list):
        for section_item in section_list:
            if section_item[0] == start_position:
                section_list.remove(section_item)
                return section_item
        for section_item in section_list:
            if section_item[0] < start_position <= section_item[1]:
                section_list.remove(section_item)
                section_list.append([section_item[0], start_position - 1])
                return [start_position, section_item[1]]

    def _get_download_root_path(self, mission_uuid):
        download_info = self._mission_info_dict[mission_uuid]["download_info"]
        first_sub_path = list(download_info["file_dict"].keys())[0]
        return first_sub_path.split("/", 1)[0]

    def _get_target_save_path(self, mission_uuid, sub_path):
        root_path = self._mission_info_dict[mission_uuid]["mission_info"]["save_path"]
        return os.path.join(root_path, sub_path)

    def _request_mission_analyze(self, mission_uuid, analyze_tag):
        mission_info = self._mission_info_dict[mission_uuid]["mission_info"]
        mission_schema = self._mission_info_dict[mission_uuid]["schema"]
        analyze_item = {"schema": mission_schema, "analyze_tag": analyze_tag, "mission_info": mission_info}
        self._send_analyze_message("request", mission_uuid, analyze_item)

    def _generate_default_mission_info(self):
        standard_mission_info = dict()
        standard_mission_info["download_link"] = None
        standard_mission_info["save_path"] = self._runtime_operator.get_code_entrance_path()
        standard_mission_info["thread_num"] = 1
        standard_mission_info["headers"] = None
        standard_mission_info["proxy"] = None
        standard_mission_info["open_after_finish"] = False
        return standard_mission_info

    @staticmethod
    def _get_url_after_quote(link):
        return urllib.parse.quote(link, safe=":/?#[]@!$&'()*+,;=%")

    def _rename_file(self, mission_uuid, old_path, new_path):
        try:
            os.rename(old_path, new_path)
        except (IsADirectoryError, NotADirectoryError):
            self._send_print_message("normal", mission_uuid, "File type mismatch")

    def _send_print_message(self, signal_type, mission_uuid, content):
        message_dict = self._generate_action_signal_template("message.print")
        detail = {"sender": "MissionInfoReceiver", "content": content}
        message_dict["value"] = self._generate_signal_value(signal_type, mission_uuid, detail)
        self._parent_queue.put(message_dict)

    def _send_analyze_message(self, signal_type, mission_uuid, mission_detail):
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
