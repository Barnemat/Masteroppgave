from genetic_algorithm.objectives.objective import Objective
from genetic_algorithm.GLOBAL import (
    get_scale_notes,
    remove_note_timing,
    remove_note_octave,
    get_note_distance,
    get_note_abs_index
)


class Objective1(Objective):
    '''
        Class to handle objective 1 of NSGAII algorithm
        Handles the objective of handling local melody optimization
    '''

    def __init__(self):
        super().__init__()

        self.fitness_functions.extend([
            f1, f2, f4, f5, f6, f7, f9, f3, f10  # , f8 ignored
        ])

    def get_total_fitness_value(self, phenotype):
        '''
        Timings are (currently) unimportant for this objective, timing related signs
        and structures are removed
        '''

        melody_beats = phenotype.genes[0]
        chord_beats = phenotype.genes[1]
        key = phenotype.key
        time_signature = phenotype.time_signature
        scale = get_scale_notes(key)
        measures = get_measures_from_melody(melody_beats, chord_beats, int(time_signature[0]), True)

        fitness_value = 0
        for measure in measures:
            chord_pitches = get_chord_pitches(measure)
            scale_pitches = get_scale_pitches(measure, scale, chord_pitches)
            non_scale_pitches = get_non_scale_pitches(measure, chord_pitches, scale_pitches)

            notes = scale_pitches + non_scale_pitches
            ornament_notes = get_ornament_notes(measure, chord_pitches, notes)

            for func in self.fitness_functions:
                fitness_value += func(
                    chord_pitches=chord_pitches,
                    scale_pitches=scale_pitches,
                    non_scale_pitches=non_scale_pitches,
                    ornament_notes=ornament_notes,
                    measure=measure,
                    time=int(time_signature[0])
                )

            # print('Measure:', measure)
            # print('Measure fitness:', fitness_value)

        # Normalize somewhat with respect to the number of measures in music
        # self.fitness_score = round(fitness_value / len(measures), 4)
        # print('Total fitness value:', self.fitness_score)
        return round(fitness_value / len(measures), 4)


def get_chord_pitches(measure):
    '''
        In chord pitch classification octaves should be ignored in the classification,
        as chord ocatave range != melody octave range
    '''

    melody = measure[0]
    chord = measure[1]

    chord_pitches = []

    for note in melody:
        no_octave_note = remove_note_octave(note)

        for chord_note in chord:
            no_octave_chord_note = remove_note_octave(chord_note)

            if no_octave_chord_note == no_octave_note:
                chord_pitches.append(note)
                break

    return chord_pitches


def get_scale_pitches(measure, scale, chord_notes):
    melody = [note for note in measure[0]]
    return [note for note in melody if note not in chord_notes and remove_note_octave(note) in scale]


def get_non_scale_pitches(measure, chord_pitches, scale_pitches):
    return [note for note in measure[0] if note not in chord_pitches and note not in scale_pitches]


def get_ornament_notes(measure, chord_notes, notes):
    melody = measure[0]
    length = len(melody)

    ornament_notes = []
    for index in range(length - 2):  # Passing notes are always concerned with the next two notes
        if melody[index] in chord_notes:
            if melody[index + 1] in notes and melody[index + 2] in chord_notes:
                ornament_notes.append(melody[index + 1])

    return ornament_notes

'''
    **kwargs:
    chord_pitches
    scale_pitches
    non_scale_pitches
    passing_tones
    neighbour_tones
    measure
'''


def f1(**kwargs):
    '''
        stabilizes melody to revolve around chord
        non-harmonic-pitches < chord_pitches
        = +1 fitness score
    '''
    return 1 if len(kwargs['scale_pitches'] + kwargs['non_scale_pitches']) <= len(kwargs['chord_pitches']) else 0


def f2(**kwargs):
    '''
        a melody where many notes that resolve in chords does not appear in key is not good
        ornament_notes < scale_pitches
        = +1 fitness (combined three functions from Olseng, Should maybe up number to +3 to account for that)
    '''
    return 2 if len(kwargs['ornament_notes']) < len(kwargs['scale_pitches']) else 0


def f3(**kwargs):  # Kan kanskje fjernes
    '''
        There should not be an abundance of non_scale_pitches
        non_scale_pitches < ornament_notes
        = +1 fitness score
    '''
    return 1 if len(kwargs['non_scale_pitches']) < len(kwargs['ornament_notes']) else 0


