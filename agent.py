import random
import math
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
        #print('-----------------')
        print("Cycles: ", self.action_counter)
        #print("Current Observation: ", self.current_observation.get_code())
        #print("Dead: ", self.flappybird.dead)
        print("Normal Theory count: ", self.theories_manager.theories_size()) #Not really theory count, actually scenarios theorized about

    def act(self):
        if self.turns_for_jump > 0:
            self.turns_for_jump -= 1
            self.bird_act(False)
            return
        self.observe_world()
        if self.current_theory is not None:
            self.update_theory()
        self.print_relevant()
        if self.current_observation.get_dead_state():
            self.current_theory = None
            self.bird_act(False)
        else:
            if self.action_counter > 1 and self.action_counter % 250 == 0:
                self.theories_manager.clean_theories()
            if self.action_counter > 1 and self.action_counter % 500 == 0:
                self.theories_manager.save_theories_to_json('theories_saved.json')
            jump = self.choose_action()
            self.action_counter += 1
            self.turns_for_jump = 4
            self.bird_act(jump)

    def choose_action(self):
        if self.action_counter < 150:
            self.act_from_theories_with_exploration(19)
        elif self.action_counter < 300:
            self.act_from_theories_with_exploration(10)
        elif self.action_counter < 500:
            self.act_from_theories_with_exploration(5)
        elif self.action_counter < 600:
            self.act_from_theories_with_exploration(2)
        else:
            self.act_from_theories_with_exploration(0)
        return self.current_theory.get_jump()

    def update_theory(self):
        theory_is_finished = self.current_theory.is_finished()
        theory_was_correct = self.current_theory.is_correct(self.current_observation) or self.current_theory.is_mutant()
        if theory_is_finished and theory_was_correct:
            self.theories_manager.update_theory(self.current_theory)
        elif theory_is_finished:
            new_theory = self.theories_manager.new_theory(self.current_theory.get_observation_before(), self.current_theory.get_jump())
            self.theories_manager.finish_and_add_theory(new_theory, self.current_observation, self.just_restarted)
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
            self.turns_for_jump = 9
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
        best_theory, both_actions_already_explored, death_actions = self.theories_manager.get_best_theory(self.current_observation)
        if best_theory is not None:
            theory_may_cause_death = death_actions[int(best_theory.get_jump())]
            if death_actions[0] and death_actions[1]:
                # theory_may_cause_death = False
                print('DEATH FOR BOTH ACTIONS')
            elif theory_may_cause_death:
                print('POSSIBLE DEATH!! IF JUMP IS ', best_theory.get_jump())
            if both_actions_already_explored or should_not_explore:
                self.current_theory = best_theory
                self.print_next_action('THEORY BASED: ')
            else:
                opposite_action = not best_theory.get_jump()
                self.current_theory = self.theories_manager.new_theory(self.current_observation, opposite_action)
                self.print_next_action('EXPLORING: ')
        else:
            self.random_act()

    def random_act(self):
        jump = self.my_random() == 2
        self.current_theory = self.theories_manager.new_theory(self.current_observation, jump)
        self.print_next_action('ACTING RANDOM: ')

    def print_next_action(self, theory_origin):
        print('-----')
        print(theory_origin, self.next_action())
        print('Theory code: ', self.current_theory.get_theory_code())
        print('Mutant: ', self.current_theory.is_mutant())
        print('-----')

    def next_action(self):
        if self.current_theory.get_jump():
            return 'JUMP'
        else:
            return 'FALL'
