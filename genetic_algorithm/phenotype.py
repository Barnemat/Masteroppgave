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
            beat = self.get_random_beat()

            syls_used = len(list(filter(lambda x: isinstance(x, list) or not x.startswith('r'), beat[0])))

            if syl_num + syls_used > self.num_syllables:
                while len(beat[0]) and syl_num + syls_used > self.num_syllables:
                    beat[0] = beat[0][:-1]
                    syls_used -= 1

            # Moves functionality for processing extra beats for whole and half notes
            if beat[1]:
                melody.append(beat[0])
                for element in beat[1]:
                    melody.append(element)
            else:
                melody.append(beat[0])

            syl_num += syls_used

            if syl_num >= self.num_syllables:
                break

        return melody

    # Sometimes there is a few to many notes in a melody with regards to syllables
    def clean_melody(self, melody):
        melody = self.dot_note_handler(melody)

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

        while len(melody) % int(self.time_signature[0]) != 0:
            melody.append([])

        return melody

    def dot_note_handler(self, melody):
        '''
        Adds empty extra beats at random locations in the melody to make number
        of beats appear correct with regards to dotted notes
        '''
        extra_beats = 0.0

        for beat in melody:
            if len(beat) == 0:
                continue

            for note in beat:
                if note[-1] == '.':
                    extra_beats += 4 / (int(note[-2]) * 2)

        # TODO: Find out if extra_beats should be ceiled
        for i in range(int(extra_beats)):
            melody.insert(randint(0, len(melody) - 1), [])

        return melody

    def get_init_chords(self, melody, num_chords=None, root=None):
        '''
        Initially chords are added one in each measure with a duration of the whole measure
        num_chords, and especially root are used in special cases (e.g. mutation) where function
        is reused
        '''
        num_chords = num_chords if num_chords else accurate_beat_counter(melody)
        chords = []

        for _ in range(num_chords):
            chord = '< '
            notes = [root] if root else [self.get_random_note(0, True)[:-1]]
            triad = choice(triads)

            note = notes[0]
            note_abs_index = get_note_abs_index(note)
            for x in range(1, randint(3, 4)):  # Allows for chords with 3 or 4 notes
                if x == 3:
                    tries = 20
                    note = self.get_random_note(0, True)[:-1]
                    while (tries > 0 and (note in notes or get_note_abs_index(note) <= get_note_abs_index(notes[-1]))):
                        note = self.get_random_note(0, True)[:-1]
                        tries -= 1

                    if tries == 0:
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

    # Not optimised for other divisors in time_signature than 4
    # Now supports adding of blank beats, where neseccary (whole notes, half notes, some dotted notes)
    def get_random_beat(self):
        beat = []
        timings = []

        note_length = choice(self.note_lengths)

        if note_length == 1:
            return [[self.get_random_note(1)], [[] for _ in range(int(self.time_signature[-1]) - 1)]]

        if note_length == 2:
            return [[self.get_random_note(2)], [[] for _ in range((int(self.time_signature[-1]) // 2) - 1)]]

        timing = 4 / note_length
        while True:
            if sum([x for x in timings] + [timing]) > 1:
                timing = 4 / choice(self.note_lengths[2:])
                continue
            else:
                timings.append(timing)

            if sum([x for x in timings]) == 1:
                break

            timing = 4 / choice(self.note_lengths[2:])

        # The 4 specifies that only time signatures of type x/4 are allowed
        for timing in timings:
            beat.append(self.get_random_note(int(4 / timing)))

        # An arbitary probability for the chance of a beat having a melisma
        # Currently set to a 15% chance
        if len(beat) > 1 and randint(0, 100) < 15:
            beat = self.set_random_melisma_in_beat(beat)

        return [beat, None]

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

        # Sets the chance of a note being dotted
        # Dotted notes need to be handled to keep time
        dotted = '.' if not (time == 16 or time == 1) and not chord_note and not only_pitch and randint(0, 100) < 30 else ''

        return note + octave + str(time) + dotted

    def get_rand_note(self, time, chord_note, only_pitch):
        '''
            Help function for get_random_note
            Added to handle minimum note pitch
        '''
        # A note could be a rest, but NOT in a chord
        note = choice(possible_notes + ['r']) if not chord_note and not only_pitch else choice(possible_notes)

        if note == 'r':
            return 'r' + str(time)

        maj = self.key[1] == 'maj'

        # TODO: If error occurs, check Github master
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
