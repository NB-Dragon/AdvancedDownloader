#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Create Time: 2020/2/20 18:02
# Create User: hya-machine
import queue
import threading
import json


class MessageHandler(threading.Thread):
    def __init__(self):
        super().__init__()
        self._message_queue = queue.Queue()
        self._run_status = True

    def get_message_queue(self):
        return self._message_queue

    def run(self) -> None:
        while self._run_status:
            if not self._message_queue.empty():
                message = self._message_queue.get()
                try:
                    print(json.dumps(message))
                except Exception:
                    print(message)

    def send_stop_state(self):
        self._run_status = False