def f4(**kwargs):
    '''
        Added back from Wu:
        at least one root or fifth of chord (tonic or dominant)
        = +1 fitness score
    '''
    chord_notes = kwargs['measure'][1]
    melody = kwargs['measure'][0]

    if len(chord_notes) < 1 or len(melody) < 1:
        return 0

    root_fifth = [remove_note_octave(chord_notes[0]), remove_note_octave(chord_notes[2])]

    for note in kwargs['scale_pitches'] + kwargs['non_scale_pitches']:
        if remove_note_octave(note) in root_fifth:
            return 1

    return 0


def f5(**kwargs):
    '''
        Combined Wu and Olseng
        Harmonic value of a melody increases if first note is root or fifth of corresponding chord
        first note is root or fifth of chord
        = +1 fitness score
    '''
    chord_notes = kwargs['measure'][1]
    melody = kwargs['measure'][0]

    if len(chord_notes) < 1 or len(melody) < 1:
        return 0

    root_fifth = [remove_note_octave(chord_notes[0]), remove_note_octave(chord_notes[2])]

    if remove_note_octave(melody[0]) in root_fifth:
        return 1

    return 0


def f6(**kwargs):
    '''
        If notes are not in scale, they should be passing notes and not standalone
        -n for unresolved non_scale_pitches, i.e. non_scale_pitches not in ornament_notes
    '''
    return -len([note for note in kwargs['non_scale_pitches'] if note not in kwargs['ornament_notes']])


def f7(**kwargs):
    '''
        If many intervals have a greater semitone span than a fifth, it will sound more chaotic
        One jump > 7 < 13 is allowed in each measure, as opposed to Olseng and Wu
        if (num_intervals of size 2 with semitone span > 7) > 1 or span > 12:
            sum(interval span for interval in intervals if span > 7)
        Update 09.04.: Testing no jump > 7 < 13 is allowed
    '''

    melody = kwargs['measure'][0]
    fitness_score = 0

    allow = False
    for index in range(len(melody) - 1):
        note = melody[index]
        next_note = melody[index + 1]

        if not note or not next_note or note == 'r' or next_note == 'r':
            continue

        distance = get_note_distance(note, next_note)

        if distance > 7:
            if not allow or distance > 12:
                fitness_score -= distance - 7
            allow = False

    return fitness_score


def f8(**kwargs):  # Kan muligens fjernes
    '''
        Awards measures with at least numerator amount of notes from time_signature
        Fitness +1
    '''
    time = kwargs['time']
    notes = kwargs['scale_pitches'] + kwargs['non_scale_pitches'] + kwargs['chord_pitches']

    return 1 if len(notes) >= time else 0


def f9(**kwargs):
    '''
        If measure contains only one note
        Fitness -1
    '''
    notes = kwargs['scale_pitches'] + kwargs['non_scale_pitches'] + kwargs['chord_pitches']

    return -1 if len(notes) == 1 else 0


def f10(**kwargs):
    '''
        If measure chord has flavor note, this should have lower note index than first note of melody
        Fitness -1
    '''
    chord = kwargs['measure'][1]
    melody = kwargs['measure'][0]

    if len(melody) == 0:
        return 0

    first_note = melody[0]

    if len(chord) > 3 and get_note_abs_index(chord[3]) > get_note_abs_index(first_note):
        return -1

    return 0


def get_measures_from_melody(mel, ch, time, remove_timing=False):
    melody = mel.copy()
    chords = [chord.replace('< ', '').replace('>', '').split(' ')[:-1] for chord in ch]
    measures = []

    while len(melody) > 0:
        measure = [[], []]
        for _ in range(time):
            if len(melody) == 0:
                break

            beat = melody.pop(0)
            unfolded_beat = []

            for note in beat:
                if isinstance(note, list):
                    for mel_note in note:
                        unfolded_beat.append(remove_note_timing(mel_note) if remove_timing else mel_note)
                else:
                    unfolded_beat.append(remove_note_timing(note) if remove_timing else note)

            measure[0].extend(unfolded_beat)

        if len(chords) > 0:
            measure[1].extend(chords.pop(0))

        measures.append(measure)

    return measures
