import queue
import threading
from listener.ActionPrintReceiver import ActionPrintReceiver
from listener.FileWriterReceiver import FileWriterReceiver
from tool.RuntimeOperator import RuntimeOperator


class ThreadMessageDistributor(threading.Thread):
    def __init__(self, runtime_operator: RuntimeOperator):
        super().__init__()
        self._runtime_operator = runtime_operator
        self._all_listener = self._init_all_listener()
        self._message_queue = queue.Queue()
        self._run_status = True

    def run(self) -> None:
        self._start_all_listener()
        while self._run_status or self._message_queue.qsize():
            message_dict = self._message_queue.get()
            # {"action": str, "value": Any}
            if message_dict is None: continue
            action = message_dict["action"]
            if action in self._all_listener:
                self._all_listener[action]["queue"].put(message_dict["value"])
            else:
                value = {"exception": False, "content": "action `{}` not defined".format(action)}
                self._all_listener["print"]["queue"].put(value)

    def get_message_queue(self):
        return self._message_queue

    def send_stop_state(self):
        for listener in self._all_listener.values():
            listener["receiver"].send_stop_state()
        self._run_status = False
        self._message_queue.put(None)

    def _init_all_listener(self):
        """
        print : handle all message which need to print
        file  : handle all file register and writing
        config: 1
        """
        result_dict = dict()
        action_print_receiver = ActionPrintReceiver(self._runtime_operator)
        action_print_queue = action_print_receiver.get_message_queue()
        result_dict["print"] = {"receiver": action_print_receiver, "queue": action_print_queue}
        file_writer_receiver = FileWriterReceiver(self._runtime_operator)
        file_writer_queue = file_writer_receiver.get_message_queue()
        result_dict["file"] = {"receiver": file_writer_receiver, "queue": file_writer_queue}
        return result_dict

    def _start_all_listener(self):
        for listener in self._all_listener.values():
            listener["receiver"].start()
