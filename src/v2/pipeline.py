import logging

from importlib import import_module

class RCPipeline:
    def __init__(self, config=None):
        self.on_data = []
        self.on_save = []

        if "on_data" in config:
            self.on_data = self.load_modules(config["on_data"])
        
        if "on_save" in config:
            self.on_save = self.load_modules(config["on_save"])

    def load_modules(self, files):
        modules = []

        for file in files:
            try:
                modules.append(
                    import_module(file)
                )
            except Exception as e:
                logging.error(f"Could not import module from {file}: {e}")

        return modules

    def exec(self, event, data):
        match event:
            case "on_data":
                steps = self.on_data
            case "on_save":
                steps = self.on_save
            case _:
                steps = []

        results = []

        for step in steps:
            try:
                result = step.process(data)
                results.append(result)
            except Exception as e:
                logging.error(f"Pipeline step failed: {e}")

        return results
