#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Create Time: 2021/5/16 12:00
# Create User: NB-Dragon
from management.mission.thread.HTTPThread import HTTPThread
from tools.RuntimeOperator import RuntimeOperator


class ThreadController(object):
    def __init__(self, runtime_operator: RuntimeOperator, progress_queue):
        self._runtime_operator = runtime_operator
        self._progress_queue = progress_queue

    def get_thread_by_schema(self, schema):
        if schema == "http":
            return HTTPThread(schema, self._progress_queue, self._runtime_operator)
        elif schema == "https":
            return HTTPThread(schema, self._progress_queue, self._runtime_operator)
