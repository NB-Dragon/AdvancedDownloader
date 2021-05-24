#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Create Time: 2021/5/16 12:00
# Create User: NB-Dragon
import queue
import threading
from listener.ThreadMessageDistributor import ThreadMessageDistributor
from manager.MissionInfoReceiver import MissionInfoReceiver
from tools.RuntimeOperator import RuntimeOperator


class MissionActionDistributor(threading.Thread):
    def __init__(self, runtime_operator: RuntimeOperator):
        super().__init__()
        self._runtime_operator = runtime_operator
        self._message_queue = queue.Queue()
        self._run_status = True
        self._init_all_listener()

    def run(self) -> None:
        self._start_all_listener()
        while self._should_thread_continue_to_execute():
            message_dict = self._message_queue.get()
            if message_dict is None: continue
            self._handle_message(message_dict)
        self._stop_all_listener()

    def get_message_queue(self):
        return self._message_queue

    def send_stop_state(self):
        self._run_status = False
        self._message_queue.put(None)

    def _should_thread_continue_to_execute(self):
        return self._run_status or self._message_queue.qsize()

    def _handle_message(self, message_dict):
        if "." in message_dict["receiver"]:
            self._handle_cross_level_receiver(message_dict)
        else:
            action_type, action_receiver = message_dict["action"], message_dict["receiver"]
            self._handle_same_level_receiver(action_type, action_receiver, message_dict["value"])

    def _handle_cross_level_receiver(self, raw_message):
        first_receiver, next_receiver = raw_message["receiver"].split(".", 1)
        raw_message["receiver"] = next_receiver
        if first_receiver in self._all_listener:
            self._all_listener[first_receiver]["queue"].put(raw_message)

    def _handle_same_level_receiver(self, action_type, action_receiver, action_detail):
        if action_type == "operate":
            pass
        elif action_type == "signal":
            self._do_with_action_signal(action_receiver, action_detail)

    def _do_with_action_signal(self, action_receiver, action_detail):
        if action_receiver in self._all_listener:
            self._all_listener[action_receiver]["queue"].put(action_detail)
        else:
            message_content = "signal_receiver `{}` not defined".format(action_receiver)
            self._send_message_to_print(message_content, False)

    def _init_all_listener(self):
        """
        message : handle all message with action
        info    : handle all mission info command
        """
        self._all_listener = dict()
        thread_message_distributor = ThreadMessageDistributor(self._runtime_operator, self._message_queue)
        thread_message_queue = thread_message_distributor.get_message_queue()
        self._all_listener["message"] = {"receiver": thread_message_distributor, "queue": thread_message_queue}
        mission_info_receiver = MissionInfoReceiver(self._runtime_operator, self._message_queue)
        mission_info_queue = mission_info_receiver.get_message_queue()
        self._all_listener["info"] = {"receiver": mission_info_receiver, "queue": mission_info_queue}

    def _start_all_listener(self):
        for listener in self._all_listener.values():
            listener["receiver"].start()

    def _stop_all_listener(self):
        for listener in self._all_listener.values():
            listener["receiver"].send_stop_state()

    def _send_message_to_print(self, content, exception: bool):
        message_item = self._generate_print_value(content, exception)
        signal_header = {"action": "signal", "receiver": "message.print", "value": message_item}
        self._message_queue.put(signal_header)

    @staticmethod
    def _generate_print_value(content, exception: bool):
        message_type = "exception" if exception else "normal"
        message_detail = {"sender": "MissionActionDistributor", "content": content}
        return {"type": message_type, "mission_uuid": None, "detail": message_detail}
