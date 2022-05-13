#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Create Time: 2022/01/01 00:00
# Create User: NB-Dragon
import queue
import threading


class ThreadTransformModule(threading.Thread):
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
        self._global_config = self._project_helper.get_project_config()["global"]

    def _should_thread_continue_to_execute(self):
        return self._run_status or self._message_queue.qsize()

    def _handle_message_detail(self, mission_uuid, message_type, message_detail):
        if message_type == "create_command":
            self._do_with_create_command(mission_uuid, message_detail)
        elif message_type == "start_command":
            self._do_with_start_command(mission_uuid, message_detail)
        elif message_type == "pause_command":
            self._do_with_pause_command(mission_uuid, message_detail)
        elif message_type == "delete_command":
            self._do_with_delete_command(mission_uuid, message_detail)
        elif message_type == "data_request":
            self._do_with_data_request(mission_uuid, message_detail)
        elif message_type == "update_request":
            self._do_with_update_request(mission_uuid, message_detail)
        elif message_type == "delete_request":
            self._do_with_delete_request(mission_uuid, message_detail)
        elif message_type == "analyze_response":
            self._do_with_analyze_response(mission_uuid, message_detail)
        elif message_type == "archive_response":
            self._do_with_archive_response(mission_uuid, message_detail)
        elif message_type == "query_response":
            self._do_with_query_response(mission_uuid, message_detail)
        else:
            abnormal_message = "Unknown message type of \"{}\"".format(message_type)
            self._send_universal_log(mission_uuid, "file", abnormal_message)

    def _do_with_create_command(self, mission_uuid, message_detail):
        self._send_archiver_archive(mission_uuid, "create_request", message_detail)

    def _do_with_start_command(self, mission_uuid, message_detail):
        self._send_worker_control(mission_uuid, "mission_start", None)

    def _do_with_pause_command(self, mission_uuid, message_detail):
        self._send_worker_control(mission_uuid, "mission_pause", None)

    def _do_with_delete_command(self, mission_uuid, message_detail):
        self._send_worker_control(mission_uuid, "mission_delete", message_detail)

    def _do_with_data_request(self, mission_uuid, message_detail):
        self._send_archiver_archive(mission_uuid, "query_request", None)

    def _do_with_update_request(self, mission_uuid, message_detail):
        response_detail = {"download_info": message_detail["download_info"]}
        self._send_archiver_archive(mission_uuid, "archive_request", response_detail)
        response_detail = {"size": message_detail["update_size"]}
        self._send_universal_speed(mission_uuid, "change", response_detail)

    def _do_with_delete_request(self, mission_uuid, message_detail):
        self._send_archiver_archive(mission_uuid, "delete_request", message_detail)
        self._send_universal_speed(mission_uuid, "delete", None)

    def _do_with_analyze_response(self, mission_uuid, message_detail):
        mission_info, download_info = message_detail["mission_info"], message_detail["download_info"]
        if message_detail["download_info"] is None:
            if message_detail["analyze_count"] < self._global_config["retry"]:
                response_detail = {"analyze_count": message_detail["analyze_count"] + 1, "mission_info": mission_info}
                self._send_analyzer_analyze(mission_uuid, "analyze_request", response_detail)
            else:
                response_detail = {"mission_info": mission_info, "download_info": download_info}
                self._send_worker_control(mission_uuid, "data_response", response_detail)
        else:
            response_detail = {"download_info": download_info}
            self._send_archiver_archive(mission_uuid, "archive_request", response_detail)

    def _do_with_archive_response(self, mission_uuid, message_detail):
        self._send_worker_control(mission_uuid, "mission_start", None)

    def _do_with_query_response(self, mission_uuid, message_detail):
        mission_info, download_info = message_detail["mission_info"], message_detail["download_info"]
        if message_detail["download_info"] is None:
            response_detail = {"analyze_count": 0, "mission_info": mission_info}
            self._send_analyzer_analyze(mission_uuid, "analyze_request", response_detail)
        else:
            response_detail = {"download_info": download_info}
            self._send_universal_speed(mission_uuid, "register", response_detail)
            response_detail = {"mission_info": mission_info, "download_info": download_info}
            self._send_worker_control(mission_uuid, "data_response", response_detail)

    def _send_analyzer_analyze(self, mission_uuid, message_type, message_detail):
        message_dict = self._generate_action_signal_template("thread-analyze")
        message_dict["value"] = self._generate_signal_value(mission_uuid, message_type, message_detail)
        self._switch_message.append_message(message_dict)

    def _send_archiver_archive(self, mission_uuid, message_type, message_detail):
        message_dict = self._generate_action_signal_template("thread-archive")
        message_dict["value"] = self._generate_signal_value(mission_uuid, message_type, message_detail)
        self._switch_message.append_message(message_dict)

    def _send_worker_control(self, mission_uuid, message_type, message_detail):
        message_dict = self._generate_action_signal_template("thread-control")
        message_dict["value"] = self._generate_signal_value(mission_uuid, message_type, message_detail)
        self._switch_message.append_message(message_dict)

    def _send_universal_speed(self, mission_uuid, message_type, message_detail):
        message_dict = self._generate_action_signal_template("thread-speed")
        message_dict["value"] = self._generate_signal_value(mission_uuid, message_type, message_detail)
        self._switch_message.append_message(message_dict)

    def _send_universal_log(self, mission_uuid, message_type, content):
        message_dict = self._generate_action_signal_template("thread-log")
        message_detail = {"sender": "ThreadTransformModule", "content": content}
        message_dict["value"] = self._generate_signal_value(mission_uuid, message_type, message_detail)
        self._switch_message.append_message(message_dict)

    @staticmethod
    def _generate_action_signal_template(receiver):
        return {"receiver": receiver, "value": {}}

    @staticmethod
    def _generate_signal_value(mission_uuid, message_type, message_detail) -> dict:
        return {"mission_uuid": mission_uuid, "message_type": message_type, "message_detail": message_detail}
