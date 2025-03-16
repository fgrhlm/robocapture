import logging
import sys
import os

from importlib.util import module_from_spec, spec_from_file_location

class RCExtWorker:
    def __init__(self, name, config):
        self.name = name
        self.config = config
        logging.debug(f"Creating new worker: {self.name}")

def load_modules(config, event):
    mod_list = config.get(event)
    modules = []

    for n in mod_list:
        if not n["enabled"]:
            continue

        path = n["path"]
        name = n["name"]
        config = n["config"]

        if path in sys.modules:
            mod = sys.modules[path]
        else:
            spec = spec_from_file_location(name, path)
            mod = module_from_spec(spec)
            sys.modules[name] = mod
            spec.loader.exec_module(mod)

        modules.append(mod.ext(config))

    return modules

def run(ext_list, data):
    results = []
    for f in ext_list:
        result = f.process(data)
        results.append(result)

    return results
