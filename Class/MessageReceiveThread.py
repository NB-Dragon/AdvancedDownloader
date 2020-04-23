#!/usr/bin/env python
import json
import queue
import threading


class MessageReceiveThread(threading.Thread):
    def __init__(self):
        super().__init__()
        self._message_queue = queue.Queue()
        self._run_status = True

    def run(self) -> None:
        while self._run_status or self._message_queue.qsize():
            if not self._message_queue.empty():
                message = self._message_queue.get()
                print(json.dumps(message, ensure_ascii=False))

    def get_message_queue(self):
        return self._message_queue

    def send_stop_state(self):
        self._run_status = False
