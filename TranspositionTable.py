from Hashing import HashUtils

class TranspositionTable:
    def __init__(self):
        self.hasher = HashUtils()

    def store(self, position, eval=None, eval_type='exact'):
        key_lower, key_upper = self.hasher.key_split(self.hasher.to_str(position))
        