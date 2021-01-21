import os
import sys
import queue
import threading

from listener.ActionPrintReceiver import ActionPrintReceiver


class ThreadMessageDistributor(threading.Thread):
    def __init__(self):
        super().__init__()
        self._code_entrance_path = os.path.split(os.path.abspath(sys.argv[0]))[0]
        self._all_listener = self._init_all_listener()
        self._message_queue = queue.Queue()
        self._run_status = True

    def run(self) -> None:
        self._start_all_listener()
        while self._run_status or self._message_queue.qsize():
            message_dict = self._message_queue.get()
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
        config: 1
        file  : 1
        """
        result_dict = dict()
        action_print_receiver = ActionPrintReceiver(self._code_entrance_path)
        action_print_queue = action_print_receiver.get_message_queue()
        result_dict["print"] = {"receiver": action_print_receiver, "queue": action_print_queue}
        return result_dict

    def _start_all_listener(self):
        for listener in self._all_listener.values():
            listener["receiver"].start()