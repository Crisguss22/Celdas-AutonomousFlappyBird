import math


class Observation:
    def __init__(self, count, dead):
        self.x_distance = 0
        self.x_distance_s = 0
        self.bird_height = 0
        self.bird_height_s = 0
        self.y_distance_over_bottom = 0
        self.y_distance_over_bottom_s = 0
        self.y_distance_below_upper = 0
        self.y_distance_below_upper_s = 0
        self.blocks_count = count
        self.dead_state = dead

    def just_restarted(self, positions):
        return (self.dead_state is False and
                self.blocks_count == 0 and
                positions[0][0] > 385)

    def set_relative_positions(self, positions):
        bottom_block, upper_block, bird_position = positions[0], positions[1], positions[2]
        self.x_distance = upper_block[0] - bird_position[0]
        self.bird_height = 720 - bird_position[1]
        self.y_distance_over_bottom = bottom_block[1] - bird_position[1] - bird_position[3] - 5
        # negative if lower than gap
        self.y_distance_below_upper = bird_position[1] - upper_block[1] - upper_block[3]
        # negative if higher than gap
        self.simplify_relative_positions()

    def simplify_relative_positions(self):
        self.x_distance_s = self.weird_extra_scale_distance(self.x_distance)
        self.bird_height_s = self.round_distance(self.bird_height, 20)
        self.y_distance_over_bottom_s = self.weird_scale_distance(self.y_distance_over_bottom)
        self.y_distance_below_upper_s = self.weird_scale_distance(self.y_distance_below_upper)

    def get_relative_positions(self):
        return [self.x_distance, self.bird_height, self.y_distance_over_bottom, self.y_distance_below_upper]

    def get_simplified_relative_positions(self):
        return [self.x_distance_s, self.bird_height_s, self.y_distance_over_bottom_s, self.y_distance_below_upper_s]

    def round_distance(self, distance, scale):
        return (distance + scale // 2) // scale

    def weird_scale_distance(self, distance):
        if -6 < distance < 6:
            return distance
        negative = distance < 0
        distance_round_down = math.ceil(math.log(abs(distance), 1.61)) + 2
        if negative:
            return distance_round_down * -1
        else:
            return distance_round_down

    def weird_extra_scale_distance(self, distance):
        if -90 < distance < 90:
            return 0
        negative = distance < 0
        distance_round_down = math.ceil(math.log(abs(distance), 2)) + 84
        if negative:
            return distance_round_down * -1
        else:
            return distance_round_down

    def get_dead_state(self):
        return self.dead_state

    def get_blocks_count(self):
        return self.blocks_count

    def equals(self, observation):
        return self.get_code() == observation.get_code()

    def get_code(self):
        return 'xd{0}ob{1}bu{2}de{3}'.format(self.x_distance_s, self.y_distance_over_bottom_s, self.y_distance_below_upper_s, int(self.dead_state))

    @classmethod
    def from_hash(cls, json):
        blocks_count = json['blocks_count']
        dead_state = json['dead_state']
        new_observation = cls(blocks_count, dead_state)
        new_observation.set_x_distance(json['x_distance'])
        new_observation.set_bird_height(json['bird_height'])
        new_observation.set_y_distance_over_bottom(json['y_distance_over_bottom'])
        new_observation.set_y_distance_below_upper(json['y_distance_below_upper'])
        new_observation.simplify_relative_positions()
        return new_observation

    def to_hash(self):
        return {
            'x_distance': int(self.x_distance),
            'bird_height': int(self.bird_height),
            'y_distance_over_bottom': int(self.y_distance_over_bottom),
            'y_distance_below_upper': int(self.y_distance_below_upper),
            'blocks_count': int(self.blocks_count),
            'dead_state': int(self.dead_state)
        }

    def set_x_distance(self, x_distance):
        self.x_distance = x_distance

    def set_bird_height(self, bird_height):
        self.bird_height = bird_height

    def set_y_distance_over_bottom(self, y_distance_over_bottom):
        self.y_distance_over_bottom = y_distance_over_bottom

    def set_y_distance_below_upper(self, y_distance_below_upper):
        self.y_distance_below_upper = y_distance_below_upper
