from genetic_algorithm.objectives.objective import Objective
from genetic_algorithm.GLOBAL import (
    get_note_timing,
    get_scale_notes,
    remove_note_timing,
    remove_note_octave,
    get_note_distance,
    get_note_abs_index,
    max_note_divisor
)


class Objective2(Objective):
    '''
        Class to handle objective 2 of NSGAII algorithm
        Handles the objective of handling global melody optimization
    '''

    def __init__(self):
        super().__init__()

        self.fitness_functions.extend([
            f1, f2, f3, f4, f5, f6, f7, f8, f9, f10, f11, f12, f13, f14, f15, f16, f17, f18, f19,
            f20, f21
        ])

    def get_total_fitness_value(self, phenotype):
        '''
        '''
        melody = phenotype.genes[0].copy()
        key = phenotype.key
        time_signature = phenotype.time_signature
        scale = get_scale_notes(key)
        notes = get_notes(melody)
        intervals = get_intervals(notes)
        quanta = get_quanta(notes)

        print(melody)
        print(key, time_signature)
        print(scale)
        print(notes)
        print(intervals)
        print(quanta)

        func_num = 1
        for func in self.fitness_functions:
            print('fitness function:', func_num)
            fitness_score = func(
                melody=melody,
                key=key,
                time_signature=time_signature,
                scale=scale,
                notes=notes,
                intervals=intervals,
                quanta=quanta
            )
            self.fitness_score += fitness_score
            print(fitness_score)
            func_num += 1

        return self.fitness_score


def get_notes(melody):
    notes = []

    for beat in melody:
        for note in beat:
            if isinstance(note, list):
                for mel_note in note:
                    notes.append(mel_note)
            else:
                notes.append(note)

    return notes


def get_intervals(notes):
    '''
        Intervals are all pairs of two pitches,
        ignore rests
    '''

    no_rest_notes = [x for x in notes if not x.startswith('r')]

    intervals = []
    for note_index in range(1, len(no_rest_notes)):
        intervals.append([no_rest_notes[note_index - 1], no_rest_notes[note_index]])

    return intervals


def get_quanta(notes):
    '''
        Quanta is the number of time steps (16th notes) in the melody, i.e. the duration of the melody
    '''
    quanta = 0
    for note in notes:
        timing = get_note_timing(note)
        timing = int(timing) if not timing.endswith('.') else int(timing[:len(timing) - 1])
        quanta += 16 // timing

        if note.endswith('.'):  # Handles dotted notes
            quanta += 16 // (timing * 2)

    return quanta


'''
    **kwargs:
    notes
    num_notes
    intervals
    quanta (16th notes - time steps)
'''


def f1(**kwargs):
    '''
        Pitch variety - num(distinct pitches) / num(notes)
    '''
    notes = kwargs['notes']
    pitches = [remove_note_octave(remove_note_timing(x)) for x in notes]
    distinct_notes = list(set([x for x in pitches]))

    return len(distinct_notes) / len(notes)


def f2(**kwargs):
    '''
        Pitch range - max(pitch) - min(pitch) / desired note range
        Change the desired note range for bigger/smaller spans
    '''
    notes = [remove_note_timing(note) for note in kwargs['notes']]
    note_range = 24  # Two octaves - MAYBE CHANGE

    min_index = 24
    max_index = 0

    for note in notes:
        note_index = get_note_abs_index(note)
        if not note == 'r' and note_index < min_index:
            min_index = note_index

        if not note == 'r' and note_index > max_index:
            max_index = note_index

    if max_index - min_index > note_range:
        return 1.0

    return (max_index - min_index) / note_range


def f3(**kwargs):
    '''
        Key focus - num(pitch quanta) / quanta
        Pitch is either dominant or tonic
    '''
    notes = [note for note in kwargs['notes']]
    notes_no_timing = [remove_note_octave(remove_note_timing(note)) for note in notes]
    scale = kwargs['scale']
    quanta = kwargs['quanta']

    tonic_dominant = []
    for note_index in range(len(notes_no_timing)):
        if notes_no_timing[note_index] == scale[0] or notes_no_timing[note_index] == scale[4]:
            tonic_dominant.append(notes[note_index])

    pitch_quanta = get_quanta(tonic_dominant)
    return pitch_quanta / quanta


def f4(**kwargs):
    '''
        Non-scale notes - num(pitch not in scale quanta) / quanta
    '''
    notes = [note for note in kwargs['notes']]
    notes_no_timing = [remove_note_octave(remove_note_timing(note)) for note in notes]
    scale = kwargs['scale']
    quanta = kwargs['quanta']

    not_in_scale = []
    for note_index in range(len(notes_no_timing)):
        if notes_no_timing[note_index] not in scale:
            not_in_scale.append(notes[note_index])

    non_scale_quanta = get_quanta(not_in_scale)
    return non_scale_quanta / quanta


