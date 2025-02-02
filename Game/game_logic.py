class GameState:
    def __init__(self):
        self.players = {}
        self.threats = []
        self.powerups = []
        self.scores = {}
        self.co2_reduced = {}
        self.energy_generated = {}

    def update_player_position(self, data):
        player_id = data.get('player_id')
        position = data.get('position')
        score = data.get('score', 0)
        co2_reduced = data.get('co2Reduced', 0)
        energy_generated = data.get('energyGenerated', 0)

        if player_id and position:
            self.players[player_id] = {
                'position': position,
                'score': score
            }
            self.scores[player_id] = score
            self.co2_reduced[player_id] = co2_reduced
            self.energy_generated[player_id] = energy_generated

    def process_shot(self, data):
        player_id = data.get('player_id')
        shot_data = data.get('shot')
        current_category = data.get('currentCategory')

        if player_id and shot_data:
            # Process shot collision and update scores
            self.check_collisions(player_id, shot_data, current_category)

    def check_collisions(self, player_id, shot_data, current_category):
        # Implement collision detection logic here if needed
        # This will be handled client-side in this implementation
        pass

    def get_state(self):
        return {
            'players': self.players,
            'threats': self.threats,
            'powerups': self.powerups,
            'scores': self.scores,
            'co2Reduced': self.co2_reduced,
            'energyGenerated': self.energy_generated
        }