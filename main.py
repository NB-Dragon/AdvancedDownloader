#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Create Time: 2022/01/01 00:00
from command.CommandHelper import CommandHelper
from helper.ProjectHelper import ProjectHelper
from module.message.MainProcessMessageModule import MainProcessMessageModule

if __name__ == "__main__":
    project_helper = ProjectHelper()
    command_helper = CommandHelper(project_helper.get_project_version())
    main_thread_message_module = MainProcessMessageModule(project_helper)
    main_thread_message_module.start()
    while True:
        command_message = command_helper.get_next_command_message()
        if isinstance(command_message, dict) and command_message["success"]:
            main_thread_message_module.get_message_queue().put(command_message["message"])
        elif command_message is None:
            main_thread_message_module.send_stop_message()
            break
