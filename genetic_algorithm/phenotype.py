from random import choice, randint
from math import ceil

from genetic_algorithm.GLOBAL import possible_notes, major, minor, allowed_melody_octaves, allowed_chord_octaves


class Phenotype:

    def __init__(self, key, num_syllables, time_signature, note_lengths, genes=None):
        self.key = key
        self.num_syllables = num_syllables
        self.time_signature = time_signature if time_signature else '4/4'
        self.syls_left = num_syllables  # Temp value for hanlding the number of syllables to set notes to
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
        while syl_num < self.num_syllables:
            beat = self.get_random_beat()

            # Moves functionality for processing extra beats for whole and half notes
            if beat[1]:
                melody.append(beat[0])
                for element in beat[1]:
                    melody.append(element)
            else:
                melody.append(beat[0])

            syls_used = len(list(filter(lambda x: isinstance(x, list) or not x.startswith('r'), beat[0])))
            syl_num += syls_used

        # TODO: Add an extra method that removes notes exceeds number of syls
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

        melody = self.dot_note_handler(melody)
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

    def get_init_chords(self, melody):
        '''
        Initially chords are added one in each measure with a duration of the whole measure
        '''
        num_chords = int(ceil(len(melody) / int(self.time_signature[0])))
        chords = []

        for _ in range(num_chords):
            chord = '< '
            notes = []

            for x in range(randint(3, 4)):  # Allows for chords with 3 or 4 notes
                note = self.get_random_note(0, True)[:-1]

                # There's no use to having the (exact) same notes appearing twice in a chord
                while note in notes:
                    note = self.get_random_note(0, True)[:-1]

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

    def get_random_note(self, time, chord_note=False):
        # A note could be a rest, but NOT in a chord
        note = choice(possible_notes + ['r']) if not chord_note else choice(possible_notes)

        if note == 'r':
            return 'r' + str(time)

        maj = self.key[1] == 'maj'

        if len(note) > 1:
            if maj:
                note = note[-1] + 'is' if self.key in major[0] else note[0] + 'es'
            else:
                note = note[-1] + 'is' if self.key in minor[0] else note[0] + 'es'

        octave = choice(allowed_chord_octaves) if chord_note else choice(allowed_melody_octaves)

        # Sets the chance of a note being dotted
        # Dotted notes need to be handled to keep time
        dotted = '.' if not chord_note and randint(0, 100) < 10 else ''

        return note + octave + str(time) + dotted

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
