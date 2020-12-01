import math


class Observation:
    def __init__(self, count, dead):
        self.x_distance = 0
        self.bird_height = 0
        self.y_distance_over_bottom = 0
        self.y_distance_below_upper = 0
        self.blocks_count = count
        self.dead_state = dead

    def just_restarted(self, positions):
        return (self.dead_state is False and
                self.blocks_count == 0 and
                positions[0][0] > 385)

    def set_relative_positions(self, positions):
        bottom_block, upper_block, bird_position = positions[0], positions[1], positions[2]
        self.x_distance = self.weird_scale_distance(upper_block[0] - bird_position[0])
        self.bird_height = self.round_distance(720 - bird_position[1], 5)
        self.y_distance_over_bottom = self.weird_scale_distance(bottom_block[1] - bird_position[1] - bird_position[3])
        # negative if lower than gap
        self.y_distance_below_upper = self.weird_scale_distance(bird_position[1] - upper_block[1] - upper_block[3])
        # negative if higher than gap

    def get_relative_positions(self,):
        return [self.x_distance, self.bird_height, self.y_distance_over_bottom, self.y_distance_below_upper]

    def round_distance(self, distance, scale):
        return (distance + scale // 2) // scale

    def weird_scale_distance(self, distance):
        if -40 < distance < 40:
            return self.round_distance(distance, 2)
        negative = distance < 0
        distance_round_down = self.round_distance(abs(distance), 5) + 21
        if negative:
            return distance_round_down * -1
        else:
            return distance_round_down

    def log_scale_distance(self, distance):
        if -2 < distance < 2:
            return distance
        negative = distance < 0
        distance_scaled = math.ceil(math.log(abs(distance), 1.15))
        if negative:
            return distance_scaled * -1
        else:
            return distance_scaled

    def get_dead_state(self):
        return self.dead_state

    def get_blocks_count(self):
        return self.blocks_count

    def equals(self, observation):
        return self.get_code() == observation.get_code()

    def get_code(self):
        return 'xd{0}bh{1}ob{2}bu{3}de{4}'.format(self.x_distance, self.bird_height, self.y_distance_over_bottom, self.y_distance_below_upper, int(self.dead_state))

    @classmethod
    def from_hash(cls, json):
        blocks_count = json['blocks_count']
        dead_state = json['dead_state']
        new_observation = cls(blocks_count, dead_state)
        new_observation.set_x_distance(json['x_distance'])
        new_observation.set_bird_height(json['bird_height'])
        new_observation.set_y_distance_over_bottom(json['y_distance_over_bottom'])
        new_observation.set_y_distance_below_upper(json['y_distance_below_upper'])
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
