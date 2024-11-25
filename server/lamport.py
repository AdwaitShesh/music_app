class LamportClock:
    def __init__(self):
        self.time = 0

    def increment(self):
        self.time += 1

    def receive_event(self, other_time):
        self.time = max(self.time, other_time) + 1

    def get_time(self):
        return self.time
