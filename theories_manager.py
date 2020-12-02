import json
import random
import os.path
from theory import Theory


class TheoriesManager:
    def __init__(self):
        self.theories = {}
        self.mutant_theories = {}

    def get_theories_from_json(self, file_name):
        theories_already_exist = os.path.isfile(file_name)
        if not theories_already_exist:
            return None
        with open(file_name, 'r') as f:
            theories_json = json.load(f)
        loaded_theories = {}
        for code in theories_json.keys():
            theories = []
            for theory_json in theories_json[code]:
                theories.append(Theory.from_hash(theory_json))
            loaded_theories[code] = theories
        self.theories = loaded_theories

    def save_theories_to_json(self, file_name):
        data = self.theories_to_json()
        with open(file_name, 'w') as f:
            json.dump(data, f)

    def theories_to_json(self):
        theories_json = {}
        for code in self.theories.keys():
            theories = []
            for theory in self.theories[code]:
                theories.append(theory.to_hash())
            theories_json[code] = theories
        return theories_json

    def theories_size(self):
        return len(self.theories)

    def new_theory(self, observation, action_jump):
        return Theory(observation, action_jump)

    def finish_and_add_theory(self, theory, observation, just_restarted):
        self.finish_theory(theory, observation, just_restarted)
        self.add_or_update_theory(theory)

    def finish_theory(self, theory, new_observation, just_restarted):
        theory.set_observation_after(new_observation)
        utility = self.calculate_theory_utility(theory, just_restarted)
        theory.set_utility(utility)
        theory.set_uses(1)

    def add_or_update_theory(self, theory):
        key = theory.get_theory_code()
        if key in self.theories:
            theories_for_context = self.theories[key]
            existing_theory = self.theory_already_exists(theories_for_context, theory)
            if existing_theory is not None:
                existing_theory.add_use()
            else:
                theories_for_context.append(theory)
        else:
            self.theories[key] = [theory]

    def update_theory(self, theory):
        key = theory.get_theory_code()
        if key in self.theories:
            theories_for_context = self.theories[key]
            existing_theory = self.theory_already_exists(theories_for_context, theory)
            if existing_theory is not None:
                existing_theory.add_use()

    def calculate_theory_utility(self, theory, just_restarted):
        new_state = theory.get_observation_after()
        if new_state.get_dead_state():
            return -1000
        if just_restarted:
            return -100
        previous_state = theory.get_observation_before()
        if new_state.get_blocks_count() > previous_state.get_blocks_count():
            return 20
        elif self.was_pushed_back(previous_state, new_state):
            return -100
        else:
            return self.evaluate_distance_to_gap(previous_state, new_state)

    def theory_already_exists(self, theories, theory):
        existing_theory = None
        for i in theories:
            if i.equals(theory):
                existing_theory = i
        return existing_theory

    def was_pushed_back(self, previous_state, new_state):
        previous_positions = previous_state.get_relative_positions()
        new_positions = new_state.get_relative_positions()
        return new_positions[0] > previous_positions[0] > 0

    def evaluate_distance_to_gap(self, previous_state, new_state):
        prev_distance = self.calculate_distance_to_gap(previous_state.get_relative_positions())
        new_distance = self.calculate_distance_to_gap(new_state.get_relative_positions())
        if new_distance < prev_distance:
            return 10
        elif new_distance == prev_distance:
            return 1
        else:
            return -5

    def calculate_distance_to_gap(self, rel_positions):
        # TODO: improve calculation, now too hardcodey
        over_bottom = rel_positions[2]
        below_upper = rel_positions[3]
        return over_bottom ** 2 + below_upper ** 2

    def get_best_theory(self, observation):
        theory_code = observation.get_code()
        best_theory = None
        both_actions_already_explored = False
        theory_may_cause_death = False
        if theory_code in self.theories:
            both_actions_already_explored = len(self.explored_actions(self.theories[theory_code])) == 2
            best_theory, theory_may_cause_death = self.theory_with_greatest_utility(self.theories[theory_code])
        return best_theory, both_actions_already_explored, theory_may_cause_death

    def explored_actions(self, theories):
        actions = []
        for theory in theories:
            actions.append(theory.get_jump())
        return set(actions)

    def theory_with_greatest_utility(self, candidate_theories):
        greatest_utility_theory = candidate_theories[0]
        # weird trick to avoid some loops
        if random.randint(0, 2) == 2:
            index = len(candidate_theories) - 1
            greatest_utility_theory = candidate_theories[index]
        death_actions = [False, False]
        for possible_theory in candidate_theories:
            if possible_theory.get_utility() < -50 and possible_theory.get_times_used() > 50:
                death_actions[int(possible_theory.get_jump())] = True
            if possible_theory.get_utility() > greatest_utility_theory.get_utility():
                greatest_utility_theory = possible_theory
        return greatest_utility_theory, death_actions
