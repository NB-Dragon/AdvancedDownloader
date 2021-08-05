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


class ActionConfigReceiver(threading.Thread):
    def __init__(self, runtime_operator: RuntimeOperator, parent_queue: queue.Queue):
        super().__init__()
        self._runtime_operator = runtime_operator
        self._message_queue = queue.Queue()
        self._run_status = True
        self._parent_queue = parent_queue
        self._mission_config_dict = dict()

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
        elif signal_type == "update_mission_config":
            self._do_with_mission_update_mission_config(mission_uuid, message_detail)
        elif signal_type == "update_download_name":
            self._do_with_mission_update_download_name(mission_uuid, message_detail)
        elif signal_type == "open":
            self._do_with_mission_open(mission_uuid, message_detail)
        elif signal_type == "request_info":
            self._do_with_mission_request_info(mission_uuid)
        elif signal_type == "request_result":
            self._do_with_mission_request_result(mission_uuid, message_detail)
        elif signal_type == "update_section":
            self._do_with_mission_update_section(mission_uuid, message_detail)
        elif signal_type == "delete":
            self._do_with_mission_delete(mission_uuid, message_detail)

    def _do_with_mission_register(self, mission_uuid, message_detail):
        if "mission_info" in message_detail and "download_info" in message_detail:
            mission_info, download_info = message_detail["mission_info"], message_detail["download_info"]
            if mission_info.get("download_link"):
                self._mission_config_dict[mission_uuid] = dict()
                self._mission_config_dict[mission_uuid]["schema"] = message_detail["schema"]
                self._mission_config_dict[mission_uuid]["mission_info"] = self._get_standard_mission_info(mission_info)
                self._mission_config_dict[mission_uuid]["download_info"] = json.loads(json.dumps(download_info))

    def _do_with_mission_update_mission_config(self, mission_uuid, message_detail):
        if mission_uuid in self._mission_config_dict:
            if "save_path" in message_detail["mission_info"]:
                old_save_path = self._get_current_download_save_path(mission_uuid)
                tmp_save_path = message_detail["mission_info"]["save_path"]
                new_save_path = self._get_target_download_save_path(mission_uuid, tmp_save_path)
                self._rename_file(mission_uuid, old_save_path, new_save_path)
            for key, value in message_detail["mission_info"].items():
                if key in self._mission_config_dict[mission_uuid]["mission_info"]:
                    self._mission_config_dict[mission_uuid]["mission_info"][key] = value

    def _do_with_mission_update_download_name(self, mission_uuid, message_detail):
        if mission_uuid in self._mission_config_dict:
            if self._mission_config_dict[mission_uuid]["download_info"]:
                sub_old_path, sub_new_path = message_detail["sub_old_path"], message_detail["sub_new_path"]
                sub_new_path = self._format_file_path(sub_new_path)
                self._rename_file_or_directory(mission_uuid, sub_old_path, sub_new_path)
                self._update_download_info_sub_path(mission_uuid, sub_old_path, sub_new_path)

    def _do_with_mission_open(self, mission_uuid, message_detail):
        if mission_uuid in self._mission_config_dict:
            if self._mission_config_dict[mission_uuid]["download_info"]:
                old_save_path = self._get_mission_info_save_path(mission_uuid, message_detail["sub_path"])
                self._send_worker_open("open", mission_uuid, {"path": old_save_path})

    def _do_with_mission_request_info(self, mission_uuid):
        if mission_uuid in self._mission_config_dict:
            self._send_or_request_download_info(mission_uuid, 1)

    def _do_with_mission_request_result(self, mission_uuid, message_detail):
        if mission_uuid in self._mission_config_dict:
            self._mission_config_dict[mission_uuid]["download_info"] = message_detail["download_info"]
            self._send_or_request_download_info(mission_uuid, message_detail["analyze_tag"])

    def _do_with_mission_update_section(self, mission_uuid, message_detail):
        if mission_uuid in self._mission_config_dict:
            if self._mission_config_dict[mission_uuid]["download_info"]:
                position, length = message_detail["position"], message_detail["length"]
                self._update_download_section(mission_uuid, message_detail["sub_path"], position, length)

    def _do_with_mission_delete(self, mission_uuid, message_detail):
        if mission_uuid in self._mission_config_dict:
            if message_detail["delete_file"]:
                self._delete_file_or_directory(mission_uuid)
            self._mission_config_dict.pop(mission_uuid)

    def _update_mission_progress(self):
        self._runtime_operator.set_mission_state(self._mission_config_dict)

    def _get_standard_mission_info(self, mission_info):
        standard_mission_info = self._generate_default_mission_info()
        for key, value in mission_info.items():
            if key in standard_mission_info:
                standard_mission_info[key] = value
        download_link = standard_mission_info["download_link"]
        standard_mission_info["download_link"] = self._get_url_after_quote(download_link)
        return standard_mission_info

    def _delete_file_or_directory(self, mission_uuid):
        if self._mission_config_dict[mission_uuid]["download_info"]:
            old_save_path = self._get_current_download_save_path(mission_uuid)
            self._remove_file(old_save_path)

    def _rename_file_or_directory(self, mission_uuid, sub_old_path, sub_new_path):
        old_save_path = self._get_mission_info_save_path(mission_uuid, sub_old_path)
        new_save_path = self._get_mission_info_save_path(mission_uuid, sub_new_path)
        self._rename_file(mission_uuid, old_save_path, new_save_path)

    def _update_download_info_sub_path(self, mission_uuid, sub_old_path, sub_new_path):
        download_info_file_dict = self._mission_config_dict[mission_uuid]["download_info"]["file_dict"]
        for download_file_item in download_info_file_dict.keys():
            if download_file_item.startswith(sub_old_path):
                last_path = download_file_item.split(sub_old_path, 1)[1]
                new_path = os.path.join(sub_new_path, last_path)
                download_info_file_dict[new_path] = download_info_file_dict.pop(download_file_item)

    def _update_download_section(self, mission_uuid, sub_path, position, length):
        download_info = self._mission_config_dict[mission_uuid]["download_info"]
        current_file_section = download_info["file_dict"][sub_path]["section"]
        match_section = self._pop_match_section(position, current_file_section)
        match_section[0] += length
        if len(match_section) == 1 or match_section[0] <= match_section[1]:
            current_file_section.append(match_section)
            current_file_section.sort(key=lambda x: x[0])

    @staticmethod
    def _pop_match_section(position, section_list):
        for section_item in section_list:
            if section_item[0] == position:
                section_list.remove(section_item)
                return section_item
        for section_item in section_list:
            if section_item[0] < position <= section_item[1]:
                section_list.remove(section_item)
                section_list.append([section_item[0], position - 1])
                return [position, section_item[1]]

    def _get_current_download_save_path(self, mission_uuid):
        download_root_path = self._get_download_info_root_path(mission_uuid)
        return self._get_mission_info_save_path(mission_uuid, download_root_path)

    def _get_target_download_save_path(self, mission_uuid, target_path):
        download_root_path = self._get_download_info_root_path(mission_uuid)
        target_path = self._format_file_path(target_path)
        return os.path.join(target_path, download_root_path)

    def _get_download_info_root_path(self, mission_uuid):
        download_info = self._mission_config_dict[mission_uuid]["download_info"]
        first_sub_path = list(download_info["file_dict"].keys())[0]
        return first_sub_path.split("/", 1)[0]

    def _get_mission_info_save_path(self, mission_uuid, sub_path):
        root_path = self._mission_config_dict[mission_uuid]["mission_info"]["save_path"]
        return os.path.join(root_path, sub_path)

    def _send_or_request_download_info(self, mission_uuid, analyze_tag):
        if self._mission_config_dict[mission_uuid]["download_info"] or analyze_tag >= 3:
            self._send_mission_progress("request_result", mission_uuid, self._mission_config_dict[mission_uuid])
        else:
            self._request_mission_analyze(mission_uuid, analyze_tag + 1)

    def _request_mission_analyze(self, mission_uuid, analyze_tag):
        mission_info = self._mission_config_dict[mission_uuid]["mission_info"]
        mission_schema = self._mission_config_dict[mission_uuid]["schema"]
        analyze_item = {"schema": mission_schema, "analyze_tag": analyze_tag, "mission_info": mission_info}
        self._send_worker_analyze("request_info", mission_uuid, analyze_item)

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

    @staticmethod
    def _format_file_path(target_path):
        path_item_list = target_path.split(os.path.sep)
        while "" in path_item_list:
            path_item_list.remove("")
        while "." in path_item_list:
            path_item_list.remove(".")
        while ".." in path_item_list:
            parent_index = path_item_list.index("..")
            path_item_list.pop(parent_index)
            if parent_index - 1 >= 0:
                path_item_list.pop(parent_index - 1)
        return os.path.sep.join(path_item_list)

    def _rename_file(self, mission_uuid, old_path, new_path):
        try:
            if os.path.exists(old_path):
                os.rename(old_path, new_path)
        except (IsADirectoryError, NotADirectoryError):
            self._send_worker_print("normal", mission_uuid, "File type mismatch")

    @staticmethod
    def _remove_file(target_path):
        if os.path.isdir(target_path):
            shutil.rmtree(target_path)
        elif os.path.exists(target_path):
            os.remove(target_path)

    def _send_worker_print(self, signal_type, mission_uuid, content):
        message_dict = self._generate_action_signal_template("parent.worker.print")
        detail = {"sender": "ActionConfigReceiver", "content": content}
        message_dict["value"] = self._generate_signal_value(signal_type, mission_uuid, detail)
        self._parent_queue.put(message_dict)

    def _send_worker_analyze(self, signal_type, mission_uuid, mission_detail):
        message_dict = self._generate_action_signal_template("parent.worker.analyze")
        message_dict["value"] = self._generate_signal_value(signal_type, mission_uuid, mission_detail)
        self._parent_queue.put(message_dict)

    def _send_worker_open(self, signal_type, mission_uuid, mission_detail):
        message_dict = self._generate_action_signal_template("parent.worker.open")
        message_dict["value"] = self._generate_signal_value(signal_type, mission_uuid, mission_detail)
        self._parent_queue.put(message_dict)

    def _send_mission_progress(self, signal_type, mission_uuid, mission_detail):
        message_dict = self._generate_action_signal_template("thread")
        message_dict["value"] = self._generate_signal_value(signal_type, mission_uuid, mission_detail)
        self._parent_queue.put(message_dict)

    @staticmethod
    def _generate_action_signal_template(receiver):
        return {"receiver": receiver, "value": None}

    @staticmethod
    def _generate_signal_value(signal_type, mission_uuid, mission_detail):
        return {"type": signal_type, "mission_uuid": mission_uuid, "detail": mission_detail}