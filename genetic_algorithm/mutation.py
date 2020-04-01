'''
Mutation functions
'''
from random import randint, choice
from genetic_algorithm.GLOBAL import (
    get_note_timing,
    get_scale_notes,
    allowed_melody_octaves,
    allowed_chord_octaves,
    max_note_divisor,
    remove_note_timing,
    get_note_abs_index
)

'''''''''''''''
Helping functions
'''''''''''''''


def get_random_note_indices(melody):
    beat = choice([i for i in range(len(melody))])
    note = -1

    while len(melody[beat]) == 0:
        beat = choice([i for i in range(len(melody))])

    while (
        note < 0 or len(melody[beat]) < 1
            or (not isinstance(melody[beat][note], list)
                and melody[beat][note].startswith('r'))
    ):
        while len(melody[beat]) == 0 or len([x for x in melody[beat] if x[0].isalpha() and not x[0] == 'r']) == 0:
            beat = choice([i for i in range(len(melody))])

        note = choice([i for i in range(len(melody[beat]))])
    return note, beat


def get_random_scale_note(key, timing, chord=False):
    note_list = get_scale_notes(key)

    new_note = choice(note_list) + choice(allowed_chord_octaves if chord else allowed_melody_octaves) + timing
    return new_note


def get_random_note_before_index(melody, beat, note, melisma_index):
    timing = (
        get_note_timing(melody[beat][note])
        if not isinstance(melody[beat][note], list)
        else get_note_timing(melody[beat][note][melisma_index])
    )

    if note == 0:
        if beat == 0:
            return None, None, None

        beat -= 1
        note = len(melody[beat]) - 1
    else:
        note -= 1

    while beat > -1:
        if len(melody[beat]) == 0:
            if beat == 0:
                break

            beat -= 1
            continue

        note = note if note >= 0 else len(melody[beat]) - 1

        while note > -1:
            if isinstance(melody[beat][note], list):
                mel_index = len(melody[beat][note]) - 1

                while mel_index > -1:
                    if get_note_timing(melody[beat][note][mel_index]) == timing:
                        return beat, note, mel_index
                    mel_index -= 1
            else:
                if get_note_timing(melody[beat][note]) == timing:
                    return beat, note, None
            note -= 1
        beat -= 1

    return None, None, None


def get_random_note_after_index(melody, beat, note, melisma_index):
    timing = (
        get_note_timing(melody[beat][note])
        if not isinstance(melody[beat][note], list)
        else get_note_timing(melody[beat][note][melisma_index])
    )

    if note == len(melody[beat]) - 1:
        if beat == len(melody) - 1:
            return None, None, None

        beat += 1
        note = 0
    else:
        note += 1

    while beat < len(melody):
        if len(melody[beat]) == 0:
            if beat == 0 or beat == len(melody):
                break

            beat += 1
            continue

        note = note if note < len(melody[beat]) else 0

        while note < len(melody[beat]):
            if isinstance(melody[beat][note], list):
                mel_index = 0

                while mel_index < len(melody[beat][note]):
                    if get_note_timing(melody[beat][note][mel_index]) == timing:
                        return beat, note, mel_index
                    mel_index += 1
            else:
                if get_note_timing(melody[beat][note]) == timing:
                    return beat, note, None
            note += 1
        beat += 1

    return None, None, None


'''''''''''''''
Note mutations
'''''''''''''''


def mutate_random_note(phenotype, in_scale=False):
    '''
    Chooses a random note in the melody and overrides it with a new note (with same timing)
    Must be set with only_pitch=True
    '''

    melody = phenotype.genes[0].copy()
    key = phenotype.key.copy()
    note, beat = get_random_note_indices(melody)

    if isinstance(melody[beat][note], list):
        melisma_index = choice([i for i in range(len(melody[beat][note]))])

        if in_scale:
            melody[beat][note][melisma_index] = get_random_scale_note(
                key, get_note_timing(melody[beat][note][melisma_index])
            )
        else:
            melody[beat][note][melisma_index] = phenotype.get_random_note(
                get_note_timing(melody[beat][note][melisma_index]),
                only_pitch=True
            )
    else:
        if in_scale:
            melody[beat][note] = get_random_scale_note(key, get_note_timing(melody[beat][note]))
        else:
            melody[beat][note] = phenotype.get_random_note(get_note_timing(melody[beat][note]), only_pitch=True)

    phenotype.genes[0] = melody


def mutate_scale_note(phenotype):
    mutate_random_note(phenotype, in_scale=True)


def mutate_timing_in_beat(phenotype):
    pass


def mutate_divide_note(phenotype):
    '''
        Divides a note, i.e. note larger than 16
        and makes it a melisma.
        The second note is chosen at random from either the scale or totally random
        Dotted notes are not considered, as it's difficult to handle
    '''

    melody = phenotype.genes[0].copy()
    key = phenotype.key
    note, beat = get_random_note_indices(melody)

    tries = 0
    while (isinstance(melody[beat][note], list)
            or melody[beat][note].startswith('r')
            or melody[beat][note].endswith('.')
            or melody[beat][note].endswith(str(max_note_divisor))):
        note, beat = get_random_note_indices(melody)
        tries += 1

        if tries > 100:
            return

    note_no_timing = remove_note_timing(melody[beat][note])
    timing = str(int(get_note_timing(melody[beat][note])) * 2)
    melisma = [note_no_timing + timing]

    # 20% chance of absolutely random note at end
    if randint(0, 100) > 20:
        melisma.append(get_random_scale_note(key, timing))
    else:
        melisma.append(phenotype.get_random_note(timing, only_pitch=True))

    if melody[beat][note].endswith('1') or melody[beat][note].endswith('2'):
        if len(melody) >= beat + 1:
            return

        melody.pop(beat + 1)

    melody[beat][note] = melisma
    phenotype.genes[0] = melody


