import time

class Latency:
    def __init__(self):
        self.t0 = time.time()

    def ms(self):
        return (time.time() - self.t0) * 1000.0
