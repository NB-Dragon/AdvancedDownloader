# Thread
> All thread tools must implement the following functions.

## start_download_mission
> @:param send_worker_write_register: inform writer worker to register.<br>
> @:method create_thread_for_section: create section thread and start.<br>
> @:method track_thread_until_complete: Ensure that all threads end normally.<br>
> @:param send_worker_write_finish: inform writer worker to finish.<br>
> @:method return_download_message: Tell the parent thread whether it ended normally.