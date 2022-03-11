#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Create Time: 2021/05/01 18:00
# Create User: NB-Dragon
from core.charset.encoding.ASCII import ASCII


class GB18030(ASCII):
    def __init__(self):
        super().__init__()
        self._charset_name = "GB18030"
        self._ascii_filter_rule = b"[\x00-\x2F]"
        self._ascii_extend_rule = b"[\x30-\x7F]"
        self._ascii_outside_rule = b"[^\x00-\x2F]+"
        self._init_specification()

    def _init_specification(self):
        self._rule_list.append({"regex": b"[\x81-\xFE][\x40-\x7E\x80-\xFE]", "length": 2})
        self._rule_list.append({"regex": b"[\x81-\xFE][\x30-\x39][\x81-\xFE][\x30-\x39]", "length": 4})
