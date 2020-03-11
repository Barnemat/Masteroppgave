from random import choice, randint

from genetic_algorithm.GLOBAL import possible_notes, major, minor, allowed_octaves


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
        self.genes = []

        while self.syls_left > 0:
            beat = self.get_random_beat()

            if isinstance(beat[0], list):
                self.genes.append(beat)
                self.syls_left -= len(beat)
                continue

            if int(beat[0][-1]) == 1:
                self.genes.append(beat)
                self.genes += [[] for _ in range(int(self.time_signature[-1]) - 1)]
            elif int(beat[0][-1]) == 2:
                self.genes.append(beat)
                self.genes += [[] for _ in range((int(self.time_signature[-1]) // 2) - 1)]
            else:
                self.genes.append(beat)

            self.syls_left -= len(beat)

    # Not optimised for other divisors in time_signature than 4
    def get_random_beat(self):
        beat = []
        timings = []

        note_length = choice(self.note_lengths)

        if note_length == 1:
            return [self.get_random_note(1)]

        if note_length == 2:
            return [self.get_random_note(2)]

        while True:
            timing = 4 / choice(self.note_lengths[2:])

            if sum([x for x in timings] + [timing]) > 1:
                continue
            else:
                timings.append(timing)

            if sum([x for x in timings]) == 1:
                break

        # The 4 specifies that only time signatures of type x/4 are allowed
        for timing in timings:
            beat.append(self.get_random_note(int(4 / timing)))

        # An arbitary probability for the chance of a beat having a melisma
        # Currently set to a ten percent chance
        if len(beat) > 1 and randint(0, 100) < 15:
            beat = self.set_random_melisma_in_beat(beat)

        return beat

    def get_random_note(self, time):
        note = choice(possible_notes)

        # if note == 'r': return r + str(time) # TODO: ADD LATER

        maj = self.key[1] == 'maj'

        if len(note) > 1:
            if maj:
                note = note[-1] + 'is' if self.key in major[0] else note[0] + 'es'
            else:
                note = note[-1] + 'is' if self.key in minor[0] else note[0] + 'es'

        octave = choice(allowed_octaves)

        return note + octave + str(time)

    def set_random_melisma_in_beat(self, beat):
        if len(beat) == 2:
            return [beat]

        melisma_start = randint(0, len(beat) - 2)
        melisma_end = randint(melisma_start + 1, len(beat) - 1)

        new_beat = beat[:melisma_start] + [beat[melisma_start:melisma_end + 1]] + beat[melisma_end + 1:]

        return new_beat
