import sys
from gncgym.utils import auto_load_classes

this = sys.modules[__name__]

this.available_objectives = None


def autoload():
    """
    Function to automatically load and import classes that are defined in the scenarios folder. References to the
    discovered scenarios are saved in scenarios.available_scenarios
    :return dict: Contains the discovered scenario classes in the scenarios folder, indexed by class name
    """
    from gncgym.objectives.objective import ControlObjective

    if this.available_objectives is None:
        this.available_objectives = auto_load_classes(['gncgym', 'objectives'], ControlObjective)
    return this.available_objectives
