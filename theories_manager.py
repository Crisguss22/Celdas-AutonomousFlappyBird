import json
import random
import os.path
from theory import Theory
from theory_mutator import TheoryMutator


class TheoriesManager:
    def __init__(self):
        self.theories = {}
        self.mutant_theories = {}
        self.theory_mutator = TheoryMutator()

    def get_theories_from_json(self, file_name):
        theories_already_exist = os.path.isfile(file_name)
        if not theories_already_exist:
            return None
        with open(file_name, 'r') as f:
            theories_json = json.load(f)
        self.theories = self.load_theories(theories_json, 'theories')
        self.mutant_theories = self.load_theories(theories_json, 'mutant_theories')

    def load_theories(self, full_json, theory_type):
        theories_json = full_json[theory_type]
        loaded_theories = {}
        for code in theories_json.keys():
            theories = []
            for theory_json in theories_json[code]:
                theories.append(Theory.from_hash(theory_json, code))
            loaded_theories[code] = theories
        return loaded_theories

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
        if theory.is_mutant():
            theory.add_use()
            return
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
        self.update_mutant_theories(theory)

    def update_theory(self, theory):
        if theory.is_mutant():
            theory.add_use()
            return
        key = theory.get_theory_code()
        if key in self.theories:
            theories_for_context = self.theories[key]
            existing_theory = self.theory_already_exists(theories_for_context, theory)
            if existing_theory is not None:
                existing_theory.add_use()
        self.update_mutant_theories(theory)

    def calculate_theory_utility(self, theory, just_restarted):
        new_state = theory.get_observation_after()
        if new_state.get_dead_state():
            return -1000
        if just_restarted:
            return -100
        previous_state = theory.get_observation_before()
        if self.was_pushed_back(previous_state, new_state):
            return -100
        else:
            return self.evaluate_distance_to_gap(previous_state, new_state)

    def theory_already_exists(self, theories, theory):
        existing_theory = None
        for th in theories:
            if th.equals(theory):
                existing_theory = th
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

    def update_mutant_theories(self, theory):
        if theory.get_times_used() < 5:
            return
        added = self.add_to_mutants()
        if added:
            self.remove_theory(theory)

    def add_to_mutants(self, theory):
        mutant_theory, missing_action = self.theory_mutator.mutated_theory_available(self.mutant_theories, theory)
        if mutant_theory is not None:
            mutant_theory.add_use()
        elif missing_action:
            mutant_theory = self.theory_mutator.mutation_for_new_action(theory)
            self.add_or_replace_mutant_theory(None, mutant_theory)
        else:
            mutant_theory, old_mutant_theory = self.theory_mutator.new_mutation(self.theories, self.mutant_theories, theory)
            self.add_or_replace_mutant_theory(old_mutant_theory, mutant_theory)
        return mutant_theory is not None

    def remove_normal_theory(self, theory):
        self.remove_theory(theory, self.theories)

    def remove_mutant_theory(self, theory):
        self.remove_theory(theory, self.mutant_theories)

    def remove_theory(self, theory, theories):
        key = theory.get_theory_code()
        theories_for_context = theories[key]
        index = -1
        for i, th in enumerate(theories_for_context):
            if th.equals(theory):
                index = i
        if index >= 0:
            theories_for_context.pop(index)

    def add_or_replace_mutant_theory(self, theory_to_delete, new_mutant_theory):
        if new_mutant_theory is None:
            return
        new_code = new_mutant_theory.get_theory_code()
        self.mutant_theories[new_mutant_theory.get_theory_code()] = new_mutant_theory
        if new_code not in self.mutant_theories:
            self.mutant_theories[new_code] = []
        self.mutant_theories[new_code].append(new_mutant_theory)
        if theory_to_delete is None:
            return
        else:
            self.remove_mutant_theory(theory_to_delete)
