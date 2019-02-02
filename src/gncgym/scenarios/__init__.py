import os
import sys
import importlib

this = sys.modules[__name__]

this.available_scenarios = dict()


def autoload():
    """
    Function to automatically load and import classes that are defined in the scenarios folder. References to the
    discovered scenarios are saved in scenarios.available_scenarios
    :return dict: Contains the discovered scenario classes in the scenarios folder, indexed by class name
    """
    def scan(path, module_path=('gncgym', 'scenarios')):
        for p in os.scandir(path):
            name, ext = os.path.splitext(p.name)
            if p.is_dir():
                # Recurse into the folder
                scan(p.path, module_path+(name,))
            elif p.is_file() and ext == '.py' and name != '__init__' and name != 'model':
                # Load the file as a module and scan it for Model subclasses
                module = importlib.import_module('.'.join(module_path + (name,)))
                for k, v in module.__dict__.items():
                    if inspect.isclass(v) and issubclass(v, BaseShipScenario) and v != BaseShipScenario:
                        this.available_scenarios[k] = v
                        
    from gncgym.base_env.base import BaseShipScenario
    import inspect
    from os.path import abspath
    from inspect import getsourcefile
    this.available_scenarios = dict()
    scenario_dir = os.path.dirname(abspath(getsourcefile(lambda: 0)))  # Find the directory of this file
    scan(scenario_dir)

    for p in os.scandir(scenario_dir):
        name, ext = os.path.splitext(p.name)
        if p.is_file() and ext == '.py' and not p.name == '__init__.py':
            # Load the file as a module and scan it for BaseScenario subclasses
            module = importlib.import_module('gncgym.scenarios.{}'.format(name))
            for k, v in module.__dict__.items():
                if inspect.isclass(v) and issubclass(v, BaseShipScenario) and v != BaseShipScenario:
                    this.available_scenarios[k] = v

    return this.available_scenarios