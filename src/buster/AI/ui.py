import sys
import threading
import time


# UX functions for CLI
def visual_loading(messages: list[str]):
    terminal = sys.stdout
    task_events = [threading.Event() for _ in messages]
    progress_done = threading.Event()

    # Custom callback to signal task completion from CrewAI tasks
    def on_task_done(task_output):
        for task_event in task_events:
            if not task_event.is_set():
                task_event.set()
                break

    # Custom animated loading spinner wheel
    def visual_processing():
        spinning_wheel = "|/-\\"
        for message, task_event in zip(messages, task_events):
            terminal.write(f"{message}... ")
            terminal.flush()
            frame_index = 0
            while not task_event.is_set():
                terminal.write(spinning_wheel[frame_index % 4])
                terminal.flush()
                time.sleep(0.1)
                terminal.write("\b \b")
                terminal.flush()
                frame_index += 1
            terminal.write(" DONE!\n")
            terminal.flush()
        progress_done.set()

    def finish():
        for task_event in task_events:
            task_event.set()
        progress_done.wait(timeout=2)

    threading.Thread(target=visual_processing, daemon=True).start()
    return on_task_done, finish
