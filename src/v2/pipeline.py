class RCPipeline:
    def __init__(self, stages: list):
        self.stages: list = stages

    def add(self, stage):
        self.stages.append(stage)

    def get(n=0):
        if n == 0:
            return self.stages
        else:
            return self.stages[n]


