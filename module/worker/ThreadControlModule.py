#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Create Time: 2022/01/01 00:00
# Create User: NB-Dragon
import queue
import threading
from module.archiver.ProgressTool import ProgressTool


class ThreadControlModule(threading.Thread):
    def __init__(self, project_helper, switch_message):
        super().__init__()
        self._project_helper = project_helper
        self._switch_message = switch_message
        self._message_queue = queue.Queue()
        self._run_status = True
        self._init_module_tool()
        self._mission_dict = dict()
        self._process_dict = dict()

    def run(self) -> None:
        while self._should_thread_continue_to_execute():
            message_dict = self._message_queue.get()
            if message_dict is None: continue
            message_type, message_detail = message_dict["message_type"], message_dict["message_detail"]
            self._handle_message_detail(message_dict["mission_uuid"], message_type, message_detail)

    def append_message(self, message):
        self._message_queue.put(message)

    def send_stop_state(self):
        self._stop_all_process()
        self._run_status = False
        self.append_message(None)

    def _init_module_tool(self):
        self._module_tool = dict()
        self._module_tool["progress"] = ProgressTool(self._project_helper)

    def _should_thread_continue_to_execute(self):
        return self._run_status or self._message_queue.qsize()

    def _handle_message_detail(self, mission_uuid, message_type, message_detail):
        if message_type == "data_sync":
            self._do_with_data_sync(mission_uuid, message_detail)
        elif message_type == "data_response":
            self._do_with_data_response(mission_uuid, message_detail)
        elif message_type == "mission_start":
            self._do_with_mission_start(mission_uuid, message_detail)
        elif message_type == "mission_pause":
            self._do_with_mission_pause(mission_uuid, message_detail)
        elif message_type == "mission_delete":
            self._do_with_mission_delete(mission_uuid, message_detail)
        elif message_type == "process_update":
            self._do_with_process_update(mission_uuid, message_detail)
        elif message_type == "process_pause":
            self._do_with_process_pause(mission_uuid, message_detail)
        elif message_type == "process_finish":
            self._do_with_process_finish(mission_uuid, message_detail)
        else:
            abnormal_message = "Unknown message type of \"{}\"".format(message_type)
            self._send_universal_log(mission_uuid, "file", abnormal_message)

    def _do_with_data_sync(self, mission_uuid, message_detail):
        mission_info, download_info = message_detail["mission_info"], message_detail["download_info"]
        self._mission_dict[mission_uuid] = {"mission_info": mission_info, "download_info": download_info}

    def _do_with_data_response(self, mission_uuid, message_detail):
        if isinstance(message_detail["download_info"], dict):
            self._mission_dict[mission_uuid]["download_info"] = message_detail["download_info"]
            self._create_download_process(mission_uuid)
        else:
            self._send_universal_log(mission_uuid, "console", "Analyze failed. Please retry.")

    def _do_with_mission_start(self, mission_uuid, message_detail):
        mission_uuid_list = self._generate_actionable_mission_uuid(mission_uuid)
        for mission_uuid_item in mission_uuid_list:
            if isinstance(self._mission_dict[mission_uuid_item]["download_info"], dict):
                if mission_uuid_item not in self._process_dict:
                    self._create_download_process(mission_uuid_item)
            else:
                self._send_semantic_transform(mission_uuid_item, "data_request", None)

    def _do_with_mission_pause(self, mission_uuid, message_detail):
        if mission_uuid in self._process_dict:
            self._pause_download_process(mission_uuid)

    def _do_with_mission_delete(self, mission_uuid, message_detail):
        if mission_uuid in self._process_dict:
            self._delete_download_process(mission_uuid, message_detail)
        else:
            self._do_with_process_finish(mission_uuid, message_detail)

    def _do_with_process_update(self, mission_uuid, message_detail):
        self._send_semantic_transform(mission_uuid, "update_request", message_detail)

    def _do_with_process_pause(self, mission_uuid, message_detail):
        if mission_uuid in self._process_dict:
            self._process_dict.pop(mission_uuid)

    def _do_with_process_finish(self, mission_uuid, message_detail):
        if mission_uuid in self._mission_dict:
            self._mission_dict.pop(mission_uuid)
        if mission_uuid in self._process_dict:
            self._process_dict.pop(mission_uuid)
        self._send_semantic_transform(mission_uuid, "delete_request", message_detail)

    def _create_download_process(self, mission_uuid):
        # 这里需要实现创建进程并启动的逻辑
        self._send_universal_log(mission_uuid, "console", "Download process started.")

    def _pause_download_process(self, mission_uuid):
        # 这里需要实现暂停进程的逻辑，使其停止后返回"process_pause"信号
        self._send_universal_log(mission_uuid, "console", "Download process pause.")

    def _delete_download_process(self, mission_uuid, message_detail):
        # 这里需要实现删除进程的逻辑，使其停止后返回"process_finish"信号
        # process_finish: 当自然结束，需设置不删除文件，非自然结束则删除文件
        self._send_universal_log(mission_uuid, "console", "Download process delete.")

    def _stop_all_process(self):
        for mission_uuid in self._process_dict.keys():
            self._pause_download_process(mission_uuid)

    def _generate_actionable_mission_uuid(self, mission_uuid):
        if mission_uuid in self._mission_dict:
            return [mission_uuid]
        elif mission_uuid is None:
            return list(self._mission_dict.keys())
        else:
            return []

    def _send_state_modify_message(self, mission_uuid, mission_state):
        response_detail = {"mission_state": mission_state}
        self._send_archiver_archive(mission_uuid, "state_request", response_detail)

    def _send_archiver_archive(self, mission_uuid, message_type, message_detail):
        message_dict = self._generate_action_signal_template("thread-archive")
        message_dict["value"] = self._generate_signal_value(mission_uuid, message_type, message_detail)
        self._switch_message.append_message(message_dict)

    def _send_semantic_transform(self, mission_uuid, message_type, message_detail):
        message_dict = self._generate_action_signal_template("thread-transform")
        message_dict["value"] = self._generate_signal_value(mission_uuid, message_type, message_detail)
        self._switch_message.append_message(message_dict)

    def _send_universal_log(self, mission_uuid, message_type, content):
        message_dict = self._generate_action_signal_template("thread-log")
        message_detail = {"sender": "ThreadControlModule", "content": content}
        message_dict["value"] = self._generate_signal_value(mission_uuid, message_type, message_detail)
        self._switch_message.append_message(message_dict)

    @staticmethod
    def _generate_action_signal_template(receiver):
        return {"receiver": receiver, "value": {}}

    @staticmethod
    def _generate_signal_value(mission_uuid, message_type, message_detail) -> dict:
        return {"mission_uuid": mission_uuid, "message_type": message_type, "message_detail": message_detail}
