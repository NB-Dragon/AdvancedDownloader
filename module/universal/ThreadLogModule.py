#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Create Time: 2022/01/01 00:00
# Create User: NB-Dragon
import queue
import threading
import time


class ThreadLogModule(threading.Thread):
    def __init__(self, project_helper):
        super().__init__()
        self._project_helper = project_helper
        global_config = self._project_helper.get_project_config()["global"]
        self._log_file_path = self._project_helper.get_project_path("log")
        self._debug_mode = global_config["debug"]
        self._message_queue = queue.Queue()
        self._run_status = True

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

    def _should_thread_continue_to_execute(self):
        return self._run_status or self._message_queue.qsize()

    def _handle_message_detail(self, mission_uuid, message_type, message_detail):
        output_content = self._generate_log_content(mission_uuid, message_detail)
        if message_type == "console":
            self._do_with_action_console(output_content)
        elif message_type == "file":
            self._do_with_action_file(output_content)

    @staticmethod
    def _generate_log_content(mission_uuid, message_detail):
        tag_name, content = message_detail.get("sender"), message_detail.get("content")
        current_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(time.time()))
        return "[{}][{}][{}]: {}".format(current_time, mission_uuid, tag_name, content)

    def _do_with_action_file(self, content):
        writer = open(self._log_file_path, "a")
        writer.write("{}\n".format(content))
        writer.close()

    def _do_with_action_console(self, content):
        if self._debug_mode:
            print(content)
