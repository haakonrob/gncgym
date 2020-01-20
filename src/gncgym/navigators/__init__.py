import sys
from gncgym.utils import auto_load_classes

this = sys.modules[__name__]

this.available_navigators = None


def autoload():
    """
    Function to automatically load and import classes that are defined in the scenarios folder. References to the
    discovered scenarios are saved in scenarios.available_scenarios
    :return dict: Contains the discovered scenario classes in the scenarios folder, indexed by class name
    """
    from gncgym.navigators.navigator import Navigator

    if this.available_navigators is None:
        this.available_navigators = auto_load_classes(['gncgym', 'navigators'], Navigator)
    return this.available_navigators