'''
Dissonant ratings from Towsey:
Interval Dissonance rating
0, 1, 2, 3, 4, 5, 7, 8, 9, 12: 0.0
10: 0.5
6, 11, 13: 1.0
'''


def f5(**kwargs):
    '''
        Dissonant intervals - sum(dissonance rating of intervals) / num(intervals)
        Follows table above
    '''
    intervals = kwargs['intervals']
    dissonance_values = [[0, 1, 2, 3, 4, 5, 7, 8, 9, 12], [10], [6, 11]]  # >= 13 = 1.0

    dissonance_ratings = []
    for interval in intervals:
        note1 = remove_note_timing(interval[0])
        note2 = remove_note_timing(interval[1])

        distance = get_note_distance(note1, note2)

        if distance in dissonance_values[1]:
            dissonance_ratings.append(0.5)
        elif distance in dissonance_values[2] or distance >= 13:
            dissonance_ratings.append(1.0)

    return sum(dissonance_ratings) / len(intervals)


def f6(**kwargs):
    '''
        Contour direction - num(rising intervals) / num(intervals)
        melody with start-note == end-note returns 0.5
    '''
    intervals = kwargs['intervals']

    if intervals[0][0] == intervals[-1][-1]:
        return 0.5

    rising_intervals = 0
    for interval in intervals:
        note1_index = get_note_abs_index(remove_note_timing(interval[0]))
        note2_index = get_note_abs_index(remove_note_timing(interval[1]))

        if note1_index < note2_index:
            rising_intervals += 1

    return rising_intervals / len(intervals)


def f7(**kwargs):
    '''
        Contour stability - num(concequtive intervals) / num(intervals) - 1
        If three concecutive notes are same pitch, they are counted
        # TODO: TEST MORE THOROUGLY
    '''
    intervals = kwargs['intervals']

    cons_intervals = 0
    for index in range(len(intervals) - 1):
        note1_index = get_note_abs_index(remove_note_timing(intervals[index][0]))
        note2_index = get_note_abs_index(remove_note_timing(intervals[index][1]))
        note3_index = get_note_abs_index(remove_note_timing(intervals[index + 1][1]))

        if (
            note1_index < note2_index
            and note2_index < note3_index
            or (note1_index == note2_index and note2_index == note3_index)
        ):
            cons_intervals += 1

        return cons_intervals / (len(intervals) - 1)


def f8(**kwargs):
    '''
        Diatonic step movement - num(Diatonic steps) / num(intervals)
    '''
    intervals = kwargs['intervals']

    diatonic_steps = 0
    for interval in intervals:
        note1 = remove_note_timing(interval[0])
        note2 = remove_note_timing(interval[1])

        distance = get_note_distance(note1, note2)

        if distance == 1 or distance == 2:
            diatonic_steps += 1

    return diatonic_steps / len(intervals)


def f9(**kwargs):
    '''
        Note density - num(notes) / quanta
    '''
    notes = [note for note in kwargs['notes'] if not note.startswith('r')]
    quanta = kwargs['quanta']

    return len(notes) / quanta


def f10(**kwargs):
    '''
        Rest density - num(silent quanta) / quanta
    '''
    quanta = kwargs['quanta']
    rests = [note for note in kwargs['notes'] if note.startswith('r')]
    rest_quanta = get_quanta(rests)

    return rest_quanta / quanta


