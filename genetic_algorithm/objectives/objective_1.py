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
            f1, f2, f3, f4, f5, f6, f7, f8, f9
        ])

    def get_total_fitness_value(self, phenotype):
        '''
        Timings are (currently) unimportant for this objective, timing related signs
        and structures are removed

        # TODO: Extend func explanation - change name to 'set'
        '''
        melody_beats = phenotype.genes[0]
        chord_beats = phenotype.genes[1]
        key = phenotype.key
        time_signature = phenotype.time_signature
        scale = get_scale_notes(key)

        beat_size = int(time_signature[-1])  # TODO: Double check if this should be time_signature[0]
        measures = []
        index = 0
        while index < len(melody_beats) and index // beat_size < len(chord_beats):

            measure = [[], []]
            for _ in range(beat_size):
                if index == len(melody_beats):
                    break

                beat = melody_beats[index]
                for note in beat:
                    if isinstance(note, list):
                        note_list = []

                        for melisma_note in note:
                            note_list.append(remove_note_timing(melisma_note))

                        measure[0].extend(note_list)
                    else:
                        measure[0].append(remove_note_timing(note))

                index += 1

            chord = chord_beats[index % beat_size].replace('< ', '').replace('>', '').split(' ')
            measure[1] = chord
            # measure[1].extend([x for x in chord if x.find('>') == -1])
            measures.append(measure)

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

        IMPORTANT: Possible change from Olseng: Only tonic and dominant of chord are counted index=0 and index=2
    '''

    melody = measure[0]
    chord = measure[1]

    chord_pitches = []

    for note in melody:
        no_octave_note = remove_note_octave(note)
        for chord_note_index in range(len(chord)):
            no_octave_chord_note = remove_note_octave(chord[chord_note_index])

            if no_octave_chord_note == no_octave_note:
                chord_pitches.append(note)
                break

            '''
            if chord_note_index == 0 or chord_note_index == 2:  # Implements proposed change (tonic/dominant)

                if no_octave_chord_note == no_octave_note:
                    chord_pitches.append(note)
                    break
            '''

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


def get_neighbour_tones(measure, chord_notes, notes):
    melody = measure[0]
    length = len(melody)

    neighbour_tones = []
    for index in range(length - 2):  # neighbour notes are always concerned with the next two notes
        if melody[index] in chord_notes:
            chord_note = melody[index]
            if melody[index + 1] in notes and melody[index + 2] == chord_note:
                neighbour_tones.append(melody[index + 1])

    return neighbour_tones


'''
def get_chord_root_fifth(chord_notes):
        Helping function for f4 and f5
        # TODO: Find out if function is needed elsewhere
        Currently deprecated (since chords are redesigned)
    # Sort octaves in different parts
    commas = []
    clean = []
    for note in chord_notes:
        if note.endswith(','):
            commas.append(note)
        else:
            clean.append(note)

    sorted(commas)
    sorted(clean)

    should_switch = len([note for note in commas if not note.startswith('a') and not note.startswith('b')]) > 0
    if should_switch:
        while commas[0].startswith('a') or commas[0].startswith('b'):
            commas.append(commas.pop(0))  # Moves as and bs to back of list

    should_switch = len([note for note in clean if not note.startswith('a') and not note.startswith('b')]) > 0
    if should_switch:
        while clean[0].startswith('a') or clean[0].startswith('b'):
            clean.append(clean.pop(0))

    sorted_chord_notes = commas + clean

    root = remove_note_octave(sorted_chord_notes[0])  # Assume that the lowest note in a chord is the root
    root_scale = []
    try:
        root_scale = get_scale_notes([root, 'maj'])  # maj/min has the same fith
    except IndexError:  # Some root notes are not allowed in both major and minor and raises exceptions
        root_scale = get_scale_notes([root, 'min'])
    except ValueError:
        root_scale = get_scale_notes([root, 'min'])

    return [root, root_scale[4]]
'''

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
        # TODO: Perhaps <= and not just <
    '''
    return 1 if len(kwargs['scale_pitches'] + kwargs['non_scale_pitches']) <= len(kwargs['chord_pitches']) else 0


def f2(**kwargs):
    '''
        a melody where many notes that resolve in chords does not appear in key is not good
        ornament_notes <= scale_pitches
        = +1 fitness (combined three functions from Olseng, Should maybe up number to +3 to account for that)
    '''
    return 2 if len(kwargs['ornament_notes']) <= len(kwargs['scale_pitches']) else 0


def f3(**kwargs):
    '''
        There should not be an abundance of non_scale_pitches
        non_scale_pitches <= ornament_notes
        = +1 fitness score
    '''
    return 1 if len(kwargs['non_scale_pitches']) <= len(kwargs['ornament_notes']) else 0


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


def f8(**kwargs):
    '''
        Awards measures with at least numerator amount of notes from time_signature
        Fitness +2
    '''
    time = kwargs['time']
    notes = kwargs['scale_pitches'] + kwargs['non_scale_pitches'] + kwargs['chord_pitches']

    return 2 if len(notes) >= time else 0


def f9(**kwargs):
    '''
        If measure contains only one note
        Fitness -1
    '''
    notes = kwargs['scale_pitches'] + kwargs['non_scale_pitches'] + kwargs['chord_pitches']

    return -1 if len(notes) == 1 else 0


'''
No longer needed, as this is defined in initial note generation
def f9(**kwargs):

        Punish notes that are lower than g
        These notes heavily interfere with chords, and are estecially unpleasing in notation
        Should have been defined elsewhere, but now fitness is easier

    all_notes = kwargs['chord_pitches'] + kwargs['scale_pitches'] + kwargs['non_scale_pitches']
    return -len([
        note for note in all_notes if not note.startswith('r')
        and get_note_abs_index(note) <= get_note_abs_index('g')
    ])
'''
