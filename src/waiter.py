import time

class Waiter:
    def __init__(self, debug=False, wait_time=10) -> None:
        self.wait_time = wait_time
        self.last_waited = time.perf_counter() - wait_time 
        self.debug = debug

    def wait(self) -> None:
        time_since = time.perf_counter() - self.last_waited
        if time_since < self.wait_time:
            if self.debug: print("Waiting for", self.wait_time - time_since)
            time.sleep(self.wait_time - time_since)
        self.last_waited = time.perf_counter()