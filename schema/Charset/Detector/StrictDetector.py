#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Create Time: 2021/4/26 12:00
# Create User: NB-Dragon
import codecs
from schema.Charset.Codecs.UTF8 import UTF8
from schema.Charset.Codecs.GB2312 import GB2312
from schema.Charset.Codecs.GBK import GBK
from schema.Charset.Codecs.GB18030 import GB18030


class StrictDetector(object):
    def __init__(self):
        self._detector_list = list()
        self._init_detector_list()

    def _init_detector_list(self):
        self._detector_list.append(UTF8())
        self._detector_list.append(GB2312())
        self._detector_list.append(GBK())
        self._detector_list.append(GB18030())

    @staticmethod
    def check_bom_header(byte_string: bytes):
        if byte_string.startswith(codecs.BOM_UTF8):
            return {"charset": "UTF8", "confidence": 1}
        elif byte_string.startswith((codecs.BOM_UTF16_LE, codecs.BOM_UTF16_BE)):
            return {"charset": "UTF16", "confidence": 1}
        elif byte_string.startswith((codecs.BOM_UTF32_LE, codecs.BOM_UTF32_BE)):
            return {"charset": "UTF32", "confidence": 1}
        elif byte_string.startswith(b'\xFE\xFF\x00\x00'):
            return {"charset": "X-ISO-10646-UCS-4-3412", "confidence": 1}
        elif byte_string.startswith(b'\x00\x00\xFF\xFE'):
            return {"charset": "X-ISO-10646-UCS-4-3412", "confidence": 1}
        return None

    def check_deeper_content(self, byte_string: bytes):
        maximum_detector = {"charset": "iso-8859-1", "confidence": 0}
        for detector in self._detector_list:
            detect_result = detector.detect(byte_string)
            if detect_result["confidence"] == 1:
                return detect_result
            if detect_result["confidence"] > maximum_detector["confidence"]:
                maximum_detector = detect_result
        return maximum_detector
