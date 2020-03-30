'''
    Crossover functions
'''
from genetic_algorithm.phenotype import Phenotype
from random import randint, choice
from math import ceil
from copy import deepcopy


def get_num_syls_in_melody(melody):
    '''
        Returns the number of syllables a given melody can support
    '''
    num_syls = 0

    for beat in melody:
        for note in beat:
            if isinstance(note, list) or not note.startswith('r'):
                num_syls += 1

    return num_syls


def clean_chords(chords, max_chords):
    while len(chords) > max_chords:
        chords.pop()
    return chords


def clean_melody(melody, num_syls):
    '''
        Starts at end of melody and removes any notes that exceeds the num_syls limit
        # TODO: Make new function that is smarter
    '''

    new_melody = melody.copy()
    while get_num_syls_in_melody(new_melody) > num_syls:
        while len(new_melody[-1]) == 0:
            del new_melody[-1]

        del new_melody[-1][-1]

    return new_melody


def get_melody_cut(melody, num_beats_cut):
    '''
        Returns a cut of a melody
        IMPORTANT:
        Only use temp melodies, because function makes in-place modifications to list which are not returned
    '''
    cut = []
    last_note_cut = '0'
    for i in range(num_beats_cut):
        if len(melody) > 0:

            # Ensures that random dot_note_handler beats are removed
            while len(melody) > 0 and len(melody[0]) == 0:
                melody.pop(0)

            if len(melody) == 0:
                return cut

            note_cut = melody.pop(0)
            if len(note_cut) > 0 and not isinstance(note_cut[-1], list):
                last_note_cut = note_cut[-1]

            cut.append(note_cut)

            # Ensures that empty beats that corresponds to a note is appended
            # Empty beats added by dot_note_handler are removed
            # Not great as whole timing is not gotten, but it works
            last_note_timing = int(last_note_cut[-1]) if last_note_cut[-1] != '.' else int(last_note_cut[-2])
            max_empty = 3 if last_note_timing == 1 else 1

            index = len(cut) - 1
            while index > -1 and len(cut[index]) == 0:
                index -= 1
                max_empty -= 1

            while len(melody) > 0 and len(melody[0]) == 0:
                pop = melody.pop(0)

                if (last_note_timing == 1 or last_note_timing == 2) and not max_empty <= 0:
                    cut.append(pop)
                    max_empty -= 0

    last_element = cut[-1][-1] if len(cut[-1]) > 0 else []
    if isinstance(last_element, list) and len(last_element) > 0:
        while len(melody) > 0 and len(melody[0]) == 0:
            melody.pop(0)

    return cut


def get_chord_cut(chords, num_chords, num_beats, time_signature):
    '''
        Returns a cut of chords
        IMPORTANT:
        Only use temp chords, because function makes in-place modifications to list which are not returned
    '''
    cut = []
    num_measures = int(ceil(num_beats / time_signature))
    chords_to_cut = num_measures - num_chords

    chords_to_cut = chords_to_cut if chords_to_cut <= len(chords) else len(chords)
    for _ in range(chords_to_cut):
        cut.append(chords.pop(0))

    return cut


def crossover_random_beats(p1, p2):
    '''
        Takes random number of beats from both phenotypes and combines them
        Empty beats are always added to previous note (or rest)
    '''
    time_signature = int(p1.time_signature[0])
    num_syls = p1.num_syllables

    max_cut = time_signature * 2
    melody_genes = []
    chord_genes = []

    p1_melody = p1.genes[0][:]
    p1_chords = p1.genes[1][:]
    p2_melody = p2.genes[0][:]
    p2_chords = p2.genes[1][:]

    current_pheno = choice([p1, p2])
    note_count = 0
    while True:
        current_melody = p1_melody if current_pheno == p1 else p2_melody
        current_chords = p1_chords if current_pheno == p1 else p2_chords

        melody_copy = [] if len(current_melody) > 0 else current_pheno.genes[0][:]
        melody_cut = get_melody_cut(
            current_melody if len(current_melody) > 0 else [choice(melody_copy)],
            randint(1, max_cut)
        )

        melody_genes.extend(melody_cut)

        chord_copy = [] if len(current_chords) > 0 else current_pheno.genes[1][:]
        chord_cut = get_chord_cut(
            current_chords if len(current_chords) > 0 else [choice(chord_copy)],
            len(chord_genes),
            len(melody_genes),
            time_signature
        )

        chord_genes.extend(chord_cut)

        # Done to make cuts from different parts of melody
        if current_pheno == p1:
            if len(p2_melody) > len(melody_cut):
                p2_melody = p2_melody[len(melody_cut):]
            else:
                p2_melody = []
        else:
            if len(p1_melody) > len(melody_cut):
                p1_melody = p1_melody[len(melody_cut):]
            else:
                p1_melody = []

        note_count = get_num_syls_in_melody(melody_genes)
        if note_count >= num_syls:
            melody_genes = clean_melody(melody_genes, num_syls)
            chord_genes = clean_chords(chord_genes, int(len(melody_genes) / time_signature))
            break

        current_pheno = p1 if current_pheno == p2 else p2

    return [melody_genes, chord_genes]


def crossover_random_measures(p1, p2):
    '''
        # TODO: Implement func
        Takes random number of measures from both phenotypes and combines them
        Empty beats are always added to previous note (or rest)
        Empty beats makes some beats span multiple measures, and this must be handled!
    '''
    pass


def apply_crossover(phenotype1, phenotype2):
    '''
        Chooses which crossover function to apply to the two input phenotypes
        Return new phenotype with the resulting genes
    '''

    # Temp - Add more possibilities as they are implemented
    genes = crossover_random_beats(deepcopy(phenotype1), deepcopy(phenotype2))
    # print(phenotype1.genes)
    # print(genes)
    return Phenotype(
        phenotype1.key,
        phenotype1.num_syllables,
        phenotype1.time_signature,
        phenotype1.note_lengths,
        genes=genes
    )
