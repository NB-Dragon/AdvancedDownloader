#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Create Time: 2021/1/25 10:00
# Create User: NB-Dragon
import queue
import threading
from tools.RuntimeOperator import RuntimeOperator
from management.worker.ActionAnalyzeReceiver import ActionAnalyzeReceiver
from management.worker.ActionOpenReceiver import ActionOpenReceiver
from management.worker.ActionPrintReceiver import ActionPrintReceiver
from management.worker.ActionSpeedReceiver import ActionSpeedReceiver
from management.worker.ActionWriterReceiver import ActionWriterReceiver


class WorkerMessageDistributor(threading.Thread):
    def __init__(self, runtime_operator: RuntimeOperator, parent_queue: queue.Queue):
        super().__init__()
        self._runtime_operator = runtime_operator
        self._message_queue = queue.Queue()
        self._run_status = True
        self._parent_queue = parent_queue
        self._init_all_listener()

    def run(self) -> None:
        self._start_all_listener()
        while self._should_thread_continue_to_execute():
            message_dict = self._message_queue.get()
            if message_dict is None: continue
            self._handle_message(message_dict)
        self._do_before_distributor_down()
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
        if first_receiver == "parent":
            self._parent_queue.put(raw_message)
        elif first_receiver in self._all_listener:
            self._all_listener[first_receiver]["queue"].put(raw_message)

    def _handle_same_level_receiver(self, action_type, action_receiver, action_detail):
        self._do_with_action_signal(action_receiver, action_detail)

    def _do_with_action_signal(self, action_receiver, action_detail):
        if action_receiver in self._all_listener:
            self._all_listener[action_receiver]["queue"].put(action_detail)
        else:
            message_content = "signal_receiver `{}` not defined".format(action_receiver)
            self._send_message_to_print(message_content, False)

    def _do_before_distributor_down(self):
        if not self._all_listener["open"]["receiver"].is_command_installed():
            file_path = self._runtime_operator.get_static_donate_image_path()
            message_content = "The sponsored QR code image path is: {}".format(file_path)
            self._send_message_to_print(message_content, False)

    def _init_all_listener(self):
        """
        print   : handle all message which need to print
        write   : handle all file register and writing
        open    : handle all the files open operation
        speed   : handle all the changes in file size
        analyze : handle all the mission analyze
        """
        self._all_listener = dict()
        action_print_receiver = ActionPrintReceiver(self._runtime_operator)
        action_print_queue = action_print_receiver.get_message_queue()
        self._all_listener["print"] = {"receiver": action_print_receiver, "queue": action_print_queue}
        action_write_receiver = ActionWriterReceiver(self._runtime_operator, self._message_queue)
        action_write_queue = action_write_receiver.get_message_queue()
        self._all_listener["write"] = {"receiver": action_write_receiver, "queue": action_write_queue}
        action_open_receiver = ActionOpenReceiver(self._runtime_operator, self._message_queue)
        action_open_queue = action_open_receiver.get_message_queue()
        self._all_listener["open"] = {"receiver": action_open_receiver, "queue": action_open_queue}
        action_speed_receiver = ActionSpeedReceiver(self._runtime_operator, self._message_queue)
        action_speed_queue = action_speed_receiver.get_message_queue()
        self._all_listener["speed"] = {"receiver": action_speed_receiver, "queue": action_speed_queue}
        action_analyze_receiver = ActionAnalyzeReceiver(self._runtime_operator, self._message_queue)
        action_analyze_queue = action_analyze_receiver.get_message_queue()
        self._all_listener["analyze"] = {"receiver": action_analyze_receiver, "queue": action_analyze_queue}

    def _start_all_listener(self):
        for listener in self._all_listener.values():
            listener["receiver"].start()

    def _stop_all_listener(self):
        for listener in self._all_listener.values():
            listener["receiver"].send_stop_state()

    def _send_message_to_print(self, content, exception: bool):
        message_item = self._generate_print_value(content, exception)
        self._all_listener["print"]["queue"].put(message_item)

    @staticmethod
    def _generate_print_value(content, exception: bool):
        message_type = "exception" if exception else "normal"
        message_detail = {"sender": "ThreadMessageDistributor", "content": content}
        return {"type": message_type, "mission_uuid": None, "detail": message_detail}