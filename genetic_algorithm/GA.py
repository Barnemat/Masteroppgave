from random import choice
from genetic_algorithm.GLOBAL import max_note_divisor
from genetic_algorithm.phenotype import Phenotype
from genetic_algorithm.GLOBAL import possible_notes
from syllable_handling.syllable_handling import SyllableDetector


class GA:

    def __init__(self, population_size, lyric, time_signature=None):
        self.population_size = population_size
        self.lyric = lyric
        self.population = None
        self.syllable_detector = lyric.syllable_detector
        self.num_syllables = SyllableDetector.count_syllables_lyric(self.syllable_detector.syllables)
        self.time_signature = time_signature if time_signature else lyric.measure_handler.measure

        self.generate_musical_key()
        self.set_possible_note_lengths()
        self.generate_population()

    def set_possible_note_lengths(self):
        note_lengths = [1]
        last_note = 1

        while last_note < max_note_divisor:
            last_note = last_note * 2
            note_lengths.append(last_note)

        self.note_lengths = note_lengths

    def generate_musical_key(self, maj=None):
        while True:
            note = choice(possible_notes)  # TODO: Muligens øke sannsynligheten for mer vanlige tonearter

            # If r (rest) is later added as valid note (rest cannot be key)
            if note != 'r':
                break

        # Major/minor should perhaps not be specified here, but be handled by a fitness function
        # Either way it should be descided by sentiment input and not randomly
        if not maj:
            maj = choice(['min', 'maj'])

        if len(note) > 1:
            if not maj:
                self.key = get_valid_min_key(note)
            else:
                self.key = [note[0] + 'is' if choice([0, 2]) == 0 else note[2] + 'es']
        else:
            self.key = [note]

        self.key.append(maj)  # Sets major/minor key

    def generate_population(self):
        if not self.population:
            self.population = []

        for _ in range(self.population_size):
            self.population.append(Phenotype(self.key, self.num_syllables, self.time_signature, self.note_lengths))


def get_valid_min_key(note):
    '''
    In musical notation the only minor key usually allowed to be flat is Eb
    Otherwise they are sharp
    Ref: https://upload.wikimedia.org/wikipedia/commons/f/ff/Circle_of_fifths_deluxe_4_de.svg
    '''

    if note == 'd-e':
        return [note[0] + 'is' if choice([0, 2]) == 0 else note[2] + 'es']
    else:
        return note[0] + 'is'
