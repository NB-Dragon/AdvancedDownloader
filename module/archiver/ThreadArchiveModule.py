#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Create Time: 2022/01/01 00:00
# Create User: NB-Dragon
import json
import os
import queue
import shutil
import threading
from module.archiver.ProgressTool import ProgressTool


class ThreadArchiveModule(threading.Thread):
    def __init__(self, project_helper, switch_message):
        super().__init__()
        self._project_helper = project_helper
        self._switch_message = switch_message
        self._message_queue = queue.Queue()
        self._run_status = True
        self._init_module_tool()
        self._mission_dict = self._load_local_progress()

    def run(self) -> None:
        self._start_all_mission()
        while self._should_thread_continue_to_execute():
            message_dict = self._message_queue.get()
            if message_dict is None: continue
            message_type, message_detail = message_dict["message_type"], message_dict["message_detail"]
            self._handle_message_detail(message_dict["mission_uuid"], message_type, message_detail)
            self._update_mission_progress()

    def append_message(self, message):
        self._message_queue.put(message)

    def send_stop_state(self):
        self._run_status = False
        self.append_message(None)

    def _init_module_tool(self):
        self._module_tool = dict()
        self._module_tool["progress"] = ProgressTool(self._project_helper)
        self._global_config = self._project_helper.get_project_config()["global"]

    def _should_thread_continue_to_execute(self):
        return self._run_status or self._message_queue.qsize()

    def _handle_message_detail(self, mission_uuid, message_type, message_detail):
        if message_type == "create_request":
            self._do_with_create_request(mission_uuid, message_detail)
        elif message_type == "archive_request":
            self._do_with_archive_request(mission_uuid, message_detail)
        elif message_type == "query_request":
            self._do_with_query_request(mission_uuid, message_detail)
        elif message_type == "delete_request":
            self._do_with_delete_request(mission_uuid, message_detail)
        elif message_type == "state_request":
            self._do_with_state_request(mission_uuid, message_detail)
        else:
            abnormal_message = "Unknown message type of \"{}\"".format(message_type)
            self._send_universal_log(mission_uuid, "file", abnormal_message)

    def _do_with_create_request(self, mission_uuid, message_detail):
        self._mission_dict[mission_uuid] = dict()
        mission_info = json.loads(json.dumps(message_detail["mission_info"]))
        self._mission_dict[mission_uuid]["mission_info"] = mission_info
        self._mission_dict[mission_uuid]["download_info"] = None
        self._mission_dict[mission_uuid]["mission_state"] = "sleeping"

    def _do_with_archive_request(self, mission_uuid, message_detail):
        if mission_uuid in self._mission_dict:
            self._mission_dict[mission_uuid]["download_info"] = message_detail["download_info"]
            self._send_semantic_transform(mission_uuid, "archive_response", None)

    def _do_with_query_request(self, mission_uuid, message_detail):
        if mission_uuid in self._mission_dict:
            response_detail = json.loads(json.dumps(self._mission_dict[mission_uuid]))
            self._send_semantic_transform(mission_uuid, "query_response", response_detail)

    def _do_with_delete_request(self, mission_uuid, message_detail):
        if mission_uuid in self._mission_dict:
            self._delete_mission_file(mission_uuid, message_detail["delete_file"])
            self._mission_dict.pop(mission_uuid)

    def _do_with_state_request(self, mission_uuid, message_detail):
        if mission_uuid in self._mission_dict:
            mission_state = message_detail["mission_state"]
            if mission_state in ["sleeping", "analyzing", "running"]:
                self._mission_dict[mission_uuid]["mission_state"] = mission_state

    def _load_local_progress(self):
        return self._module_tool["progress"].get_download_progress()

    def _update_mission_progress(self):
        self._module_tool["progress"].set_download_progress(self._mission_dict)

    def _start_all_mission(self):
        if self._global_config["auto_start"]:
            response_detail = {"success": True}
            for mission_uuid in self._mission_dict.keys():
                self._send_semantic_transform(mission_uuid, "archive_response", response_detail)

    def _delete_mission_file(self, mission_uuid, delete_file):
        if delete_file is True:
            mission_file_path = self._mission_dict[mission_uuid]["save_path"]
            if os.path.isfile(mission_file_path):
                os.remove(mission_file_path)
            elif os.path.isdir(mission_file_path):
                shutil.rmtree(mission_file_path)

    def _send_semantic_transform(self, mission_uuid, message_type, message_detail):
        message_dict = self._generate_action_signal_template("thread-transform")
        message_dict["value"] = self._generate_signal_value(mission_uuid, message_type, message_detail)
        self._switch_message.append_message(message_dict)

    def _send_universal_log(self, mission_uuid, message_type, content):
        message_dict = self._generate_action_signal_template("thread-log")
        message_detail = {"sender": "ThreadArchiveModule", "content": content}
        message_dict["value"] = self._generate_signal_value(mission_uuid, message_type, message_detail)
        self._switch_message.append_message(message_dict)

    @staticmethod
    def _generate_action_signal_template(receiver):
        return {"receiver": receiver, "value": {}}

    @staticmethod
    def _generate_signal_value(mission_uuid, message_type, message_detail) -> dict:
        return {"mission_uuid": mission_uuid, "message_type": message_type, "message_detail": message_detail}
