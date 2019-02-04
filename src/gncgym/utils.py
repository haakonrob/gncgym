import os
import inspect
import importlib
import numpy as np


def distance(p1, p2):
    return np.sqrt((float(p1[0]) - float(p2[0]))**2 + (float(p1[1]) - float(p2[1]))**2)


def rotate(vec, angle):
    if isinstance(vec, np.ndarray):
        vec = vec.flatten()
    angle = float(angle)
    return (vec[0]*np.cos(angle) - vec[1]*np.sin(angle), vec[1]*np.cos(angle) + vec[0]*np.sin(angle))


def flatten(li):
    return [i for i in dfs(li)] if not isinstance(li, np.ndarray) else li.flatten()


def between(x, a, b):
    return (a > b and a > x > b) or (a < b and a < x < b)


def sign(x):
    # No zero on purpose
    return 1 if x > 0 else -1


def dfs(li):
    for i in li:
        if type(li) is not list and type(li) is not tuple:
            yield i
        else:
            for j in dfs(i):
                yield j


def auto_load_classes(module_path, class_type):
    import gncgym

    module_path = tuple(module_path)
    gncgym_src_path = os.path.dirname(gncgym.__file__)
    assert(module_path[0] == 'gncgym')
    root_dir = os.path.join(*((gncgym_src_path,) + module_path[1:]))

    def scan(path=root_dir, mpath=module_path):
        discovered_classes = dict()
        for p in os.scandir(path):
            name, ext = os.path.splitext(p.name)
            if p.is_dir():
                # Recurse into the folder
                scan(p.path, mpath + (name,))
            elif p.is_file() and ext == '.py' and name != '__init__' and name != 'model':
                # Load the file as a module and scan it for Model subclasses
                module = importlib.import_module('.'.join(mpath + (name,)))
                for k, v in module.__dict__.items():
                    if inspect.isclass(v) and issubclass(v, class_type) and v != class_type:
                        discovered_classes[k] = v
        return discovered_classes

    return scan()
