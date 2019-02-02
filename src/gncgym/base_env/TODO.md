
## Summary of what base.py does (and should do)
+ Entry point for the environment, so it is in charge of 'stepping' the environment
+ Initiates rendering of the environment
+ Performs collision detection
 
## What base.py does, but shouldn't 
+ Renders indicators directly (move to new module)
+ Calculates observed obstacles (move to observer, this must take in the environment state somehow, list of objects?)
+ Generates background (new module, possibly with indicators)
    + This could also later be extended to visualise disturbances, so maybe new env_rendering file
+ Tracks errors
    + Move this to the objective module, then the errors to use and reward signal can be swapped out
+ Stops the simulation when reward is too low or when a collision happens, this is also something for objective to do

## TODO for the base gncgym environment
+ Separate the rendering from base.py
    + Move indicator drawing into indicator.py
    + Move object drawing into objects.py
+ BaseScenario should implement a control loop containing:
    + **Plant** (model to be simulated)
    + **Objective module**: class that contains the trajectory, and that transforms the measurements/actual state into
      an error signal. Replaces the sum node in typical control diagrams.
    + **Optional observer**: this module simulates sensors, if needed. Takes in the real state and disturbance signals, 
      and returns some kind of measurement.
    + **Optional disturbance source**: Module that generates a disturbance signal and applies it to the model. The model
      must support this kind of disturbance of course.
    + **Optional controller** (this will be in series with whatever is actually running the environment and applying 
    actions to it.)
+ BaseScenario should then call a simplified rendering class to draw the current state of the environment

  
