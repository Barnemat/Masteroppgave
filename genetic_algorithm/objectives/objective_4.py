from genetic_algorithm.objectives.objective import Objective
from genetic_algorithm.GLOBAL import (
    get_scale_notes,
    remove_note_timing,
    remove_note_octave,
    get_note_distance,
    get_triad_distances
)


class Objective4(Objective):
    '''
        Class to handle objective 4 of NSGAII algorithm
        Handles the objective of handling local chord optimization
    '''

    def __init__(self):
        super().__init__()

        self.fitness_functions.extend([
            f1, f2, f3
        ])

    def get_total_fitness_value(self, phenotype):
        '''
        '''
        chords = phenotype.genes[1]
        key = phenotype.key
        time_signature = phenotype.time_signature
        scale = get_scale_notes(key)

        fitness_value = 0
        for chord in chords:
            chord = chord.replace('< ', '').replace('>', '').split(' ')

            for func in self.fitness_functions:
                fitness_value += func(
                    chord=chord,
                    key=key,
                    time_signature=time_signature,
                    scale=scale
                )

            # print('Measure:', measure)
            # print('Measure fitness:', fitness_value)

        # Normalize somewhat with respect to the number of measures in music
        # self.fitness_score = round(fitness_value / len(measures), 4)
        # print('Total fitness value:', self.fitness_score)
        if fitness_value == 0:
            return 1
        return round(fitness_value / len(chords), 4)


def f1(**kwargs):
    '''
        Heavily punish chord roots not in key
        = -50 fitness score
    '''
    chord = kwargs['chord']
    scale = kwargs['scale']

    if not remove_note_octave(chord[0]) in scale:
        return -50
    return 1


def f2(**kwargs):
    '''
        Punish chord not following set scale degrees
        https://en.wikipedia.org/wiki/Major_scale#Triad_qualities
        = -30 fitness score
    '''

    chord = kwargs['chord'][:-1]
    key = kwargs['key']
    scale = kwargs['scale']
    root = remove_note_octave(chord[0])

    if root in scale:
        index = scale.index(root)
        distances = get_triad_distances(index, key)

        for i in range(len(chord)):
            if i == 3:
                break

            if not get_note_distance(chord[0], chord[i]) == distances[i]:
                return -30
    return 0


def f3(**kwargs):
    '''
        Punish semi-tone dissonace in flavor note
        = -20 fitness score
    '''
    chord = kwargs['chord'][:-1]

    if len(chord) == 3:
        return 0

    last_note = chord[-1]

    for i in range(len(chord)):
        if get_note_distance(chord[i], last_note) == 1:
            return -20
    return 0


'''
    # TODO: Maybe make 7th chords more desireable than e.g. aug 6th etc.
'''
