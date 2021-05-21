#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Create Time: 2021/5/16 12:00
# Create User: NB-Dragon
import queue
from controller.analyzer.HTTPAnalyzer import HTTPAnalyzer
from tools.RuntimeOperator import RuntimeOperator


class AnalyzeController(object):
    def __init__(self, runtime_operator: RuntimeOperator, parent_queue: queue.Queue):
        self._runtime_operator = runtime_operator
        self._parent_queue = parent_queue
        self._init_all_analyzer()
        self._check_all_analyzer()

    def _init_all_analyzer(self):
        self._all_analyser = dict()
        self._all_analyser["http"] = HTTPAnalyzer("http", self._parent_queue, self._runtime_operator)
        self._all_analyser["https"] = HTTPAnalyzer("https", self._parent_queue, self._runtime_operator)

    def _check_all_analyzer(self):
        for analyzer in self._all_analyser.values():
            method = analyzer.get_download_info
            method = analyzer.get_current_finish_size

    def get_analyzer(self, schema):
        return self._all_analyser.get(schema)
