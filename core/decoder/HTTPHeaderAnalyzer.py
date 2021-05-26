#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Create Time: 2021/5/16 12:00
# Create User: NB-Dragon
import os
import re
import urllib.parse
import urllib3
from core.decoder.ContentDisposition import ContentDisposition
from tools.RuntimeOperator import RuntimeOperator


class HTTPHeaderAnalyzer(object):
    def __init__(self, runtime_operator: RuntimeOperator):
        self._runtime_operator = runtime_operator
        self._content_disposition = ContentDisposition()

    def generate_resource_info(self, headers, link):
        filename = self._get_download_file_name(headers, link)
        filesize = self._get_download_file_size(headers)
        range_skill = self._judge_download_range_skill(headers, filesize)
        return {"filename": filename, "filesize": filesize, "range": range_skill}

    @staticmethod
    def get_url_after_quote(link):
        return urllib.parse.quote(link, safe=":/?#[]@!$&'()*+,;=%")

    def get_request_manager(self, schema, alive_count, proxy=None):
        cert_pem_file = self._runtime_operator.get_static_cert_path()
        if proxy is None or len(proxy) == 0:
            return urllib3.PoolManager(cert_reqs='CERT_REQUIRED', ca_certs=cert_pem_file,
                                       maxsize=alive_count, timeout=5)
        else:
            proxy_url = "{}://{}".format(schema, proxy)
            return urllib3.ProxyManager(cert_reqs='CERT_REQUIRED', ca_certs=cert_pem_file,
                                        maxsize=alive_count, timeout=5, proxy_url=proxy_url)

    def _get_download_file_name(self, headers, link):
        content_disposition = headers.get("content-disposition")
        content_type = headers.get("content-type")
        if content_disposition and "filename" in content_disposition:
            result = self._content_disposition.generate_parm_dict(content_disposition)
            filename = result["param"]["filename"]
        else:
            link_parse_result = urllib.parse.urlparse(link)
            filename = link_parse_result.path.split("/")[-1]
            filename = self._content_disposition.parse_unquote_value(filename)
        filename = self._get_default_file_name(content_type, filename)
        return filename

    def _get_default_file_name(self, content_type, current_name):
        if "." in current_name:
            name, postfix = os.path.splitext(current_name)
        elif len(current_name):
            name, postfix = current_name, ".dat"
        else:
            name, postfix = "unknown", ".dat"
        correct_postfix = self._find_correct_postfix(content_type)
        postfix = correct_postfix or postfix
        return "{}{}".format(name, postfix)

    def _find_correct_postfix(self, content_type):
        default_postfix = self._runtime_operator.get_content_type_postfix()
        for key, value in default_postfix.items():
            if key in content_type:
                return value
        return None

    @staticmethod
    def _get_download_file_size(headers):
        if "content-range" in headers:
            return int(re.findall("bytes \\d+-\\d+/(\\d+)", headers["content-range"])[0])
        elif "content-length" in headers:
            return int(headers.get("content-length"))
        else:
            return None

    @staticmethod
    def _judge_download_range_skill(headers, filesize):
        has_range_header = "content-range" in headers or "accept-ranges" in headers
        return isinstance(filesize, int) and has_range_header
