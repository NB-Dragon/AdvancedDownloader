#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Create Time: 2021/1/25 10:00
# Create User: NB-Dragon
import json
import queue
import threading
import time
from tools.RuntimeOperator import RuntimeOperator


class ActionPrintReceiver(threading.Thread):
    def __init__(self, runtime_operator: RuntimeOperator):
        super().__init__()
        self._runtime_operator = runtime_operator
        self._message_queue = queue.Queue()
        self._run_status = True

    def run(self) -> None:
        while self._should_thread_continue_to_execute():
            message_dict = self._message_queue.get()
            if message_dict is None: continue
            self._handle_message_detail(message_dict["mission_uuid"], message_dict["detail"])

    def get_message_queue(self):
        return self._message_queue

    def send_stop_state(self):
        self._run_status = False
        self._message_queue.put(None)

    def _should_thread_continue_to_execute(self):
        return self._run_status or self._message_queue.qsize()

    def _handle_message_detail(self, mission_uuid, mission_detail):
        exception = mission_detail.get("exception", False)
        output_detail = self._generate_final_message(mission_uuid, mission_detail)
        message_content = json.dumps(output_detail, ensure_ascii=False)
        if not exception:
            print(message_content)
        else:
            self._runtime_operator.append_run_log_content("{}\n".format(message_content))

    @staticmethod
    def _generate_final_message(mission_uuid, mission_detail):
        output_detail = dict()
        output_detail["timestamp"] = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(time.time()))
        output_detail["mission_uuid"] = mission_uuid
        output_detail["sender"] = mission_detail.get("sender")
        output_detail["content"] = mission_detail.get("content")
        return output_detail