def f11(**kwargs):
    '''
        Rhytmic variety  - num(distinct note durations used) / num(possible note durations)
        Important: changed denominator from 16 to num_possible note durations
    '''
    notes = kwargs['notes']
    possible_durations = ((max_note_divisor // 4) * 2) + 1  # Dotted notes doubles + 1 the possible values
    note_durations = list(set([get_note_timing(note) for note in notes]))

    return len(note_durations) / possible_durations


def f12(**kwargs):
    '''
        Rhytmic range - max(note duration) +  min(note duration) / num(possible note durations)
        Important: Changed to be based on the number of different possibilities
    '''
    notes = kwargs['notes']
    timings = ['1.', '1', '2.', '2', '4.', '4', '8.', '8', '16']
    note_durations = list(set([timings.index(get_note_timing(note)) + 1 for note in notes]))

    return (max(note_durations) / min(note_durations)) / len(timings)


def f13(**kwargs):
    '''
        Repeated pitches - num(intervals containing same notes) / num(intervals)
    '''
    intervals = kwargs['intervals']

    same_note_intervals = 0
    for interval in intervals:
        note_1 = remove_note_timing(interval[0])
        note_2 = remove_note_timing(interval[1])

        if note_1.startswith('r') or note_2.startswith('r'):
            continue
        elif note_1 == note_2:
            same_note_intervals += 1

    return same_note_intervals / len(intervals)


def f14(**kwargs):
    '''
        Repeated rhytms - num(intervals containing notes with same duration) / num(intervals)
    '''
    intervals = kwargs['intervals']

    same_duration_intervals = 0
    for interval in intervals:
        if interval[0].startswith('r') or interval[1].startswith('r'):
            continue

        note_1 = get_note_timing(interval[0])
        note_2 = get_note_timing(interval[1])

        if note_1 == note_2:
            same_duration_intervals += 1

    return same_duration_intervals / len(intervals)


def f15(**kwargs):
    '''
        On-beat pitch - num(beats covered by one pitch) / num(beats)
    '''
    melody = kwargs['melody']

    one_beat_pitches = 0
    for beat in melody:
        if len(beat) == 1:
            one_beat_pitches += 1

    return one_beat_pitches / len(melody)


def f16(**kwargs):
    '''
        Repeated pitch patterns (3 notes) - num(repeated patterns of 3 notes) / num(notes) - 4
    '''
    notes = kwargs['notes']

    repeated_3_patterns = 0
    for index in range(len(notes) - 5):
        first_notes = [notes[index], notes[index + 1], notes[index + 2]]
        compare_with = [notes[index + 3], notes[index + 4], notes[index + 5]]

        if first_notes == compare_with:
            repeated_3_patterns += 1

    return repeated_3_patterns / (len(notes) - 4)


def f17(**kwargs):
    '''
        Repeated rhytmic patterns (3 notes) - num(repeated patterns of 3 durations) / num(notes) - 4
    '''
    notes = kwargs['notes']

    repeated_3_patterns = 0
    for index in range(len(notes) - 5):
        first_notes = [
            get_note_timing(notes[index]), get_note_timing(notes[index + 1]), get_note_timing(notes[index + 2])
        ]
        compare_with = [
            get_note_timing(notes[index + 3]), get_note_timing(notes[index + 4]), get_note_timing(notes[index + 5])
        ]

        if first_notes == compare_with:
            repeated_3_patterns += 1

    return repeated_3_patterns / (len(notes) - 4)


def f18(**kwargs):
    '''
        Repeated pitch patterns (4 notes) - num(repeated patterns of 4 notes) / num(notes) - 5
    '''
    notes = kwargs['notes']

    repeated_4_patterns = 0
    for index in range(len(notes) - 7):
        first_notes = [notes[index], notes[index + 1], notes[index + 2], notes[index + 3]]
        compare_with = [notes[index + 4], notes[index + 5], notes[index + 6], notes[index + 7]]

        if first_notes == compare_with:
            repeated_4_patterns += 1

    return repeated_4_patterns / (len(notes) - 5)


def f19(**kwargs):
    '''
        Repeated rhytmic patterns (4 notes) - num(repeated patterns of 4 durations) / num(notes) - 5
    '''
    notes = kwargs['notes']

    repeated_4_patterns = 0
    for index in range(len(notes) - 7):
        first_notes = [
            get_note_timing(notes[index]),
            get_note_timing(notes[index + 1]),
            get_note_timing(notes[index + 2]),
            get_note_timing(notes[index + 3])
        ]
        compare_with = [
            get_note_timing(notes[index + 4]),
            get_note_timing(notes[index + 5]),
            get_note_timing(notes[index + 6]),
            get_note_timing(notes[index + 7])
        ]

        if first_notes == compare_with:
            repeated_4_patterns += 1

    return repeated_4_patterns / (len(notes) - 5)


'''
def f13(**kwargs):
    ''''''
    Syncopation - Come back this
    ''''''
    pass
'''


'''''''''''''''
NOVEL FITNESS FUNCTIONS
'''''''''''''''


def f20(**kwargs):
    '''
        Semi-tone steps - num(intervals with semi tone step) / num(intervals)
        Dissonance measurement: dissonance = sad, creepy etc.
    '''
    intervals = kwargs['intervals']

    semitone_steps = 0
    for interval in intervals:
        note1 = remove_note_timing(interval[0])
        note2 = remove_note_timing(interval[1])

        distance = get_note_distance(note1, note2)

        if distance == 1:
            semitone_steps += 1

    return semitone_steps / len(intervals)


def f21(**kwargs):
    '''
        # TODO: IMPLEMENT!!
        Word in lyric stress and rhythm satisfaction
    '''
    return 0.0
