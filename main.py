#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Create Time: 2022/01/01 00:00
from helper.CommandHelper import CommandHelper
from helper.ProjectHelper import ProjectHelper
from module.message.ThreadMessageModule import ThreadMessageModule

if __name__ == "__main__":
    project_helper = ProjectHelper()
    command_helper = CommandHelper(project_helper)
    thread_message_module = ThreadMessageModule(project_helper)
    thread_message_module.start()
    while True:
        command_message = command_helper.get_next_command_message()
        if isinstance(command_message, dict) and command_message["success"]:
            thread_message_module.append_message(command_message["message"])
        elif command_message is None:
            thread_message_module.send_stop_state()
            break
