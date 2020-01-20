import sys
import logging


env = sys.modules[__name__]

# Public
env.data_log = dict()


# Private
blocks = dict()


def init(**kwargs):
    """
    This function must be called before starting simulation. It interprets the kwargs as simulation options,
    enabling those options that are valid, emitting a warning to the log if an option isn't recognised or valid,
    and raising Exceptions when the configuration as a whole is invalid and the simulation cannot be run. It does not
    return anything as simEnv is meant to be used as a 'global' module, where anything that imports simEnv has access
    to its variables.

    :param kwargs: kwargs that
    :return: None
    """

    if kwargs['solver'] == 'fixed_step':
        env.dt = kwargs['step_size']

    env.time = 0
    return env.time


def step():
    env.time += env.dt
    return env.time


class BlockData:
    """
    Data class that keeps track of block metadata. The only required values are the block id
    and the block type. The blocks can otherwise store whatever values they like in the class.
    """
    def __init__(self, id, type, **kwargs):
        self.id = id
        self.type = type
        for k,v in kwargs.items():
            self.__dict__[k] = v


def initialise_block_with_type(block_type):
    """
    Adds an entry to the blocks dict, and generates an id for the block.

    :param block_type:
    :return: BlockData object containing the initial metadata of the block
    """
    try:
        block_id = str(block_type) + str(len(blocks[block_type]))
    except KeyError:
        logging.error("Unknown block type {} was initialised.".format(block_type))

    block_metadata = BlockData(id=id, type=block_type)
    blocks[block_id] = block_metadata
    return block_metadata


def declare_block(make_block_fun):
    """
    A decorator function that announces to the simulation environment that
    blocks of its type exist. It also wraps the make_block function in a closure
    that allocates block ids at runtime.

    :param make_block_fun: function that creates the block.
    :return: closure containing the make_block fun
    """

    block_type = make_block_fun.__name__
    if not block_type.startswith('make_'):
        logging.warn(("The function "+ block_type + "() "
                     "has been declared a block, but "
                     "its name does not start with 'make_'. "
                     "This may make the logs harder to read."))
    else:
        block_type = block_type[4:]

    blocks[block_type] = []

    def fwrapper(*args, **kwargs):
        """
        Wrapper around the block creation function. Initialises the block metadata object
        and makes it available to the nested functions as the 'self' keyword, similar to
        javascript practices. 'this' was not used because the value does not change when
        entering the scope of nested functions, which might trip up someone used to
        Javascript.

        :param args: args that are passed on to make_block_fun
        :param kwargs: kwargs that are passed on to make_block_fun
        :return: The result of making the block (should be a function)
        """
        nonlocal block_type
        this = initialise_block_with_type(block_type)
        return make_block_fun(*args, **kwargs)

    return fwrapper