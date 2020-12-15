from theory import Theory
from mutated_observation import MutatedObservation
import copy


class TheoryMutator:
    def __init__(self):
        self.x_limit = 10
        self.x_neg_limit = -10
        self.x_current_limit = 100
        self.x_current_neg_limit = -100

    def mutated_theory_available(self, mutant_theories, theory):
        mutated_code = self.find_mutated_code_on_x(theory.get_theory_code())
        mutant_theory = None
        missing_action = False
        if mutated_code in mutant_theories:
            mutant_theory = self.find_mutant_equivalent(mutant_theories[mutated_code], theory)
            missing_action = mutant_theory is None
        return mutant_theory, missing_action

    def find_mutated_code_on_x(self, theory_code):
        if self.code_is_within_current_x_mutation(theory_code):
            distance = self.x_current_limit
            if self.get_x_distance(theory_code) < 0:
                distance = self.x_current_neg_limit
            return 'xd{0}ob{1}'.format(distance, theory_code.split('ob')[1])
        else:
            return None

    def mutate_new_code_on_x(self, theory_code):
        if self.code_is_within_possible_x_mutation(theory_code):
            new_x_distance = self.get_x_distance(theory_code)
            return 'xd{0}ob{1}'.format(new_x_distance, theory_code.split('ob')[1])
        else:
            return None

    def code_is_within_current_x_mutation(self, theory_code):
        x_distance = self.get_x_distance(theory_code)
        return x_distance >= self.x_current_limit or x_distance <= self.x_current_neg_limit

    def code_is_within_possible_x_mutation(self, theory_code):
        x_distance = self.get_x_distance(theory_code)
        return x_distance >= self.x_limit or x_distance <= self.x_neg_limit

    def get_x_distance(self, theory_code):
        return theory_code.split('ob')[0].split('d')[1]

    def new_mutation(self, normal_theories, mutant_theories, theory):
        mutant_theory, old_mutant_theory = None, None
        possible_code = self.mutate_new_code_on_x(theory.get_theory_code())
        if possible_code is not None:
            old_code = self.find_mutated_code_on_x(theory.get_theory_code())
            if old_code in mutant_theories:
                old_mutant_theory = self.find_mutant_equivalent(mutant_theories[old_code], theory)
                mutant_theory = self.update_mutant_theory(old_mutant_theory, theory)
            else:
                mutant_theory = self.create_mutant_theory(possible_code, theory)
            self.update_x_limit(theory)
        return mutant_theory, old_mutant_theory

    def update_mutant_theory(self, old_mutant_theory, new_theory):
        if old_mutant_theory is None:
            return None
        else:
            return self.merge_theories(old_mutant_theory, new_theory)

    def create_mutant_theory(self, possible_code, new_theory):
        observation_before = MutatedObservation(possible_code)
        mutant_theory = copy.deepcopy(new_theory)
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

    def mutation_for_new_action(self, theory):
        mutated_code = self.find_mutated_code_on_x(theory.get_theory_code())
        new_mutant_theory = copy.deepcopy(theory)
        new_mutant_theory.make_mutant()
        observation_before = MutatedObservation(mutated_code)
        new_mutant_theory.set_observation_before(observation_before)
        return new_mutant_theory

    def update_x_limit(self, theory):
        new_distance = self.get_x_distance(theory.get_theory_code())
        if new_distance > 0:
            self.x_current_limit = new_distance
        else:
            self.x_current_neg_limit = new_distance

    def merge_theories(self, old_mutant_theory, new_theory):
        mutant_observation_before = old_mutant_theory.get_observation_before()
        total_uses = old_mutant_theory.get_uses() + new_theory.get_uses()
        new_mutant_theory = copy.deepcopy(new_theory)
        new_mutant_theory.set_observation_before(mutant_observation_before)
        new_mutant_theory.set_uses(total_uses)
        return new_mutant_theory
