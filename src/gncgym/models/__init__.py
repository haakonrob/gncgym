from .model_definitions import Model
from gncgym.utils import auto_load_classes

import os
import sys
import importlib

this = sys.modules[__name__]

this.available_models = None


def autoload():
    """
    Function to automatically load and import classes that are defined in the scenarios folder. References to the
    discovered scenarios are saved in scenarios.available_scenarios
    :return dict: Contains the discovered scenario classes in the scenarios folder, indexed by class name
    """
    if this.available_models is None:
        this.available_models = auto_load_classes(['gncgym', 'models'], class_type=Model)
    return this.available_models
