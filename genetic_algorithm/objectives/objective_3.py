from genetic_algorithm.objectives.objective import Objective
from genetic_algorithm.GLOBAL import (
    get_note_timing
)


class Objective3(Objective):
    '''
        Class to handle objective 3 of NSGAII algorithm
        Handles the objective of handling global melody optimization
    '''

    def __init__(self, syllables, phonemes):
        super().__init__()

        self.fitness_functions.extend([
            f1
        ])

        self.syllables = syllables
        self.phonemes = phonemes

    def get_total_fitness_value(self, phenotype):
        '''
        '''
        melody = phenotype.genes[0].copy()

        func_num = 1
        fitness_score = 0
        for func in self.fitness_functions:
            # print('fitness function:', func_num)
            fitness_score += func(
                melody=melody,
                phonemes=self.phonemes,
                syllables=self.syllables
            )

            fitness_score = round(fitness_score, 4)
            # self.fitness_score += fitness_score
            # print(fitness_score)
            func_num += 1

        return fitness_score


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
                    timing = float(timing[:len(timing) - 1]) - 0.5  # Subtracts arbituary number, but needs to be lower
                else:
                    timing = float(timing)

            timings.append(timing)

        max_timing = min(timings)
        min_timing = max(timings)

        if max_timing == min_timing:
            syls_long_vowels_sat += 0.5
            continue

        sat_value = 0.0  # Max 1.0
        for index in range(len(stress_values)):
            timing = timings[index]
            stress_value = stress_values[index]
            # print(timing, stress_value)
            if stress_value == 1:  # Primary stress value
                if timing == max_timing:
                    sat_value += 1.0
                elif timing < min_timing:
                    sat_value += 0.25
                elif timing == min_timing:
                    sat_value = 0.0
            elif stress_value == 2:  # Secondary stress value
                if timing == max_timing:
                    sat_value += 0.5
                elif timing <= min_timing:
                    sat_value += 0.25
            else:
                if timing > max_timing:
                    if timing == min_timing:
                        sat_value += 0.75
                    else:
                        sat_value += 0.5

        sat_value /= len(stress_values)  # Normalizes value

        syls_long_vowels_sat += sat_value

    return round(syls_long_vowels_sat / non_empty_phonemes, 4)
