import click
import inspect
import gncgym.scenarios.example_scenarios as scenarios
from gncgym.base_env.base import BaseScenario
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

def play(model, scenario):
    """

    :param model:
    :param scenario:
    :return:
    """
    play_scenario(scenario)


@cli.command()
def make():
    import gym

    env = gym.make('shipExampleScenario-v0')
