#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Create Time: 2020/3/12 14:16
# Create User: hya-machine
import io
import re
import queue
import pycurl


class ResponseHeaderHandler(object):
    def __init__(self):
        self._header_dict = {}

    def response_header_handler(self, each_header):
        temp_content = each_header.decode()
        temp_content = re.sub("[\r\n]", "", temp_content)
        if re.findall("HTTP/[\\d.]+ \\d+ \\w+", temp_content):
            self._header_dict.clear()
            self._header_dict["status"] = re.findall("HTTP/[\\d.]+ (\\d+) \\w+", temp_content)
        elif temp_content != "":
            key, value = temp_content.split(": ", 1)
            self._header_dict[key.lower()] = value

    def get_header_dict(self):
        return self._header_dict.copy()


class CurlHelper(object):
    def __init__(self, link, message_sender: queue.Queue, headers: dict = None, cookies: dict = None):
        self._headers = headers if headers is not None else {}
        self._cookies = cookies if cookies is not None else {}
        self._message_sender = message_sender
        self._link = link
        self._curl = None
        self._response_header_handler = ResponseHeaderHandler()

    def _init_base_headers_curl(self):
        format_header = ["{}: {}".format(key, value) for key, value in self._headers.items()]
        format_cookie = "; ".join(["{}={}".format(key, value) for key, value in self._cookies.items()])
        self._curl = pycurl.Curl()
        self._curl.setopt(pycurl.URL, self._link)
        self._curl.setopt(pycurl.CONNECTTIMEOUT, 10)
        self._curl.setopt(pycurl.TIMEOUT, 30)
        self._curl.setopt(pycurl.HTTPHEADER, format_header)
        self._curl.setopt(pycurl.COOKIE, format_cookie)
        self._curl.setopt(pycurl.SSL_VERIFYPEER, False)  # 设置忽略ssl

    def _follow_location_and_auto_referer(self):
        self._curl.setopt(pycurl.FOLLOWLOCATION, True)
        self._curl.setopt(pycurl.AUTOREFERER, True)
        self._curl.setopt(pycurl.NOBODY, True)

    def _set_only_receive_headers(self):
        self._curl.setopt(pycurl.VERBOSE, True)
        self._curl.setopt(pycurl.RANGE, "0-0")
        self._curl.setopt(pycurl.HEADERFUNCTION, self._response_header_handler.response_header_handler)
        self._curl.setopt(pycurl.WRITEDATA, None)

    def _get_value_from_response_header_handler(self, key):
        response_header_dict = self._response_header_handler.get_header_dict()
        return response_header_dict[key] if key in response_header_dict else None

    def _update_redirected_link(self):
        try:
            self._init_base_headers_curl()
            self._follow_location_and_auto_referer()
            self._perform_curl()
            self._link = self._curl.getinfo(pycurl.EFFECTIVE_URL)
            self._release_self_curl()
            return True
        except Exception as e:
            self._make_message_and_send(str(e))
            return False

    def get_final_location(self):
        try:
            self._init_base_headers_curl()
            self._follow_location_and_auto_referer()
            self._perform_curl()
            return self._curl.getinfo(pycurl.EFFECTIVE_URL)
        except Exception as e:
            self._make_message_and_send(str(e))
            return None

    def only_request_headers(self):
        try:
            if self._update_redirected_link():
                self._init_base_headers_curl()
                self._set_only_receive_headers()
                self._perform_curl()
                self._release_self_curl()
            else:
                self._make_message_and_send("获取有效下载链接失败，请检查网络后重试")
        except Exception as e:
            self._make_message_and_send(str(e))

    def analyse_response_header(self):
        headers = {"link": self._link,
                   "status": self._get_value_from_response_header_handler("status"),
                   "length": self._get_value_from_response_header_handler("content-length"),
                   "disposition": self._get_value_from_response_header_handler("content-disposition"),
                   "accept_ranges": self._get_value_from_response_header_handler("accept-ranges"),
                   "content_ranges": self._get_value_from_response_header_handler("content-range")}
        return headers

    def _perform_curl(self):
        self._curl.perform()

    def _release_self_curl(self):
        self._curl.close()
        self._curl = None

    def _make_message_and_send(self, content):
        message = {"sender": "CurlHelper", "title": "Network Connect Fail", "result": content}
        self._message_sender.put(message)
