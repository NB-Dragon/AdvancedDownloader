#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Create Time: 2021/4/25 12:00
# Create User: NB-Dragon
import re

from schema.Charset.Codecs.ASCII import ASCII


class GB18030(ASCII):
    def __init__(self):
        super().__init__()
        self._charset_name = "GB18030"
        self._ascii_filter_rule = b"[\x00-\x2F]"
        self._bytes_without_ascii_rule = b"[^\x00-\x2F]+"
        self._init_specification()

    def _init_specification(self):
        self._rule_list.append({"regex": b"[\x81-\xFE][\x40-\x7E\x80-\xFE]", "length": 2})
        self._rule_list.append({"regex": b"[\x81-\xFE][\x30-\x39][\x81-\xFE][\x30-\x39]", "length": 4})

    def _detect_match_count(self, byte_string: bytes):
        match_count = 0
        for rule in self._rule_list:
            tmp_result = re.findall(rule["regex"], byte_string)
            match_count += rule["length"] * len(tmp_result)
            byte_string = re.sub(rule["regex"], b"\x00", byte_string)
        match_count += len(re.findall(b"[\x30-\x7F]", byte_string))
        return match_count
