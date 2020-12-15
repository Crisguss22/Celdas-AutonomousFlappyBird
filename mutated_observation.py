import math


class MutatedObservation:
    def __init__(self, code):
        self.x_distance_s = 0
        self.bird_height_s = 0
        self.y_distance_over_bottom_s = 0
        self.y_distance_below_upper_s = 0
        self.initialize_from_code(code)
        self.blocks_count = 0
        self.dead_state = False

    def just_restarted(self, positions):
        return (self.dead_state is False and
                self.blocks_count == 0 and
                positions[0][0] > 385)

    def get_simplified_relative_positions(self):
        return [self.x_distance_s, self.y_distance_over_bottom_s, self.y_distance_below_upper_s]

    def get_dead_state(self):
        return self.dead_state

    def get_blocks_count(self):
        return self.blocks_count

    def equals(self, observation):
        return self.get_code() == observation.get_code()

    def get_code(self):
        return 'xd{0}ob{1}bu{2}de{3}'.format(self.x_distance_s, self.y_distance_over_bottom_s, self.y_distance_below_upper_s, int(self.dead_state))

    def to_hash(self):
        return {
            'mutant_code': self.get_code()
        }

    def initialize_from_code(self, code):
        self.x_distance_s = int(code.split('ob')[0].split('d')[1])
        remaining = code.split('ob')[1]
        self.y_distance_over_bottom_s = int(remaining.split('bu')[0])
        remaining = remaining.split('bu')[1]
        self.y_distance_below_upper_s = int(remaining.split('de')[0])
