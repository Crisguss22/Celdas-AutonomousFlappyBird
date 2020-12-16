from theory import Theory
from mutated_observation import MutatedObservation
import copy


class TheoryMutator:
    def __init__(self):
        self.x_limit = 1
        self.x_neg_limit = -1
        self.x_current_limit = 20
        self.x_current_neg_limit = -20

    def initialize_limits(self, mutant_theories):
        for theories in mutant_theories.values():
            self.update_x_limit(theories[0])

    def update_x_limit(self, theory):
        new_distance = self.get_x_distance(theory.get_theory_code())
        if self.x_current_limit > new_distance > 0:
            self.x_current_limit = new_distance
        elif self.x_current_neg_limit < new_distance < 0:
            self.x_current_neg_limit = new_distance

    def find_mutant_theories_applicable(self, mutant_theories, observation):
        mutated_code = self.find_mutated_code_on_x(mutant_theories, observation.get_code())
        if mutated_code in mutant_theories:
            return mutant_theories[mutated_code]
        else:
            return []

    def mutated_theory_available(self, mutant_theories, theory):
        mutated_code = self.find_mutated_code_on_x(mutant_theories, theory.get_theory_code())
        mutant_theory = None
        missing_action = False
        if mutated_code in mutant_theories:
            mutant_theory = self.find_mutant_equivalent(mutant_theories[mutated_code], theory)
            missing_action = mutant_theory is None
        return mutant_theory, missing_action

    def find_mutated_code_on_x(self, mutant_theories, theory_code):
        if self.code_is_within_current_x_mutation(theory_code):
            found = False
            found_code = None
            positive = self.get_x_distance(theory_code) > 0
            if positive:
                x_distance = self.x_current_limit
                step = 1
            else:
                x_distance = self.x_current_neg_limit
                step = -1
            while not found and -12 <= x_distance <= 12:
                possible_code = 'xd{0}ob{1}'.format(x_distance, theory_code.split('ob')[1])
                if possible_code in mutant_theories:
                    found = True
                    found_code = possible_code
                x_distance += step
            return found_code
        else:
            print('No no no')
            return None

    def find_old_mutated_code_on_x(self, mutant_theories, theory_code):
        if self.code_is_within_possible_x_mutation(theory_code):
            remaining_code = theory_code.split('ob')[1]
            code = None
            min_distance = self.x_current_limit
            max_distance = 10
            if self.get_x_distance(theory_code) < 0:
                min_distance = self.x_current_neg_limit
                max_distance = -10
            for x in range(min_distance, max_distance):
                possible_code = 'xd{0}ob{1}'.format(x, remaining_code)
                if possible_code in mutant_theories:
                    code = possible_code
            return code
        else:
            return None

    def mutate_new_code_on_x(self, theory_code):
        if self.code_is_within_possible_x_mutation(theory_code):
            new_x_distance = self.get_x_distance(theory_code)
            if new_x_distance > self.x_current_limit:
                x_distance = self.x_current_limit
            elif new_x_distance < self.x_current_neg_limit:
                x_distance = self.x_current_neg_limit
            else:
                x_distance = new_x_distance
            return 'xd{0}ob{1}'.format(x_distance, theory_code.split('ob')[1])
        else:
            return None

    def code_is_within_current_x_mutation(self, theory_code):
        x_distance = self.get_x_distance(theory_code)
        return x_distance >= self.x_current_limit or x_distance <= self.x_current_neg_limit

    def code_is_within_possible_x_mutation(self, theory_code):
        x_distance = self.get_x_distance(theory_code)
        return x_distance > self.x_limit or x_distance < self.x_neg_limit

    def get_x_distance(self, theory_code):
        return int(theory_code.split('ob')[0].split('d')[1])

    def new_mutation(self, mutant_theories, theory):
        mutant_theory, old_mutant_theory = None, None
        possible_code = self.mutate_new_code_on_x(theory.get_theory_code())
        if possible_code is not None:
            print('Possible MUTANT THEORY')
            old_code = self.find_old_mutated_code_on_x(mutant_theories, theory.get_theory_code())
            if old_code in mutant_theories:
                print('There was old MUTANT THEORY')
                old_mutant_theory = self.find_mutant_equivalent(mutant_theories[old_code], theory)
                mutant_theory = self.update_mutant_theory(old_mutant_theory, theory, possible_code)
            else:
                print('Brand new MUTANT THEORY')
                print('Possible code', possible_code)
                mutant_theory = self.create_mutant_theory(possible_code, theory)
            if mutant_theory is not None:
                self.update_x_limit(theory)
        return mutant_theory, old_mutant_theory

    def update_mutant_theory(self, old_mutant_theory, new_theory, possible_code):
        if old_mutant_theory is None:
            return None
        else:
            return self.merge_theories(old_mutant_theory, new_theory, possible_code)

    def create_mutant_theory(self, possible_code, new_theory):
        observation_before = MutatedObservation(possible_code)
        mutant_theory = copy.deepcopy(new_theory)
        mutant_theory.make_mutant()
        mutant_theory.set_observation_before(observation_before)
        return mutant_theory

    def find_mutant_equivalent(self, mutant_theories, theory):
        mutant_equivalent = None
        for existing_theory in mutant_theories:
            if self.theories_are_equivalent(existing_theory, theory):
                mutant_equivalent = existing_theory
        return mutant_equivalent

    def theories_are_equivalent(self, theory1, theory2):
        return theory1.get_utility() == theory2.get_utility() and theory1.get_jump() == theory2.get_jump()

    def mutation_for_new_action(self, mutant_theories, theory):
        mutated_code = self.find_mutated_code_on_x(mutant_theories, theory.get_theory_code())
        new_mutant_theory = copy.deepcopy(theory)
        new_mutant_theory.make_mutant()
        observation_before = MutatedObservation(mutated_code)
        new_mutant_theory.set_observation_before(observation_before)
        return new_mutant_theory

    def merge_theories(self, old_mutant_theory, new_theory, possible_code):
        observation_before = MutatedObservation(possible_code)
        total_uses = old_mutant_theory.get_times_used() + new_theory.get_times_used()
        new_mutant_theory = copy.deepcopy(new_theory)
        new_mutant_theory.make_mutant()
        new_mutant_theory.set_observation_before(observation_before)
        new_mutant_theory.set_uses(total_uses)
        return new_mutant_theory

    def get_current_limits(self):
        return [self.x_current_limit, self.x_current_neg_limit]

    def merge_all_theories(self, old_theories, current_theories):
        for i, old_theory in enumerate(old_theories):
            current_equivalent = self.find_mutant_equivalent(current_theories, old_theory)
            if current_equivalent is not None:
                total_uses = old_theory.get_times_used() + current_equivalent.get_times_used()
                current_equivalent.set_uses(total_uses)
                old_theories.pop(i)
        return len(old_theories) == 0
