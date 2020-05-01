from genetic_algorithm.objectives.objective import Objective
from genetic_algorithm.GLOBAL import (
    get_note_timing,
    get_scale_notes,
    get_triad_distances,
    remove_note_octave,
    get_note_distance,
    get_all_notes,
    get_note_dec_timing,
    remove_note_timing,
    major_scale_chords,
    minor_scale_chords
)


class Objective3(Objective):
    '''
        Class to handle objective 3 of NSGAII algorithm
        Handles the objective of global optimization of the lyric's fitness to melody and chords
        I.e. it's a song making objective
    '''

    def __init__(self, syllables, phonemes, target_values=None):
        super().__init__()

        self.fitness_functions.extend([
            f1, f2, f3, f4, f5, f6, f7, f8, f9, f10, f11, f12, f13
        ])

        self.harmonic_punishment_functions = [
            hf1, hf2, hf3, hf4, hf5
        ]

        if target_values:
            self.target_values = target_values
        else:
            self.target_values = [

            ]

        self.syllables = syllables
        self.phonemes = phonemes

    def compare_with_target_value(self, value, target_index):
        return 1 - abs(value - self.target_values[target_index])

    def get_total_fitness_value(self, phenotype):
        '''
        '''
        melody = phenotype.genes[0].copy()
        chords = [chord.replace('< ', '').replace('>', '').split(' ') for chord in phenotype.genes[1]]
        key = phenotype.key
        time_signature = phenotype.time_signature
        scale = get_scale_notes(key)
        measures = get_measures_from_melody(melody, int(time_signature[0]))
        line_ending_indices = get_line_ending_indices(self.syllables)
        all_notes = get_all_notes(melody)

        ignored_funcs = [5, 11, 12]

        func_num = 0
        fitness_score = 0
        for func in self.fitness_functions:
            # print('fitness function:', func_num + 1)
            if func_num + 1 in ignored_funcs:
                continue

            fitness_score += self.compare_with_target_value(func(
                melody=melody,
                chords=chords,
                time_signature=time_signature,
                scale=scale,
                key=key,
                phonemes=self.phonemes,
                syllables=self.syllables,
                measures=measures,
                line_ending_indices=line_ending_indices,
                all_notes=all_notes
            ), func_num)

            func_num += 1
            # self.fitness_score += fitness_score

        # print(fitness_score)

        for func in self.harmonic_punishment_functions:
            fitness_score += func(len(self.fitness_functions), chords=chords, key=key, scale=scale)

        # print(fitness_score)
        return round(fitness_score, 4)


def f1(**kwargs):
    '''
        Start/end chord should contain tonic triad.
        Returns 0.5 for each condition met
        Note: function is strict (does only allow for closest triad) - could be changed
    '''
    chords = kwargs['chords']
    key = kwargs['key']

    first_last = [chords[0][:-1], chords[-1][:-1]]

    points = 0.0
    for chord in first_last:
        if is_correct_triad(chord, key, 0):
            points += 0.5

    return points


def f2(**kwargs):
    '''
        Returns the portion of chords with dominant triads
        num(dominant triads) / num(chords)
    '''
    chords = [chord[:-1] for chord in kwargs['chords']]
    key = kwargs['key']

    num_triads = 0
    for chord in chords:
        if is_correct_triad(chord, key, 4):
            num_triads += 1

    return round(num_triads / len(chords), 4)


def f3(**kwargs):
    '''
        Dominant should resolve in tonic within two measures
        num(resolving dominant chords) / num(dominant chords)
    '''

    chords = [chord[:-1] for chord in kwargs['chords']]
    key = kwargs['key']

    tonic_dom_list = []
    doms = 0
    for chord in chords:
        if is_correct_triad(chord, key, 0):
            tonic_dom_list.append('t')
        elif is_correct_triad(chord, key, 4):
            tonic_dom_list.append('d')
            doms += 1
        else:
            tonic_dom_list.append('other')

    res_doms = 0
    while len(tonic_dom_list) > 0:
        value = tonic_dom_list.pop(0)

        if value == 'd':
            for _ in range(2):
                if len(tonic_dom_list) == 0:
                    break

                if tonic_dom_list.pop(0) == 't':
                    res_doms += 1
                    break
    # Maybe change default to 0.5, to set it between worst/best
    return round(res_doms / (doms if doms > 0 else 1.0), 4)


