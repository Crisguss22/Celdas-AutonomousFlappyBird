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
        self.just_restarted = False
        self.turns_for_jump = 0

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
        print("Theory count: ", self.theories_manager.theories_size()) #Not really theory count, just based on hash code

    def act(self):
        if self.turns_for_jump > 0:
            self.turns_for_jump -= 1
            self.bird_act(False)
            return
        print('-----------------')
        self.observe_world()
        if self.current_theory is not None:
            self.update_theory()
        self.print_relevant()
        if self.action_counter == 200:
            self.theories_manager.save_theories_to_json('theories_saved.json')
        if self.current_observation.get_dead_state():
            self.current_theory = None
            self.bird_act(False)
        else:
            if self.action_counter > 1 and self.action_counter % 2000 == 0:
                self.theories_manager.save_theories_to_json('theories_saved.json')
            jump = self.choose_action()
            self.action_counter += 1
            self.turns_for_jump = 1
            self.bird_act(jump)

    def choose_action(self):
        if self.action_counter < 2000:
            self.act_from_theories_with_exploration(19)
        elif self.action_counter < 4000:
            self.act_from_theories_with_exploration(10)
        elif self.action_counter < 6000:
            self.act_from_theories_with_exploration(5)
        else:
            self.act_from_theories_with_exploration(1)
        return self.current_theory.get_jump()

    def update_theory(self):
        theory_is_finished = self.current_theory.is_finished()
        theory_was_correct = self.current_theory.is_correct(self.current_observation)
        if theory_is_finished and theory_was_correct:
            self.theories_manager.update_theory(self.current_theory)
        else:
            self.theories_manager.finish_and_add_theory(self.current_theory, self.current_observation, self.just_restarted)

    def my_random(self):
        return random.randint(0, 20)

    def observe_world(self):
        positions = self.flappybird.getWorldPositionObjets()
        self.current_observation = Observation(self.flappybird.counter, self.flappybird.dead)
        self.current_observation.set_relative_positions(positions)
        self.just_restarted = self.current_observation.just_restarted(positions)

    def bird_act(self, jump):
        if jump:
            self.turns_for_jump = 2
            self.flappybird.holdKeyDown()
        else:
            self.flappybird.releaseKey()

    def run(self):  
        self.flappybird.initGame()
        while True:
            self.flappybird.eachCicle()            
            self.act()

    def act_from_theories_with_exploration(self, probability):
        should_not_explore = self.my_random() > probability
        best_theory, both_actions_already_explored = self.theories_manager.get_best_theory(self.current_observation)
        if best_theory is not None:
            if both_actions_already_explored or should_not_explore:
                print('THEORY BASED: ', best_theory.get_jump())
                self.current_theory = best_theory
            else:
                opposite_action = not best_theory.get_jump()
                print('EXPLORING: ', opposite_action)
                self.current_theory = self.theories_manager.new_theory(self.current_observation, opposite_action)
        else:
            self.random_act()

    def random_act(self):
        jump = self.my_random() == 2
        print('ACTING RANDOM: ', jump)
        self.current_theory = self.theories_manager.new_theory(self.current_observation, jump)
