#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Create Time: 2022/01/01 09:00
# Create User: NB-Dragon
import urllib.parse
import urllib3


class NetworkRequestHelper(object):
    def __init__(self, ca_cert_path, timeout):
        self._ca_cert_path = ca_cert_path
        self._timeout = timeout
        self._init_request_tool()

    def get_request_manager(self, target_link, alive_count, proxy):
        schema_name = self._get_link_schema(target_link)
        if schema_name in ["http", "https"]:
            request_tool = self._request_tool["http(s)"]
            return request_tool.get_http_manager(schema_name, alive_count, proxy)
        else:
            return None

    def get_connect_client(self, request_manager, target_link, headers):
        if isinstance(request_manager, urllib3.PoolManager):
            request_tool = self._request_tool["http(s)"]
            return request_tool.get_http_client(request_manager, target_link, headers)
        return {"client": None, "error": "Unknown request manager"}

    def _init_request_tool(self):
        self._request_tool = dict()
        self._request_tool["http(s)"] = HTTPRequestTool(self._ca_cert_path, self._timeout)

    @staticmethod
    def _get_link_schema(target_link):
        link_parse_result = urllib.parse.urlparse(target_link)
        return link_parse_result.scheme


class HTTPRequestTool(object):
    def __init__(self, ca_cert_path, timeout):
        self._ca_cert_path = ca_cert_path
        self._timeout = timeout

    def get_http_manager(self, schema_name, alive_count, proxy):
        if proxy is None or len(proxy) == 0:
            return self._generate_http_normal_manager(alive_count)
        else:
            proxy_url = "{}://{}".format(schema_name, proxy)
            return self._generate_http_proxy_manager(alive_count, proxy_url)

    @staticmethod
    def get_http_client(request_manager, target_link, headers):
        try:
            connect_client = request_manager.request("GET", target_link, headers=headers, preload_content=False)
            if connect_client.status in [200, 206]:
                return {"client": connect_client, "error": None}
            else:
                message = "The response status code not in {200, 206}"
                return {"client": connect_client.close(), "error": message}
        except UnicodeEncodeError:
            message = "The server does not follow internet standards."
            return {"client": None, "error": message}
        except Exception as e:
            return {"client": None, "error": str(e)}

    def _generate_http_normal_manager(self, alive_count):
        return urllib3.PoolManager(cert_reqs='CERT_REQUIRED', ca_certs=self._ca_cert_path,
                                   timeout=self._timeout, maxsize=alive_count)

    def _generate_http_proxy_manager(self, alive_count, proxy_url):
        return urllib3.ProxyManager(cert_reqs='CERT_REQUIRED', ca_certs=self._ca_cert_path,
                                    timeout=self._timeout, maxsize=alive_count, proxy_url=proxy_url)