def switch_random_notes(phenotype):
    '''
        Switches two semi-random notes in the melody
        Only concideres notes with the same timings
        One note is chosen at random and the nearest note with same timing are swapped
    '''

    melody = phenotype.genes[0].copy()
    note, beat = get_random_note_indices(melody)
    melisma_index = randint(0, len(melody[beat][note]) - 1) if isinstance(melody[beat][note], list) else None

    func = choice([get_random_note_after_index, get_random_note_before_index])
    switch_beat, switch_note, switch_mel_index = func(melody, beat, note, melisma_index)

    if not switch_beat:
        if func == get_random_note_after_index:
            switch_beat, switch_note, switch_mel_index = get_random_note_before_index(melody, beat, note, melisma_index)
        else:
            switch_beat, switch_note, switch_mel_index = get_random_note_after_index(melody, beat, note, melisma_index)

    if not switch_beat:
        return

    a = melody[beat][note][melisma_index] if melisma_index else melody[beat][note]
    b = melody[switch_beat][switch_note][switch_mel_index] if switch_mel_index else melody[switch_beat][switch_note]

    # Don't have time to properly fix error
    if isinstance(a, list) or isinstance(b, list):
        return

    if a and b:
        if melisma_index:
            melody[beat][note][melisma_index] = b
        else:
            melody[beat][note] = b

        if switch_mel_index:
            melody[switch_beat][switch_note][switch_mel_index] = a
        else:
            melody[switch_beat][switch_note] = a

    phenotype.genes[0] = melody


'''''''''''''''
Chord mutations
'''''''''''''''


def mutate_random_chord(phenotype, root=None):
    '''
        Finds a completely random chord root, and generates a valid triad chord,
        with a possibility for an extra note
    '''
    chords = phenotype.genes[1].copy()
    new_chord = phenotype.get_init_chords(phenotype.genes[0], 1, root)[0]

    index = randint(0, len(chords) - 1)
    chords[index] = new_chord
    phenotype.genes[1] = chords


def mutate_scale_note_chord(phenotype):
    '''
    Finds a random chord root from scale, and generates a valid triad chord,
    with a possibility for an extra note
    '''
    root = get_random_scale_note(phenotype.key, '', True)
    mutate_random_chord(phenotype, root)


def mutate_extra_note_in_chord(phenotype):
    '''
        Add/modifies an extra note in a chord
        # TODO: Choose whether the note should be random (but from scale) or chosen by rules
    '''
    chords = phenotype.genes[1].copy()

    if len(chords) == 4:
        chords = chords[:3]

    last_note = chords[-1]  # For resolving distance issues
    new_note = get_random_scale_note(phenotype.key, '', True)

    tries = 20
    while tries > 0 and get_note_abs_index(new_note) <= get_note_abs_index(last_note):
        new_note = get_random_scale_note(phenotype.key, '', True)
        tries -= 1

    if tries <= 0:
        return

    phenotype.genes[1] = chords


def switch_random_chords(phenotype):
    '''
        Switches places for two chords in the music
    '''
    chords = phenotype.genes[1].copy()

    a = randint(0, len(chords) - 1)
    b = a

    tries = 20
    while tries > 0 and a == b:
        b = randint(0, len(chords) - 1)
        tries -= 1

    if tries <= 0:
        return

    a_chord = chords[a]
    b_chord = chords[b]

    chords[a] = b_chord
    chords[b] = a_chord

    phenotype.genes[1] = chords


def apply_mutation(phenotype):
    '''
        Applies a mutation function based on probabilites defined below
        Probabilites are defined as the number space between the previous variable and current variable
        max should be 100
    '''
    random_note = 10
    scale_note = 35
    timing_in_beat = 45
    divide_note = 50
    switch_notes = 65
    random_chord = 70
    random_scale_note_chord = 85
    switch_chords = 95
    extra_note_chord = 100

    p = randint(0, switch_chords)

    if p <= random_note:
        mutate_random_note(phenotype)
    elif p <= scale_note:
        mutate_scale_note(phenotype)
    elif p <= timing_in_beat:
        mutate_timing_in_beat(phenotype)
    elif p <= divide_note:
        mutate_divide_note(phenotype)
    elif p <= switch_notes:
        switch_random_notes(phenotype)
    elif p <= random_chord:
        mutate_random_chord(phenotype)
    elif p <= random_scale_note_chord:
        mutate_scale_note_chord(phenotype)
    elif p <= switch_chords:
        switch_random_chords(phenotype)
    elif p <= extra_note_chord:
        mutate_extra_note_in_chord(phenotype)
