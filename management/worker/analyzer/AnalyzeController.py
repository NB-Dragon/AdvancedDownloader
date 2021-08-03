#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Create Time: 2021/5/16 12:00
# Create User: NB-Dragon
from management.worker.analyzer.HTTPAnalyzer import HTTPAnalyzer
from tools.RuntimeOperator import RuntimeOperator


class AnalyzeController(object):
    def __init__(self, runtime_operator: RuntimeOperator, parent_message):
        self._runtime_operator = runtime_operator
        self._parent_message = parent_message
        self._init_all_analyzer()
        self._check_all_analyzer()

    def _init_all_analyzer(self):
        self._all_analyzer = dict()
        self._all_analyzer["http"] = HTTPAnalyzer("http", self._parent_message, self._runtime_operator)
        self._all_analyzer["https"] = HTTPAnalyzer("https", self._parent_message, self._runtime_operator)

    def _check_all_analyzer(self):
        title_message = "schema for '{}' doesn't have method 'get_download_info'."
        for schema, analyzer in self._all_analyzer.items():
            assert hasattr(analyzer, "get_download_info"), title_message.format(schema)

    def get_analyzer_by_schema(self, schema):
        return self._all_analyzer.get(schema)
