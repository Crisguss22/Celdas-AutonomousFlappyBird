import random
import math
import numpy as np
from pprint import pprint
from flappybird import FlappyBird
from observation import Observation
from theories_manager import TheoriesManager

class Agent:
    def __init__(self):
        self.flappybird = FlappyBird()
        self.current_observation = None
        self.current_theory = None
        self.action_counter = 0
        self.theories_manager = TheoriesManager()
        self.theories_manager.get_theories_from_json('theories_saved.json')

    def init(self):    
        pass

    """
     * Method used to determine the next move to be performed by the agent.
     * now is moving random
     """

    def print_relevant(self):
        print("Cycles: ", self.action_counter)
        print("Current Observation: ", self.current_observation.get_code())
        print("Dead: ", self.flappybird.dead)
        print("Theory count: ", self.theories_manager.theories_size())

    def act(self):
        self.observe_world()
        if self.current_theory is not None:
            self.update_theory()
        self.print_relevant()
        if self.current_observation.get_dead_state():
            self.current_theory = None
            self.bird_act(False)
        else:
            if self.action_counter > 1 and self.action_counter % 20000 == 0:
                self.theories_manager.save_theories_to_json('theories_saved.json')
            jump = self.choose_action()
            self.action_counter += 1
            self.bird_act(jump)

    def choose_action(self):
        if self.action_counter < 5000:
            self.random_act()
        elif self.action_counter < 10000:
            self.semirandom_act()
        elif self.action_counter < 15000:
            self.act_from_theories_with_exploration()
        else:
            self.act_from_known_theories()
        return self.current_theory.get_jump()

    def update_theory(self):
        if self.current_theory.is_finished():
            self.theories_manager.add_or_update_theory(self.current_theory)
        else:
            self.theories_manager.finish_and_add_theory(self.current_theory, self.current_observation)

    def my_random(self):
        return random.randint(0, 20)

    def observe_world(self):
        positions = self.flappybird.getWorldPositionObjets()
        self.current_observation = Observation(self.flappybird.counter, self.flappybird.dead)
        self.current_observation.set_relative_positions(positions)

    def bird_act(self, jump):
        if jump:
            self.flappybird.holdKeyDown()
        else:
            self.flappybird.releaseKey()

    def run(self):  
        self.flappybird.initGame()
        while True:
            self.flappybird.eachCicle()            
            self.act()

    def random_act(self):
        jump = self.my_random() == 2
        print('Acting Random')
        self.current_theory = self.theories_manager.new_theory(self.current_observation, jump)

    def semirandom_act(self):
        if self.my_random() > 8:
            self.random_act()
        else:
            self.act_from_theories_with_exploration()

    def act_from_theories_with_exploration(self):
        theory, multiple_theories = self.theories_manager.get_best_theory(self.current_observation)
        if theory is not None:
            if multiple_theories:
                print('Theory Based')
                self.current_theory = theory
            else:
                print('Exploring')
                self.current_theory = self.theories_manager.new_theory(self.current_observation, not theory.get_jump())
        else:
            self.random_act()

    def act_from_known_theories(self):
        theory, multiple_theories = self.theories_manager.get_best_theory(self.current_observation)
        if theory is not None:
            print('Theory Based')
            self.current_theory = theory
        else:
            self.random_act()
