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
            if message_dict is None: continue
            message_exception = message_dict["detail"].pop("exception")
            time_description = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(time.time()))
            message_content = json.dumps({time_description: message_dict}, ensure_ascii=False)
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
            log_file = self._runtime_operator.get_cache_file("log")
            writer = open(log_file, 'a')
            writer.write(message)
            writer.close()
        except Exception as e:
            print(str(e))