def f4(**kwargs):
    '''
        Number of repeated chords
        num(chord_intervals with same chords) / chord_intervals
    '''
    chords = [chord[:-1] for chord in kwargs['chords']]

    intervals = []

    for i in range(1, len(chords)):
        intervals.append([chords[i - 1], chords[i]])

    count = 0
    for interval in intervals:
        if interval[0] == interval[1]:
            count += 1

    return round(count / len(intervals), 4)


def f5(**kwargs):  # IGNORED - Not correct objective
    '''
        Return proportion of measures that start with a note on first beat
        num(measure with pitch on first beat) / num(measures)
    '''
    measures = kwargs['measures']

    count = 0
    for measure in measures:
        if len(measure[0]) > 0 and (isinstance(measure[0][0], list) or not measure[0][0].startswith('r')):
            count += 1
    return round(count / len(measures), 4)


def f6(**kwargs):
    '''
        Returns the portion of chords with tonic triads
        num(tonic triads) / num(chords)
        MAybe splice with above function
    '''
    chords = [chord[:-1] for chord in kwargs['chords']]
    key = kwargs['key']

    tonic_triad_chords = 0
    for chord in chords:
        if is_correct_triad(chord, key, 0):
            tonic_triad_chords += 1

    return round(tonic_triad_chords / len(chords), 4)


def f7(**kwargs):
    '''
        Returns the portion of distinct chords
        num(distinct chords) / num(chords)
    '''
    chords = [str(chord[:-1]) for chord in kwargs['chords']]
    distinct_chords = list(set(chords))

    return round(len(distinct_chords) / len(chords), 4)


def f8(**kwargs):
    '''
        Returns the portion of chords with a 4th flavor note
        num(chords with 4th note) / num(chords)
    '''
    return len([chord for chord in kwargs['chords'] if len(chord[:-1]) == 4]) / len(kwargs['chords'])


def f9(**kwargs):
    '''
        Returns chord progression starting/ending with dominant triads
        Starts = 0.5, ends = 0.5, 0.0, otherwise
    '''
    chords = kwargs['chords']
    key = kwargs['key']

    first_last = [chords[0][:-1], chords[-1][:-1]]

    points = 0.0
    for chord in first_last:
        if is_correct_triad(chord, key, 4):
            points += 0.5

    return points


def f10(**kwargs):
    '''
        Returns the portion of tonic triad chords with flavor notes
        num(tonic triads with flavor) / num(tonic triad chords)
    '''
    chords = [chord[:-1] for chord in kwargs['chords']]
    key = kwargs['key']

    tonic_triad_chords = 0
    flavor_triads = 0
    for chord in chords:
        if is_correct_triad(chord, key, 0):
            tonic_triad_chords += 1

            if len(chord) == 4:
                flavor_triads += 1

    return round(flavor_triads / tonic_triad_chords, 4) if tonic_triad_chords > 0 else 0.0


def f11(**kwargs):  # IGNORED - 30.04.20, but used in harmonic punishment
    '''
        Num chord roots in key
    '''
    chords = kwargs['chords']
    scale = kwargs['scale']

    in_scale = 0
    for chord in chords:
        if remove_note_octave(chord[0]) in scale:
            in_scale += 1

    return round(in_scale / len(chords), 4)


