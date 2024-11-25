class WeightedRoundRobin:
    def __init__(self, servers):
        self.servers = servers
        self.index = -1
        self.current_weight = 0

    def get_server(self):
        while True:
            self.index = (self.index + 1) % len(self.servers)
            if self.index == 0:
                self.current_weight -= 1
                if self.current_weight <= 0:
                    self.current_weight = max(server[2] for server in self.servers)

            if self.servers[self.index][2] >= self.current_weight:
                return self.servers[self.index][:2]
