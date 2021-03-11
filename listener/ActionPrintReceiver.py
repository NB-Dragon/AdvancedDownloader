#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Create Time: 2021/1/25 10:00
# Create User: NB-Dragon
import time
import json
import queue
import threading
from tool.RuntimeOperator import RuntimeOperator


class ActionPrintReceiver(threading.Thread):
    def __init__(self, runtime_operator: RuntimeOperator):
        super().__init__()
        self._runtime_operator = runtime_operator
        self._message_queue = queue.Queue()
        self._run_status = True

    def run(self) -> None:
        while self._run_status or self._message_queue.qsize():
            message_dict = self._message_queue.get()
            # {"mission_uuid": str, "detail": {"sender": str, "content": str, "exception": bool}}
            if message_dict:
                self._handle_message_detail(message_dict["mission_uuid"], message_dict["detail"])

    def get_message_queue(self):
        return self._message_queue

    def send_stop_state(self):
        self._run_status = False
        self._message_queue.put(None)

    def _handle_message_detail(self, mission_uuid, mission_detail):
        exception = mission_detail.pop("exception")
        output_detail = self._generate_final_message(mission_uuid, mission_detail)
        message_content = json.dumps(output_detail, ensure_ascii=False)
        if not exception:
            print(message_content)
        else:
            self._append_log_message("{}\n".format(message_content))

    @staticmethod
    def _generate_final_message(mission_uuid, mission_detail):
        output_detail = dict()
        output_detail["timestamp"] = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(time.time()))
        output_detail["mission_uuid"] = mission_uuid
        output_detail["sender"] = mission_detail["sender"]
        output_detail["content"] = mission_detail["content"]
        return output_detail

    def _append_log_message(self, message):
        file_path = self._runtime_operator.get_cache_file("log")
        writer = open(file_path, 'a')
        writer.write(message)
        writer.close()
