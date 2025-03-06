import logging
import sys
import os

from importlib import import_module
from dataclasses import dataclass

# https://www.geeksforgeeks.org/how-to-dynamically-load-modules-or-classes-in-python/
# https://stackoverflow.com/questions/67631/how-can-i-import-a-module-dynamically-given-the-full-path
# https://docs.python.org/3/library/dataclasses.html
# https://stackoverflow.com/questions/47558704/python-dynamic-import-methods-from-file

@dataclass
class RCPipelineResult:
    name: str
    data: list

class RCPipeline:
    def __init__(self, config=None):
        self.config = config
        self.on_data = []
        self.on_save = []

        if "on_data" in self.config["pipeline"]:
            logging.debug("Loading 'on_data' pipeline steps..")
            self.on_data = self.load_modules(config["pipeline"]["on_data"])
        
        if "on_save" in self.config["pipeline"]:
            logging.debug("Loading 'on_save' pipeline steps..")
            self.on_save = self.load_modules(config["pipeline"]["on_save"])

    def load_modules(self, mod_list):
        logging.debug(f"Pipeline steps in config: {' '.join([n for n in mod_list])}")
        modules = []
       
        for i,mod_path in enumerate(mod_list):
            logging.debug(f"[{i+1}/{len(mod_list)}] Importing module from {mod_path}..")
            if mod_path in sys.modules:
                mod = sys.modules[mod_path]
            else:
                mod = import_module(mod_path)

            # Append pipeline step instance to list
            step = mod.step(self.config)
            logging.debug(f"[{i+1}/{len(mod_list)}] Adding module {step.name} to pipeline!")
            modules.append(step)
            
            logging.debug(f"[{i+1}/{len(mod_list)}] {step.name} loaded from {mod_path}!")

        loaded_mods = " ".join([n.name for n in modules])
        logging.debug(f"Loaded pipeline modules: {loaded_mods}")

        return modules

    def exec(self, event, data):
        logging.debug(f"{event} event triggered!")

        match event:
            case "on_data":
                steps = self.on_data
            case "on_save":
                steps = self.on_save
            case _:
                steps = []

        results = []

        for i,step in enumerate(steps):
            logging.debug(f"Pipeline exec: {step.name or i}")
            try:
                result = step.process(data)
                results.append(result)
            except Exception as e:
                logging.error(f"Pipeline step failed: {e}")

        return results
