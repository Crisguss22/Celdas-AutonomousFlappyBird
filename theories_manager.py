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
        self.theory_mutator.initialize_limits(self.mutant_theories)

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
        theories_json = {'theories': self.theories_hash(self.theories),
                         'mutant_theories': self.theories_hash(self.mutant_theories)}
        return theories_json

    def theories_hash(self, theories):
        theories_hash = {}
        for code in theories.keys():
            theories_for_code = []
            for theory in theories[code]:
                theories_for_code.append(theory.to_hash())
            theories_hash[code] = theories_for_code
        return theories_hash

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
        mutant_code = self.theory_mutator.find_mutated_code_on_x(self.mutant_theories, theory_code)
        best_theory = None
        both_actions_already_explored = False
        death_actions = [False, False]
        if mutant_code in self.mutant_theories:
            both_actions_already_explored = len(self.explored_actions(self.mutant_theories[mutant_code])) == 2
            best_theory, death_actions = self.theory_with_greatest_utility(self.mutant_theories[mutant_code])
        need_more_search = best_theory is None or best_theory.get_utility() < 0 or not both_actions_already_explored
        if theory_code in self.theories and need_more_search:
            both_actions_already_explored = len(self.explored_actions(self.theories[theory_code])) == 2
            best_theory, death_actions = self.theory_with_greatest_utility(self.theories[theory_code])
        return best_theory, both_actions_already_explored, death_actions

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
        if theory.get_times_used() < 3:
            return
        added = self.add_to_mutants(theory)
        if added:
            self.remove_normal_theory(theory)

    def add_to_mutants(self, theory):
        mutant_theory, missing_action = self.theory_mutator.mutated_theory_available(self.mutant_theories, theory)
        if mutant_theory is not None:
            mutant_theory.add_use()
        elif missing_action:
            mutant_theory = self.theory_mutator.mutation_for_new_action(self.mutant_theories, theory)
            self.add_or_replace_mutant_theory(None, mutant_theory)
        else:
            mutant_theory, old_mutant_theory = self.theory_mutator.new_mutation(self.mutant_theories, theory)
            self.add_or_replace_mutant_theory(old_mutant_theory, mutant_theory)
        return mutant_theory is not None

    def print_relevant(self, theory):
        if theory is None:
            return
        print('-----------------')
        print("Theory Code: ", theory.get_theory_code())
        print("Current Mut Limits: ", self.theory_mutator.get_current_limits())
        print("Mutant Theory count: ", len(self.mutant_theories))
        print('-----------------')

    def remove_normal_theory(self, theory):
        self.remove_theory(theory, self.theories)

    def remove_mutant_theory(self, theory):
        self.remove_theory(theory, self.mutant_theories)

    def remove_theory(self, theory, theories):
        key = theory.get_theory_code()
        print('-----------------')
        print("REMOVIIIING: ", key)
        print('-----------------')
        theories_for_context = theories[key]
        index = -1
        for i, th in enumerate(theories_for_context):
            if th.equals(theory):
                index = i
        if index >= 0:
            theories_for_context.pop(index)
        if len(theories_for_context) == 0:
            theories.pop(key)

    def add_or_replace_mutant_theory(self, theory_to_delete, new_mutant_theory):
        if new_mutant_theory is None:
            return
        new_code = new_mutant_theory.get_theory_code()
        if new_code not in self.mutant_theories:
            self.mutant_theories[new_code] = []
        self.mutant_theories[new_code].append(new_mutant_theory)
        if theory_to_delete is None:
            return
        else:
            self.remove_mutant_theory(theory_to_delete)

    def clean_theories(self):
        self.clean_mutant_theories()
        self.reduce_normal_theories()

    def clean_mutant_theories(self):
        print('------------------')
        print('CLEANING MUTANTS!!')
        print('Before count: ', len(self.mutant_theories))
        keys_to_delete = []
        for code in self.mutant_theories.keys():
            mutated_code = self.theory_mutator.find_mutated_code_on_x(self.mutant_theories, code)
            if mutated_code != code:
                print('About to merge ', code, ' into ', mutated_code)
                all_merged = self.theory_mutator.merge_all_theories(self.mutant_theories[code], self.mutant_theories[mutated_code])
                if all_merged:
                    keys_to_delete.append(code)
        print(keys_to_delete)
        for key in keys_to_delete:
            self.mutant_theories.pop(key)
        print('After count: ', len(self.mutant_theories))
        print('------------------')

    def reduce_normal_theories(self):
        print('------------------')
        print('CLEANING NORMALS!!')
        print('Before count: ', len(self.theories))
        for code in self.theories.keys():
            self.theories[code] = self.compressed_theories(self.theories[code])
        print('After count: ', len(self.theories))
        print('------------------')

    def compressed_theories(self, theories):
        final_theories = []
        jump_theories = []
        fall_theories = []
        for theory in theories:
            if theory.get_jump():
                jump_theories.append(theory)
            else:
                fall_theories.append(theory)
        if len(fall_theories) > 0:
            fall_theory = self.merged_theory(fall_theories)
            if fall_theory.get_utility() == -1000:
                fall_theory.set_utility(-999)
            final_theories.append(fall_theory)
        if len(jump_theories) > 0:
            jump_theory = self.merged_theory(jump_theories)
            final_theories.append(jump_theory)
        return final_theories

    def merged_theory(self, theories):
        print('-------')
        first_theory = theories[0]
        if len(theories) > 1:
            print(first_theory.get_theory_code())
            for i in range(1, len(theories)-1):
                theory = theories[i]
                print(theory.get_theory_code())
                total_uses = theory.get_times_used() + first_theory.get_times_used()
                first_theory_causes_death = first_theory.get_utility() < -50
                if (-50 > theory.get_utility() or theory.get_utility() > 0) and not first_theory_causes_death:
                    first_theory = theory
                first_theory.set_uses(total_uses)
            print(first_theory.get_theory_code())
        print('-------')
        return first_theory
