class Observation:
    def __init__(self, count, dead):
        self.x_distance = 0
        self.bird_height = 0
        self.y_distance_over_bottom = 0
        self.y_distance_below_upper = 0
        self.blocks_count = count
        self.dead_state = dead

    def set_relative_positions(self, positions):
        bottom_block, upper_block, bird_position = positions[0], positions[1], positions[2]
        self.x_distance = self.round_distance(upper_block[0] - bird_position[0])
        self.bird_height = self.round_distance(720 - bird_position[1])
        self.y_distance_over_bottom = self.round_distance(bottom_block[1] - bird_position[1] - bird_position[3])
        # negative if lower than gap
        self.y_distance_below_upper = self.round_distance(bird_position[1] - upper_block[1] - upper_block[3])
        # negative if higher than gap

    def get_relative_positions(self,):
        # x_distance = self.round_distance(self.upper_block[0] - self.bird_position[0])
        # bird_height = self.round_distance(720 - self.bird_position[1])
        # y_distance_over_bottom = self.round_distance(self.bottom_block[1] - self.bird_position[1] - self.bird_position[3]) #negative if lower than gap
        # y_distance_below_upper = self.round_distance(self.bird_position[1] - self.upper_block[1] - self.upper_block[3]) #negative if higher than gap
        # print(x_distance, y_distance_over_bottom, y_distance_below_upper, bird_height)
        return [self.x_distance, self.bird_height, self.y_distance_over_bottom, self.y_distance_below_upper]

    def round_distance(self, distance):
        scale = 5
        return (distance + scale // 2) // scale

    def get_dead_state(self):
        return self.dead_state

    def get_blocks_count(self):
        return self.blocks_count

    def equals(self, observation):
        return (self.get_relative_positions() == observation.get_relative_positions() and
                self.dead_state == observation.get_dead_state())

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