def f12(**kwargs):  # IGNORED 30.04.20. Moved to harmonic punishment
    '''
        Find chords following set scale degrees
        https://en.wikipedia.org/wiki/Major_scale#Triad_qualities
        https://en.wikipedia.org/wiki/Minor_scale
    '''

    chords = [chord[:-1] for chord in kwargs['chords']]
    key = kwargs['key']
    scale = kwargs['scale']

    following_scale_degrees = 0
    for chord in chords:
        root = remove_note_octave(chord[0])

        if root in scale:
            for i in range(len(scale)):
                if root == scale[i]:
                    if is_correct_triad(chord, key, i):
                        following_scale_degrees += 1

    return round(following_scale_degrees / len(chords), 4)


def f13(**kwargs):
    '''
        Find chords with semi-tone dissonace in flavor note
    '''
    chords = [chord[:-1] for chord in kwargs['chords']]

    semi_tone_dis = 0
    for chord in chords:
        if len(chord) == 3:
            return 0

        last_note = chord[-1]

        for i in range(len(chord)):
            if get_note_distance(chord[i], last_note) == 1:
                semi_tone_dis += 1

    return round(semi_tone_dis / len(chords), 4)


'''
HARMONIC PUNISHMENT
'''


def hf1(fitness_functions, **kwargs):
    '''
        If not at least a 0.30 of chords contains tonic triads
        Return -num(chords) / 3
        If not at least a 0.15 of chords contains tonic triads
        Return -num(chords) / 1.5
        Done to heavily punish chord progressions not revolving around tonic
    '''
    portion_of_tonics = f6(**kwargs)

    if portion_of_tonics < 0.30:
        return -(fitness_functions / 3)
    elif portion_of_tonics < 0.15:
        return -(fitness_functions / 1.5)

    return 0


def hf2(fitness_functions, **kwargs):
    '''
        Punishes repeating chord progressions
    '''
    portion_repeated = f4(**kwargs)

    if portion_repeated < 0.3:
        return 0

    return -(fitness_functions * portion_repeated)


def hf3(fitness_functions, **kwargs):
    '''
        Punishes chord progressions where chords does not follow set scale degrees
    '''
    portion_of_set_scale_degrees = f12(**kwargs)

    return -(1.5 * fitness_functions - (portion_of_set_scale_degrees * fitness_functions * 1.5))


def hf4(fitness_functions, **kwargs):
    '''
        Punishes chord progressions based on number of roots not in key
    '''
    roots_in_key = f11(**kwargs)

    return -(2 * fitness_functions - (roots_in_key * fitness_functions * 2))


def hf5(fitness_functions, **kwargs):
    '''
        Punishes flavor note not in chord root key
    '''
    chords = [chord[:-1] for chord in kwargs['chords']]

    count = 0
    for chord in chords:
        if len(chord) < 4:
            continue

        root = remove_note_octave(chord[0])
        scale = get_scale_notes([root, 'maj']) + get_scale_notes([root, 'min'])

        if remove_note_octave(chord[-1]) not in scale:
            count += 1

    return -(count * (10 * count / fitness_functions))


def is_correct_triad(chord, key, index):
    distances = get_triad_distances(index, key)
    scale = get_scale_notes([get_scale_notes(key)[index], distances[1]])

    distances = distances[0]
    root = chord[0]

    if not remove_note_octave(root) == scale[0]:
        return False

    for i in range(1, len(chord)):
        if i == 3:
            break

        chord_note_no_oct = remove_note_octave(chord[i])
        if chord_note_no_oct not in scale or not get_note_distance(root, chord[i]) == distances[i]:
            return False
    return True


def get_num_syls_in_line(line):
    count = 0
    for word in line:
        for syl in word:
            count += 1
    return count


def get_measures_from_melody(mel, time):
    melody = mel.copy()
    measures = []

    while len(melody) > 0:
        measure = []
        for _ in range(time):
            if len(melody) == 0:
                break

            measure.append(melody.pop(0))
        measures.append(measure)
    return measures


def get_line_ending_indices(lines):
    line_ending_indices = []
    index = 0

    for line in lines:
        syls = get_num_syls_in_line(line)
        index += syls
        line_ending_indices.append(index)

    return line_ending_indices
