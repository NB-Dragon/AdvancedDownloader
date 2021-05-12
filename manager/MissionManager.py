#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Create Time: 2021/5/10 12:30
# Create User: NB-Dragon
import queue
import threading
from tools.RuntimeOperator import RuntimeOperator
from listener.ThreadMessageDistributor import ThreadMessageDistributor


class MissionManager(threading.Thread):
    def __init__(self):
        super().__init__()
        self._runtime_operator = RuntimeOperator()
        self._message_queue = queue.Queue()
        self._run_status = True
        self._mission_dict = dict()
        self._init_all_listener()

    def run(self) -> None:
        self._start_all_listener()
        while self._should_thread_continue_to_execute():
            message_dict = self._message_queue.get()
            if message_dict is None: continue

        self._stop_all_listener()

    def get_message_queue(self):
        return self._message_queue

    def send_stop_state(self):
        self._run_status = False
        self._message_queue.put(None)

    def _should_thread_continue_to_execute(self):
        return self._run_status or self._message_queue.qsize() or self._has_mission_alive()

    def _init_all_listener(self):
        """
        message : handle all message with action
        """
        self._all_listener = dict()
        thread_message_distributor = ThreadMessageDistributor(self._runtime_operator)
        thread_message_queue = thread_message_distributor.get_message_queue()
        self._all_listener["message"] = {"receiver": thread_message_distributor, "queue": thread_message_queue}

    def _start_all_listener(self):
        for listener in self._all_listener.values():
            listener["receiver"].start()

    def _stop_all_listener(self):
        for listener in self._all_listener.values():
            listener["receiver"].send_stop_state()

    def _has_mission_alive(self):
        alive_mission = [key for key, value in self._mission_dict.items() if value["running"]]
        return len(alive_mission) == 0
