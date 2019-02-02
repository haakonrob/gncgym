from .model_definitions import Model

import os
import sys
import importlib

this = sys.modules[__name__]

this.available_models = dict()


def autoload():
    """
    Function to automatically load and import classes that are defined in the models folder. References to the
    discovered models are saved in scenarios.available_models.
    :return dict: Contains the discovered model classes in the models folder, indexed by class name.
    """

    def scan(path, module_path=('gncgym', 'models')):
        for p in os.scandir(path):
            name, ext = os.path.splitext(p.name)
            if p.is_dir():
                # Recurse into the folder
                scan(p.path, module_path+(name,))
            elif p.is_file() and ext == '.py' and name != '__init__' and name != 'definitions':
                # Load the file as a module and scan it for Model subclasses
                module = importlib.import_module('.'.join(module_path + (name,)))
                for k, v in module.__dict__.items():
                    if inspect.isclass(v) and issubclass(v, Model) and v != Model:
                        this.available_models[k] = v

    import inspect
    from os.path import abspath
    from inspect import getsourcefile
    this.available_models = dict()
    model_dir = os.path.dirname(abspath(getsourcefile(lambda: 0)))  # Find the directory of this file
    scan(model_dir)

    return this.available_models
