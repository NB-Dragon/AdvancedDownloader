import os
import json
import queue
import threading


class ActionPrintReceiver(threading.Thread):
    def __init__(self, runtime_entrance_path):
        super().__init__()
        self._message_queue = queue.Queue()
        self._log_file = os.path.join(runtime_entrance_path, "log.txt")
        self._run_status = True

    def run(self) -> None:
        while self._run_status or self._message_queue.qsize():
            message_dict = self._message_queue.get()
            if message_dict is None: continue
            message_exception = message_dict.pop("exception")
            message_content = json.dumps(message_dict, ensure_ascii=False)
            if not message_exception:
                print(message_content)
            else:
                self._append_log_message("{}\n".format(message_content))

    def get_message_queue(self):
        return self._message_queue

    def send_stop_state(self):
        self._run_status = False
        self._message_queue.put(None)

    def _append_log_message(self, message):
        try:
            writer = open(self._log_file, "a")
            writer.write(message)
            writer.close()
        except Exception as e:
            print(str(e))
