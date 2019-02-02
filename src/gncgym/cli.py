import click
import inspect
import gncgym.scenarios.example_scenarios as scenarios
from gncgym.env.base import BaseShipScenario
from gncgym.play import play_scenario

@click.group()
def cli():
    """
    Entry point for the package when called from the command line. Defined as a Click command group, to enable
    the addition of new commands as the need arises.
    """
    pass


@cli.command()
@click.option('--model',
              default='supply_ship_3DOF',
              help='The name of the model that you want to simulate. This must refer to a '
                   'module in the models directory.')

@click.option('--scenario',
              default='ExampleScenario',
              help='The scenario that you want to run.')

@click.option('--controller',
              default='human',
              help='Name of module that defines a control module for the model. This module '
                   'uses the measured state to generate inputs to the model')

@click.option('--objective',
              default='path-following',
              help='A control objective for the model.')

@click.option('--disturbances',
              default='none',
              help='Name of module that defines disturbances to add to the simulation.'
                   'Support for disturbances is model dependent.')

@click.option('--observer',
              default='none',
              help='Measurement nodule. If you want to simulate noisy measurements or'
                   'experiment with different oberservers, this is the place to do it.')

def play(model, scenario, controller, objective, disturbances, observer):
    """

    :param model:
    :param scenario:
    :return:
    """
    play_scenario(scenario)


