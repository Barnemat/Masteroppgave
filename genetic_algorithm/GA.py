from nltk.corpus import cmudict
from random import choice

from genetic_algorithm.GLOBAL import max_note_divisor
from genetic_algorithm.phenotype import Phenotype
from genetic_algorithm.GLOBAL import possible_notes, major, minor
from genetic_algorithm.objectives.objective_1 import Objective1
from genetic_algorithm.objectives.objective_2 import Objective2
from genetic_algorithm.objectives.objective_3 import Objective3
from genetic_algorithm.objectives.objective_4 import Objective4
from genetic_algorithm.objectives.target_values import get_o2_values_as_list, get_o3_values_as_list
from syllable_handling.syllable_handling import SyllableDetector
from genetic_algorithm.nds import NonDominatedSorter

d = cmudict.dict()


class GA:

    def __init__(self, population_size, lyric, time_signature=None):
        self.population_size = population_size
        self.lyric = lyric
        self.population = None
        self.syllable_detector = lyric.syllable_detector
        self.num_syllables = SyllableDetector.count_syllables_lyric(self.syllable_detector.syllables)
        self.time_signature = time_signature if time_signature else lyric.measure_handler.measure
        self.sentiment = lyric.get_sentiment()
        self.tournament_winner_indices = []

        self.generate_musical_key()
        self.set_possible_note_lengths()
        self.generate_population()
        self.phonemes = get_phonemes_from_syls(self.syllable_detector.syllables)

        self.objectives = [
            Objective1(),
            Objective2(target_values=get_o2_values_as_list()),
            Objective3(self.syllable_detector.syllables, self.phonemes, target_values=get_o3_values_as_list()),
            Objective4()
        ]

    def set_possible_note_lengths(self):
        note_lengths = [1]
        last_note = 1

        while last_note < max_note_divisor:
            last_note = last_note * 2
            note_lengths.append(last_note)

        self.note_lengths = note_lengths

    def generate_musical_key(self, maj=None):
        note = choice(possible_notes)  # TODO: Muligens øke sannsynligheten for mer vanlige tonearter

        # Major/minor should perhaps not be specified here, but be handled by a fitness function
        # Either way it should be descided by sentiment input and not randomly
        if not maj:
            # maj = choice(['min', 'maj'])
            maj = sentiment_based_major_minor(self.sentiment)

        if len(note) > 1:
            if maj == 'min':
                self.key = get_valid_min_key(note)
            else:
                self.key = get_valid_maj_key(note)
        else:
            self.key = [note]

        self.key.append(maj)  # Sets major/minor key

    def generate_population(self):
        if not self.population:
            self.population = []

        for _ in range(self.population_size * 2):
            self.population.append(Phenotype(self.key, self.num_syllables, self.time_signature, self.note_lengths))

    def iterate(self):
        nds = NonDominatedSorter(self.population, self.objectives, self.population_size)
        self.population = nds.get_new_population()
        self.tournament_winner_indices = nds.tournament_winner_indices.copy()


def get_valid_min_key(note):
    '''
    In musical notation the only minor key usually allowed to be flat is Eb
    Otherwise they are sharp
    Ref: https://upload.wikimedia.org/wikipedia/commons/f/ff/Circle_of_fifths_deluxe_4_de.svg
    '''

    if note[0] + 'is' in minor[0]:
        return [note[0] + 'is']
    elif note[-1] + 'es' in minor[1]:
        return [note[-1] + 'es']

    return [note[choice([0, 2])]]


def get_valid_maj_key(note):
    '''
    In musical notation the only major key usually allowed to be sharp is F#
    Otherwise they are flat
    Ref: https://upload.wikimedia.org/wikipedia/commons/f/ff/Circle_of_fifths_deluxe_4_de.svg
    '''

    if note[0] + 'is' in major[0]:
        return [note[0] + 'is']
    elif note[-1] + 'es' in major[1]:
        return [note[-1] + 'es']

    return [note[choice([0, 2])]]


def get_phonemes_from_syls(syllables):
    syls = [y for x in syllables for y in x]

    phonemes = []
    for syl in syls:
        word = ''.join(syl).lower()

        if word not in d:
            phonemes.append([])
            continue

        phoneme = d[word][0]

        stress_values = [x[-1] for x in phoneme if x[-1].isnumeric()]

        if len(stress_values) != len(syl):
            phonemes.append([])
            continue

        phonemes.append(phoneme)

    return phonemes


def sentiment_based_major_minor(sent_value):
    '''
        Returns suggested major/minor key, based on sentiment input
        Value between -0.5 and 0.5 = 50/50 chance
        -1.0 < Value < -0.5 30/70 chance
        0.5 < Value < 1.0 70/30 chance
        Value < -1.0 5/95 chance
        Value > 1.0 85/15 chance
    '''
    maj_min = ''

    '''
    Not really favorable with much probabilities at this point
    if sent_value < -1.0:
        maj_min = 'min' if randint(0, 100) < 95 else 'maj'
    elif sent_value < -0.5:
        maj_min = 'min' if randint(0, 100) < 70 else 'maj'
    elif sent_value < 0.5:
        maj_min = 'min' if randint(0, 100) < 50 else 'maj'
    elif sent_value < 1.0:
        maj_min = 'min' if randint(0, 100) < 30 else 'maj'
    else:
        maj_min = 'min' if randint(0, 100) < 15 else 'maj'
    '''

    if sent_value < 0.0:
        maj_min = 'min'
    else:
        maj_min = 'maj'

    return maj_min
