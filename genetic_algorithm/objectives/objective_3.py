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
            f1, f2, f3, f4, f5, f6, f7, f8, f9, f10, f11, f12, f13, f14, f15
        ])

        self.harmonic_punishment_functions = [
            hf1, hf2
        ]

        if target_values:
            self.target_values = target_values
        else:
            self.target_values = [
                1.00, 1.00, 0.35, 1.00, 1.00, 1.00, 0.60, 0.30, 0.70, 0.60, 0.40, 0.50, 0.35, 0.00, 0.40
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

        func_num = 0
        fitness_score = 0
        for func in self.fitness_functions:
            # print('fitness function:', func_num + 1)
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
            fitness_score = func(fitness_score, chords=chords, key=key)

        # print(fitness_score)
        return round(fitness_score, 4)


def f1(**kwargs):
    '''
        Word in lyric stress and rhythm satisfaction
        Returns a normalized value for how the syllables in words throughout the lyric
        satisfies stress constraints from cmudict phonemes
        The function reward longer notes for primary stress values and shorter notes for no stress values etc.
    '''
    notes = [y for x in kwargs['melody'] for y in x if len(x) > 0]
    syls = [y for x in kwargs['syllables'] for y in x]
    phonemes = kwargs['phonemes'].copy()
    # print(notes)
    # print(syls)
    # print(phonemes)

    syls_long_vowels_sat = 0.0
    non_empty_phonemes = 0
    for syl_index in range(len(syls)):
        word_notes = []

        if len(notes) == 0:
            break

        for index in range(len(syls[syl_index])):
            note = notes.pop(0)

            while not isinstance(note, list) and note.startswith('r'):
                if len(notes) == 0:
                    break

                note = notes.pop(0)

            word_notes.append(note)

            if len(notes) == 0:
                break

        phoneme = phonemes.pop(0)

        if len(phoneme) == 0:
            continue

        stress_values = [int(x[-1]) for x in phoneme if x[-1].isnumeric()]

        timings = []
        for index in range(len(word_notes)):
            timing = ''
            if isinstance(word_notes[index], list):
                mel_timings = []

                for mel in word_notes[index]:
                    if mel.startswith('r'):  # Added security
                        continue

                    mel_timing = get_note_timing(mel).strip()

                    if mel_timing.endswith('.'):
                        # Subtracts (almost) arbituary number, but needs to be lower
                        mel_timing = float(mel_timing[:len(mel_timing) - 1]) - 0.5
                    else:
                        mel_timing = float(mel_timing)
                    mel_timings.append(mel_timing)
                timing = 4 / sum([4 / x for x in mel_timings])
            else:
                timing = get_note_timing(word_notes[index]).strip()

                if timing.endswith('.'):
                    # Subtracts arbituary number, but needs to be lower
                    timing = 4 / (float(timing[:len(timing) - 1]) - 0.5)
                else:
                    timing = 4 / float(timing)

            timings.append(timing)

        if len(stress_values) != len(timings):
            continue

        max_timing = max(timings)
        min_timing = min(timings)

        non_empty_phonemes += 1

        if max_timing == min_timing:
            syls_long_vowels_sat += 1.0
            continue

        sat_value = 0.0  # Max 1.0
        for index in range(len(stress_values)):
            timing = timings[index]
            stress_value = stress_values[index]
            # print(timing, stress_value)
            if stress_value == 1:  # Primary stress value
                if timing == max_timing:
                    sat_value += 1.0
                elif timing > min_timing:
                    sat_value += 0.25
                elif timing == min_timing:
                    sat_value = 0.0
            elif stress_value == 2:  # Secondary stress value
                if timing == max_timing:
                    sat_value += 0.5
                elif timing >= min_timing:
                    sat_value += 0.25
            else:
                if timing < max_timing:
                    if timing == min_timing:
                        sat_value += 0.75
                    else:  # TODO: elif timing
                        sat_value += 0.5

        sat_value /= len(stress_values)  # Normalizes value

        syls_long_vowels_sat += sat_value
    return round(syls_long_vowels_sat / non_empty_phonemes, 4)


def f2(**kwargs):
    '''
        Start/end chord should contain tonic triad.
        Returns 0.5 for each condition met
        Note: function is strict (does only allow for closest triad) - could be changed
    '''
    chords = kwargs['chords']
    key = kwargs['key']
    scale = kwargs['scale']

    first_last = [chords[0][:-1], chords[-1][:-1]]
    distances = get_triad_distances(0, key)[0]

    points = 0.0
    for chord in first_last:
        if remove_note_octave(chord[0]) != scale[0]:
            continue

        chord_points = 0.5
        for index in range(len(chord)):
            if index == 3:  # Ignore flavor note in triad
                break
            if (remove_note_octave(chord[index]) not in scale
                    or not get_note_distance(chord[0], chord[index]) == distances[index]):
                chord_points = 0.0
                break
        points += chord_points

    return points


def f3(**kwargs):
    '''
        Returns the portion of chords with dominant triads
        num(dominant triads) / num(chords)
    '''
    chords = [chord[:-1] for chord in kwargs['chords']]
    key = kwargs['key']
    scale = kwargs['scale']
    dominant_triad_distances = get_triad_distances(4, key)[0]
    dom_scale = get_scale_notes([scale[4], 'maj'])

    num_triads = 0
    for chord in chords:
        triad = True

        if remove_note_octave(chord[0]) != scale[4]:
            continue

        for i in range(len(chord)):
            if i == 3:
                break

            chord_note_no_oct = remove_note_octave(chord[i])
            if (chord_note_no_oct not in dom_scale
                    or not get_note_distance(chord[0], chord[i]) == dominant_triad_distances[i]):
                triad = False
                break

        num_triads += 1 if triad else 0

    return round(num_triads / len(chords), 4)


def f4(**kwargs):
    '''
        Dominant should resolve in tonic within two measures
        num(resolving dominant chords) / num(dominant chords)
        # TODO: Find out if functions should be moved to other objective
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


def f5(**kwargs):
    '''
        Returns number of line endings also ending a measure (ending + rest is also ending)
        num(lines ends measure) / num(lines)
    '''
    measures = kwargs['measures']
    line_ending_indices = kwargs['line_ending_indices']

    num_ends_measure = 0
    note_total_index = 0
    for measure in measures:
        for beat_index in range(len(measure)):
            for note_index in range(len(measure[beat_index])):
                if note_total_index in line_ending_indices:
                    if (beat_index == len(measure) - 1 and note_index == len(measure[beat_index]) - 1):
                        num_ends_measure += 1
                note_total_index += 1

    return round(num_ends_measure / len(line_ending_indices), 4)


def f6(**kwargs):
    '''
        Number of line endings ending on note with longer duration than previous
        num(notes w. note durations > prev note) / lines
    '''
    melody = kwargs['melody']
    line_ending_indices = kwargs['line_ending_indices']

    count = 0
    total_note_count = 0
    for beat_i in range(len(melody)):
        for note_i in melody[beat_i]:
            if total_note_count in line_ending_indices:
                note = melody[beat_i][note_i]
                if isinstance(note, list):
                    if len(note) > 1 and get_note_dec_timing(note[-2]) < get_note_dec_timing(note[-1]):
                        count += 1
                elif note_i == 0:
                    if beat_i > 0 and len(melody[beat_i - 1][-1]) > 0 and len(melody[beat_i][note_i]) > 0:
                        if get_note_dec_timing(melody[beat_i - 1][-1]) < get_note_dec_timing(melody[beat_i][note_i]):
                            count += 1
                elif len(melody[beat_i][-1]) > 0 and len(melody[beat_i][note_i]) > 0:
                    count += 1
                total_note_count += 1

    return round(count / len(line_ending_indices), 4)


def f7(**kwargs):
    '''
        Number of line endings ending on tonic
        num(tonic ending lines) / lines
    '''
    line_ending_indices = kwargs['line_ending_indices']
    tonic = kwargs['scale'][0]
    melody = kwargs['melody']

    count = 0
    total_note_count = 0
    for beat_i in range(len(melody)):
        for note_i in range(len(melody[beat_i])):
            if total_note_count in line_ending_indices:
                note = melody[beat_i][note_i]

                if isinstance(note, list):
                    if remove_note_octave(remove_note_timing(melody[beat_i][note_i][-1])) == tonic:
                        count += 1
                elif remove_note_octave(remove_note_timing(melody[beat_i][note_i])) == tonic:
                    count += 1

            total_note_count += 1

    return round(count / len(line_ending_indices), 4)


def f8(**kwargs):
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


def f9(**kwargs):
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


def f10(**kwargs):
    '''
        BYPASSED! 15.04.20
        Return number of chord roots that should have major/minor triad in number of chords
        maj/min is decided by key

        num(maj/min roots) / num(chords)
        target_num should probably be 0.4 - 0.5, and somewhat based on sentiment (i.e. increace with high sent. values)
    '''
    key = kwargs['key']
    chords = chords = [chord[:-1] for chord in kwargs['chords']]
    scale = kwargs['scale']
    scale_chords = major_scale_chords if key[1] == 'maj' else minor_scale_chords

    count = 0
    for chord in chords:
        root = remove_note_octave(chord[0])

        if root in scale:
            index = scale.index(root)

            if key[1] == 'maj' and scale_chords[index] == 'maj':
                count += 1
            elif key[1] == 'min':
                if scale_chords[index] == 'min' or scale_chords[index] == 'dim':
                    count += 1

    # return count / len(chords)
    return 0.60


def f11(**kwargs):
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


def f12(**kwargs):
    '''
        Returns the portion of distinct chords
        num(distinct chords) / num(chords)
    '''
    chords = [str(chord[:-1]) for chord in kwargs['chords']]
    distinct_chords = list(set(chords))

    return round(len(distinct_chords) / len(chords), 4)


def f13(**kwargs):
    '''
        Returns the portion of chords with a 4th flavor note
        num(chords with 4th note) / num(chords)
    '''
    return len([chord for chord in kwargs['chords'] if len(chord[:-1]) == 4]) / len(kwargs['chords'])


def f14(**kwargs):
    '''
        Returns chord progression starting/ending with dominant triads
        Starts = 0.5, ends = 0.5, 0.0, otherwise
    '''
    chords = kwargs['chords']
    key = kwargs['key']
    scale = get_scale_notes([kwargs['scale'][4], 'maj'])

    first_last = [chords[0][:-1], chords[-1][:-1]]
    distances = get_triad_distances(4, key)[0]

    points = 0.0
    for chord in first_last:
        if remove_note_octave(chord[0]) != scale[0]:
            continue

        chord_points = 0.5
        for index in range(len(chord)):
            if index == 3:  # Ignore flavor note in triad
                break

            if (remove_note_octave(chord[index]) not in scale
                    or not get_note_distance(chord[0], chord[index]) == distances[index]):
                chord_points = 0.0
                break
        points += chord_points

    return points


def f15(**kwargs):
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


'''
def f13(**kwargs):
        # TODO: IMPLEMENT LATER IF NEEDED
        Gets number of syllables that spans multiple measures
        num(syls spanning multiple measures)/ num(syls)
        (Not desired that number is high)
    pass
'''


'''
HARMONIC PUNISHMENT
'''


def hf1(fitness_value, **kwargs):
    '''
        If not at least a 0.33 of chords contains tonic triads
        Return fitness_value / 2
        Done to heavily punish chord progressions not revolving around tonic
    '''
    portion_of_tonics = f11(**kwargs)

    if portion_of_tonics < (1 / 3):
        return fitness_value / 2

    return fitness_value


def hf2(fitness_value, **kwargs):
    '''
        If a chord is found to be repeated for more than 0.5 of the chord progression
        Return fitness value / 2 if chord is not tonic - fitness_value / 1.25 if tonic
        Done to heavily punish "monotone" chord progressions
    '''
    chords = [chord[:-1] for chord in kwargs['chords']]
    key = kwargs['key']

    for chord in chords:
        repeated = len([x for x in chords if x == chord])
        tonic = is_correct_triad(chord, key, 0)

        if repeated > len(chords) / 2:
            if tonic:
                return fitness_value / 1.25
            else:
                return fitness_value / 2

    return fitness_value


def is_correct_triad(chord, key, index):
    distances = get_triad_distances(index, key)
    scale = []

    try:
        scale = get_scale_notes([get_scale_notes(key)[index], distances[1]])
    except ValueError:
        return False

    distances = distances[0]

    for i in range(len(chord)):
        if i == 3:
            break

        chord_note_no_oct = remove_note_octave(chord[i])
        if chord_note_no_oct not in scale or not get_note_distance(scale[0], chord[i]) == distances[i]:
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
