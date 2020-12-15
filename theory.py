from observation import Observation
from mutated_observation import MutatedObservation


class Theory:
    def __init__(self, observation, jump):
        self.observation_before = observation
        self.jump = jump
        self.observation_after = None
        self.utility = 0
        self.times_used = 0
        self.mutant = False

    @classmethod
    def from_hash(cls, json, code):
        mutant = json['mutant']
        if mutant:
            observation_before = MutatedObservation(code)
        else:
            observation_before = Observation.from_hash(json['observation_before'])
        jump = json['jump']
        new_theory = cls(observation_before, jump)
        observation_after = Observation.from_hash(json['observation_after'])
        new_theory.set_observation_after(observation_after)
        new_theory.set_utility(json['utility'])
        new_theory.set_uses(json['times_used'])
        return new_theory

    def get_observation_before(self):
        return self.observation_before

    def get_jump(self):
        return self.jump

    def get_observation_after(self):
        return self.observation_after

    def get_utility(self):
        return self.utility

    def get_times_used(self):
        return self.times_used

    def set_observation_after(self, observation):
        self.observation_after = observation

    def set_observation_before(self, observation):
        self.observation_before = observation

    def set_utility(self, utility):
        self.utility = utility

    def add_use(self):
        self.times_used += 1

    def set_uses(self, uses):
        self.times_used = uses

    def is_mutant(self):
        return self.mutant

    def make_mutant(self):
        self.mutant = True

    def get_theory_code(self):
        return self.observation_before.get_code()

    def equals(self, theory):
        if theory is None:
            return False
        return (self.observation_before.equals(theory.get_observation_before()) and
                self.observation_after.equals(theory.get_observation_after()) and
                self.jump == theory.get_jump())

    def is_finished(self):
        return (self.observation_after is not None and
                self.times_used > 0 and
                self.utility != 0)

    def is_correct(self, actual_observation):
        if self.observation_after is None:
            return False
        return self.observation_after.equals(actual_observation)

    def to_hash(self):
        return {
            'observation_before': self.observation_before.to_hash(),
            'jump': self.jump,
            'mutant': self.mutant,
            'observation_after': self.observation_after.to_hash(),
            'utility': int(self.utility),
            'times_used': int(self.times_used)
        }
