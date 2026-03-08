import time

class Clock:
    def __init__(self, fps):
        self.period = 1.0 / fps
        self.next_t = time.perf_counter()

    def tick(self):
        self.next_t += self.period
        sleep_s = self.next_t - time.perf_counter()
        if sleep_s > 0:
            time.sleep(sleep_s)
        else:
            self.next_t = time.perf_counter()
