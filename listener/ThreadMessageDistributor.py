#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Create Time: 2021/1/25 10:00
# Create User: NB-Dragon
import queue
import threading
from tools.RuntimeOperator import RuntimeOperator
from listener.ActionOpenReceiver import ActionOpenReceiver
from listener.ActionPrintReceiver import ActionPrintReceiver
from listener.ActionSpeedReceiver import ActionSpeedReceiver
from listener.ActionWriterReceiver import ActionWriterReceiver


class ThreadMessageDistributor(threading.Thread):
    def __init__(self, runtime_operator: RuntimeOperator):
        super().__init__()
        self._runtime_operator = runtime_operator
        self._message_queue = queue.Queue()
        self._run_status = True
        self._init_all_listener()

    def run(self) -> None:
        self._start_all_listener()
        while self._run_status or self._message_queue.qsize():
            message_dict = self._message_queue.get()
            if message_dict is None: continue
            action = message_dict["action"]
            if action in self._all_listener:
                self._all_listener[action]["queue"].put(message_dict["value"])
            else:
                self._send_message_to_print("action `{}` not defined".format(action))
        self._do_before_distributor_down()
        self._stop_all_listener()

    def get_message_queue(self):
        return self._message_queue

    def send_stop_state(self):
        self._run_status = False
        self._message_queue.put(None)

    def _do_before_distributor_down(self):
        if not self._all_listener["open"]["receiver"].is_command_installed():
            file_path = self._runtime_operator.get_static_donate_image_path()
            content = "The sponsored QR code image path is: {}".format(file_path)
            self._send_message_to_print(content)

    def _init_all_listener(self):
        """
        print : handle all message which need to print
        write : handle all file register and writing
        speed : handle all the changes in file size
        open  : handle all the files open operation
        """
        self._all_listener = dict()
        action_print_receiver = ActionPrintReceiver(self._runtime_operator)
        action_print_queue = action_print_receiver.get_message_queue()
        self._all_listener["print"] = {"receiver": action_print_receiver, "queue": action_print_queue}
        action_speed_receiver = ActionSpeedReceiver(self._runtime_operator, self._message_queue)
        action_speed_queue = action_speed_receiver.get_message_queue()
        self._all_listener["speed"] = {"receiver": action_speed_receiver, "queue": action_speed_queue}
        action_write_receiver = ActionWriterReceiver(self._runtime_operator, self._message_queue)
        action_write_queue = action_write_receiver.get_message_queue()
        self._all_listener["write"] = {"receiver": action_write_receiver, "queue": action_write_queue}
        action_open_receiver = ActionOpenReceiver(self._runtime_operator, self._message_queue)
        action_open_queue = action_open_receiver.get_message_queue()
        self._all_listener["open"] = {"receiver": action_open_receiver, "queue": action_open_queue}

    def _start_all_listener(self):
        for listener in self._all_listener.values():
            listener["receiver"].start()

    def _stop_all_listener(self):
        for listener in self._all_listener.values():
            listener["receiver"].send_stop_state()

    def _send_message_to_print(self, content):
        detail_info = {"sender": "ThreadMessageDistributor", "content": content, "exception": False}
        value = {"mission_uuid": None, "detail": detail_info}
        self._all_listener["print"]["queue"].put(value)
