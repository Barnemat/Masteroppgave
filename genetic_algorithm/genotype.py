

class Genotype:

    def __init__(self, num_syllables, key, measures=None):
        # For eks. delt opp i measures, time-steps og noter
        # Measures [[[[a, 4]], [[a\', 16], [d\,, 8], [a, 16]], [[a, 8], [R, 8]], [a, 4]], [[[]...]...]
        # Melisma med en gang?

        self.key = key
        
