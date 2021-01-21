import os
import sys
import json


class RuntimeOperator(object):
    def __init__(self):
        self._code_entrance_path = os.path.split(os.path.abspath(sys.argv[0]))[0]
        self._cache_directory = os.path.join(self._code_entrance_path, ".cache")
        self._check_cache_directory()
        self._setup_cache_inner_file()

    def get_mission_dict(self):
        if os.path.isfile(self._cache_inner_file["mission"]):
            file_content = self._get_file_content(self._cache_inner_file["mission"])
            if len(file_content):
                return json.loads(file_content)
            else:
                return None
        else:
            return None

    def set_mission_file(self, mission_dict):
        json_content = json.dumps(mission_dict)
        writer = open(self._cache_inner_file["mission"], 'w')
        writer.write(json_content)
        writer.close()

    def get_cache_file(self, file_type: str):
        return self._cache_inner_file[file_type]

    def _check_cache_directory(self):
        if not os.path.exists(self._cache_directory):
            os.mkdir(self._cache_directory)

    def _setup_cache_inner_file(self):
        self._cache_inner_file = dict()
        self._cache_inner_file["mission"] = os.path.join(self._cache_directory, "mission.json")
        self._cache_inner_file["log"] = os.path.join(self._cache_directory, "log.txt")

    @staticmethod
    def _get_file_content(file_path):
        reader = open(file_path, 'r')
        content = reader.read()
        reader.close()
        return content
