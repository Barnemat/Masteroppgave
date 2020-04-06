from nltk.corpus import cmudict
from random import choice, randint

from genetic_algorithm.GLOBAL import max_note_divisor
from genetic_algorithm.phenotype import Phenotype
from genetic_algorithm.GLOBAL import possible_notes, major, minor
from genetic_algorithm.objectives.objective_1 import Objective1
from genetic_algorithm.objectives.objective_2 import Objective2
from genetic_algorithm.objectives.objective_3 import Objective3
from genetic_algorithm.objectives.objective_4 import Objective4
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

        self.generate_musical_key()
        self.set_possible_note_lengths()
        self.generate_population()
        self.phonemes = get_phonemes_from_syls(self.syllable_detector.syllables)

        self.objectives = [
            Objective1(),
            Objective2(),
            Objective3(self.syllable_detector.syllables, self.phonemes),
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
            maj = choice(['min', 'maj'])

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

        '''
        Old - before tournament selection
        new = []
        for pheno_index in range(len(population)):
            if pheno_index == len(population) - 1:
                new.append(apply_crossover(population[pheno_index], population[0]))
                break

            new.append(apply_crossover(population[pheno_index], population[pheno_index + 1]))

        self.population.extend(new)

        for phenotype in self.population:
            if randint(0, 100) <= 5:  # Chance of phenotype mutating
                apply_mutation(phenotype)
        '''


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
