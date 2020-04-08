from math import ceil
from genetic_algorithm.objectives.objective import Objective
from genetic_algorithm.GLOBAL import (
    get_note_timing,
    get_scale_notes,
    get_triad_distances,
    remove_note_octave,
    get_note_distance,
    get_all_notes,
    get_note_dec_timing,
    remove_note_timing
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
            f1, f2, f3, f4, f5, f6, f7, f8
        ])

        if target_values:
            self.target_values = target_values
        else:
            self.target_values = [
                1.00, 1.00, 0.35, 1.00, 1.00, 1.00, 0.60, 0.35
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
        measures = get_measures_from_melody(melody, time_signature)
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

        non_empty_phonemes += 1

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

        max_timing = max(timings)
        min_timing = min(timings)

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
    '''
    chords = kwargs['chords']
    key = kwargs['key']

    first_last = [chords[0][:-1], chords[-1][:-1]]
    distances = get_triad_distances(0, key)

    points = 0.0
    for chord in first_last:
        chord_points = 0.5
        for index in range(len(chord)):
            if index == 3:  # Ignore flavor note in triad
                break
            if not get_note_distance(key[0], chord[index]) == distances[index]:
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
    dominant = scale[4]
    dominant_triad_distances = get_triad_distances(4, key)

    num_triads = 0
    for chord in chords:
        triad = True
        for i in range(len(chord)):
            if i == 3:
                break

            if not get_note_distance(dominant, remove_note_octave(chord[i])) == dominant_triad_distances[i]:
                triad = False
                break

        num_triads += 1 if triad else 0

    return num_triads / len(chords)


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
    return res_doms / doms if doms > 0 else 1.0


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

    return num_ends_measure / len(line_ending_indices)


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

    return count / len(line_ending_indices)


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

    return count / len(line_ending_indices)


def f8(**kwargs):
    '''
        Number of repeated chords
        num(chord_intervals with same chords) / chord_intervals
    '''
    chords = kwargs['chords']

    intervals = []

    for i in range(1, len(chords)):
        intervals.append([chords[i - 1], chords[i]])

    count = 0
    for interval in intervals:
        if interval[0] == interval[1]:
            count += 1

    return count / len(intervals)


def is_correct_triad(chord, key, index):
    distances = get_triad_distances(index, key)
    scale = get_scale_notes(key)

    for i in range(len(chord)):
        if i == 3:
            break

        if not get_note_distance(scale[index], remove_note_octave(chord[i])) == distances[i]:
            return False

    return True


def get_num_syls_in_line(line):
    count = 0
    for word in line:
        for syl in word:
            count += 1
    return count


def get_measures_from_melody(mel, time_signature):
    melody = mel.copy()
    measures = []

    for _ in range(int(ceil(len(melody) // int(time_signature[0])))):
        measure = []

        for _ in range(int(time_signature[0])):
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
