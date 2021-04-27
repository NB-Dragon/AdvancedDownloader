#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Create Time: 2021/4/25 20:00
# Create User: NB-Dragon
from schema.Charset.Detector.StrictDetector import StrictDetector

strict_detector = StrictDetector()


def detect(byte_string: bytes):
    byte_string = byte_string[0:1000]
    check_result = strict_detector.check_bom_header(byte_string)
    if check_result is None:
        check_result = strict_detector.check_deeper_content(byte_string)
    return check_result
