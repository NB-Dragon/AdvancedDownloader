#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Create Time: 2022/01/01 00:00
# Create User: NB-Dragon
import queue
import threading


class ThreadInteractModule(threading.Thread):
    def __init__(self):
        super().__init__()
        self._message_queue = queue.Queue()
        self._run_status = True

    def run(self) -> None:
        while self._should_thread_continue_to_execute():
            message_dict = self._message_queue.get()
            if message_dict is None: continue
            message_type, message_detail = message_dict["message_type"], message_dict["message_detail"]
            self._handle_message_detail(message_type, message_detail)

    def append_message(self, message):
        self._message_queue.put(message)

    def send_stop_state(self):
        self._run_status = False
        self.append_message(None)

    def _should_thread_continue_to_execute(self):
        return self._run_status or self._message_queue.qsize()

    def _handle_message_detail(self, message_type, message_detail):
        if message_type == "table":
            self._print_interactive_content(self._generate_table_content(message_detail))

    def _generate_table_content(self, message_detail):
        content_list = list()
        column_length_list = self._get_column_max_length(message_detail["rows"])
        if column_length_list is not None:
            table_row_split_content = self._generate_table_row_split_content(column_length_list)
            content_list.append(table_row_split_content)
            content_list.append(self._generate_table_header_content(message_detail["rows"], column_length_list))
            content_list.append(table_row_split_content)
            content_list.append(self._generate_table_body_content(message_detail["rows"], column_length_list))
            content_list.append(table_row_split_content)
            return "\n".join(content_list)
        else:
            return None

    def _get_column_max_length(self, row_content_list):
        if len(row_content_list) >= 2:
            result_list = [0] * len(row_content_list[0])
            for index in range(len(result_list)):
                current_column_list = [row_content[index] for row_content in row_content_list]
                result_list[index] = self._get_content_max_length(current_column_list)
            return result_list
        else:
            return None

    @staticmethod
    def _get_content_max_length(content_list: list):
        length_list = [len(content.encode()) for content in content_list]
        return max(length_list)

    @staticmethod
    def _generate_table_row_split_content(column_length_list: list):
        return "+-{}-+".format("-+-".join(["-" * length for length in column_length_list]))

    @staticmethod
    def _generate_row_content(content_list, column_length_list: list):
        result_list = []
        for index in range(len(content_list)):
            value = content_list[index]
            space = column_length_list[index] - len(value)
            result_list.append(" {}{} ".format(value, " " * space))
        return "|{}|".format("|".join(result_list))

    def _generate_table_header_content(self, row_content_list, column_length_list: list):
        header_list = row_content_list[0]
        return self._generate_row_content(header_list, column_length_list)

    def _generate_table_body_content(self, row_content_list, column_length_list: list):
        body_list = row_content_list[1:]
        result_list = [self._generate_row_content(body_item, column_length_list) for body_item in body_list]
        return "\n".join(result_list)

    @staticmethod
    def _print_interactive_content(content):
        if content is not None:
            print(content)
