from random import choice, randint
from math import ceil

from genetic_algorithm.GLOBAL import (
    possible_notes,
    major,
    minor,
    allowed_melody_octaves,
    allowed_chord_octaves,
    get_note_abs_index,
    absolute_note_list,
    triads,
    get_key_sharps_flats,
    min_notes,
    accurate_beat_counter
)


class Phenotype:

    def __init__(self, key, num_syllables, time_signature, note_lengths, genes=None):
        self.key = key
        self.num_syllables = num_syllables
        self.time_signature = time_signature if time_signature else '4/4'
        self.note_lengths = note_lengths
        self.genes = None

        if genes:
            self.genes = genes

        if not self.genes:
            self.set_init_genes()

    def set_init_genes(self):
        melody = self.clean_melody(self.get_init_melody())
        chords = self.get_init_chords(melody)

        self.genes = [melody, chords]

    def get_init_melody(self):
        melody = []

        syl_num = 0
        while True:
            measure = self.get_random_measure()
            syls_used = get_notes_in_measure(measure)
            syl_num += syls_used

            for beat in measure:
                melody.append(beat)

            if syl_num >= self.num_syllables:
                break

        return melody

    # Sometimes there is a few to many notes in a melody with regards to syllables
    def clean_melody(self, melody):
        # Need to take rests 'r' into account
        num_notes = 0
        for beat in melody:
            for note in beat:
                if isinstance(note, list) or not note.startswith('r'):
                    num_notes += 1

        while num_notes > self.num_syllables:
            if len(melody[-1]) == 0:
                del melody[-1]
                continue

            del melody[-1][-1]
            num_notes -= 1

        # while len(melody) % int(self.time_signature[0]) != 0:
        #    melody.append([])

        return melody

    def get_init_chords(self, melody, num_chords=None, root=None):
        '''
        Initially chords are added one in each measure with a duration of the whole measure
        num_chords, and especially root are used in special cases (e.g. mutation) where function
        is reused
        '''
        num_chords = num_chords if num_chords else ceil(accurate_beat_counter(melody) / int(self.time_signature[0]))
        chords = []

        for _ in range(num_chords):
            chord = '< '
            notes = [root] if root else []

            if len(notes) == 0:
                root = self.get_random_note(0, True)[:-1]

                root_index = get_note_abs_index(root)
                max_root = get_note_abs_index(min_notes[1]) + 12
                while root_index > max_root:
                    root = self.get_random_note(0, True)[:-1]
                    root_index = get_note_abs_index(root)

                notes.append(root)

            triad = choice(triads)

            note = notes[0]
            note_abs_index = get_note_abs_index(note)
            for x in range(1, 4):  # Allows for chords with 3 or 4 notes
                if x == 3 and randint(1, 100) < 25:  # Sets a 25 % chance of 4th note in chord
                    tries = 20
                    note = self.get_random_note(0, True)[:-1]
                    while (tries > 0 and (note in notes or get_note_abs_index(note) <= get_note_abs_index(notes[-1]))):
                        note = self.get_random_note(0, True)[:-1]
                        tries -= 1

                    if tries == 0:
                        break
                elif x == 3:
                    break
                else:
                    note = absolute_note_list[note_abs_index + triad[x]]
                    if isinstance(note, list):
                        maj_min = 'maj' if triad == triads[1] or triad == triads[3] else 'min'
                        sharps_flats = get_key_sharps_flats([notes[0], maj_min])
                        if sharps_flats == 'es':
                            note = note[0]
                        else:
                            note = note[1]

                notes.append(note)

            for note in notes:
                chord += note + ' '

            # TODO: Needs tweaking if legal time signatures changes from 3/4 and 4/4
            if self.time_signature == '3/4':
                chord += '>2.'
            else:
                chord += '>1'

            chords.append(chord)

        return chords

    def get_random_measure(self):
        num_beats = int(self.time_signature[0])
        timings = get_measure_timings(num_beats, self.note_lengths)

        beats = []
        for beat_timings in timings:
            beat = []

            for timing in beat_timings:
                beat.append(self.get_random_note(timing))

            # An arbitary probability for the chance of a beat having a melisma
            # Currently set to a 15% chance
            if len(beat) > 1 and randint(0, 100) < 15:
                beat = self.set_random_melisma_in_beat(beat)

            beats.append(beat)

        return beats

    def get_random_note(self, time, chord_note=False, only_pitch=False):
        note = self.get_rand_note(time, chord_note, only_pitch)
        octave = choice(allowed_chord_octaves) if chord_note else choice(allowed_melody_octaves)

        if chord_note:
            while get_note_abs_index(note + octave) < get_note_abs_index(min_notes[1]):
                note = self.get_rand_note(time, chord_note, only_pitch)
                octave = choice(allowed_chord_octaves)
        else:
            while get_note_abs_index(note + octave) < get_note_abs_index(min_notes[0]):
                note = self.get_rand_note(time, chord_note, only_pitch)
                octave = choice(allowed_melody_octaves)

        return note + octave + str(time)

    def get_rand_note(self, time, chord_note, only_pitch):
        '''
            Help function for get_random_note
            Added to handle minimum note pitch
        '''
        # A note could be a rest, but NOT in a chord
        note = choice(possible_notes + ['r']) if not chord_note and not only_pitch else choice(possible_notes)

        if note == 'r':
            return 'r'

        maj = self.key[1] == 'maj'

        if len(note) > 1:
            if self.key in (major[0] if maj else minor[0]):
                note = note[-1] + 'is'
            elif self.key in (major[1] if maj else minor[1]):
                note = note[0] + 'es'
            else:
                note = note[choice([-1, 0])]

        return note

    def set_random_melisma_in_beat(self, beat):
        if len(beat) == 2:
            if len(list(filter(lambda x: x.startswith('r'), beat))) > 0:
                return beat
            return [beat]

        melisma_start = randint(0, len(beat) - 2)
        melisma_end = randint(melisma_start + 1, len(beat) - 1)

        beat_start = beat[:melisma_start]
        melisma = [beat[melisma_start:melisma_end + 1]]
        beat_end = beat[melisma_end + 1:]

        if len(list(filter(lambda x: x.startswith('r'), melisma[0]))) > 0:
            if len(list(filter(lambda x: x.startswith('r'), melisma[0]))) <= 1:
                return [beat]
            elif len(list(filter(lambda x: x.startswith('r'), melisma[0]))) > 1:
                return beat
            else:
                beat_start += list(filter(lambda x: x.startswith('r'), melisma[0]))
                melisma = [list(filter(lambda x: not x.startswith('r'), melisma[0]))]

        return beat_start + melisma + beat_end


def get_measure_timings(total_timing, note_lengths):
    timing = 0.0

    measure_timings = []
    for _ in range(total_timing):
        beat = []
        beat_timing = 0.0

        while beat_timing < 1:
            if timing == total_timing:
                break

            note_timing = 4 / choice(note_lengths)
            dotted = not (note_timing == 0.25 or note_timing == 4) and randint(0, 100) < 30

            sub_timing = note_timing if not dotted else note_timing + (note_timing / 2)

            if sub_timing + timing > total_timing:
                continue

            beat.append(str(int(4 / note_timing)) + ('.' if dotted else ''))
            beat_timing += sub_timing
            timing += sub_timing

        measure_timings.append(beat)

    return measure_timings


def get_notes_in_measure(measure):
    count = 0
    for beat in measure:
        for note in beat:
            if isinstance(note, list) or not note.startswith('r'):
                count += 1 if not isinstance(note, list) else len(note)
    return count
