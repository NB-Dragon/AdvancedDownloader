#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Create Time: 2021/5/16 12:00
# Create User: NB-Dragon
import queue
import threading
from listener.ThreadMessageDistributor import ThreadMessageDistributor
from manager.MissionAnalyseReceiver import MissionAnalyseReceiver
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
            if message_dict["action"] == "operate":
                pass
            elif message_dict["action"] == "signal":
                self._handle_action_signal(message_dict["receiver"], message_dict["value"])
        self._stop_all_listener()

    def get_message_queue(self):
        return self._message_queue

    def send_stop_state(self):
        self._run_status = False
        self._message_queue.put(None)

    def _should_thread_continue_to_execute(self):
        return self._run_status or self._message_queue.qsize()

    def _handle_action_signal(self, signal_receiver, signal_detail):
        if signal_receiver in self._all_listener:
            self._all_listener[signal_receiver]["queue"].put(signal_detail)
        else:
            self._send_print_message_to_listener("action `{}` not defined".format(signal_receiver))

    def _init_all_listener(self):
        """
        message : handle all message with action
        analyse : handle all mission which want to analyse
        """
        self._all_listener = dict()
        thread_message_distributor = ThreadMessageDistributor(self._runtime_operator)
        thread_message_queue = thread_message_distributor.get_message_queue()
        self._all_listener["message"] = {"receiver": thread_message_distributor, "queue": thread_message_queue}
        mission_analyse_receiver = MissionAnalyseReceiver(self._runtime_operator, self._message_queue)
        mission_analyse_queue = mission_analyse_receiver.get_message_queue()
        self._all_listener["analyse"] = {"receiver": mission_analyse_receiver, "queue": mission_analyse_queue}

    def _start_all_listener(self):
        for listener in self._all_listener.values():
            listener["receiver"].start()

    def _stop_all_listener(self):
        for listener in self._all_listener.values():
            listener["receiver"].send_stop_state()

    def _send_print_message_to_listener(self, content):
        detail_info = {"sender": "MissionActionDistributor", "content": content, "exception": False}
        message_dict = {"action": "print", "value": {"mission_uuid": None, "detail": detail_info}}
        self._all_listener["message"]["queue"].put(message_dict)
