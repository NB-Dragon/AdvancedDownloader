#!/usr/bin/env python
import os
import sys
import json
import queue
import threading


class MessageReceiveThread(threading.Thread):
    def __init__(self):
        super().__init__()
        self._message_queue = queue.Queue()
        self._code_entrance_path = os.path.split(os.path.abspath(sys.argv[0]))[0]
        self._log_file = os.path.join(self._code_entrance_path, "log.txt")
        self._run_status = True

    def run(self) -> None:
        while self._run_status or self._message_queue.qsize():
            message_dict = self._message_queue.get()
            if message_dict is None:
                continue
            if not message_dict["exception"]:
                print(json.dumps(message_dict["message"], ensure_ascii=False))
            else:
                self._append_log_message("{}\n".format(message_dict["message"]))

    def _append_log_message(self, message):
        try:
            writer = open(self._log_file, "a")
            writer.write(message)
            writer.close()
        except Exception as e:
            print(str(e))

    def get_message_queue(self):
        return self._message_queue

    def send_stop_state(self):
        self._run_status = False
        self._message_queue.put(None)
