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
    get_note_abs_index,
    min_notes,
    get_triad_distances,
    get_key_sharps_flats,
    absolute_note_list,
    accurate_beat_counter
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
    new_note = choice(note_list)
    octave = choice(allowed_chord_octaves if chord else allowed_melody_octaves)

    if chord:
        while get_note_abs_index(new_note + octave) < get_note_abs_index(min_notes[1]):
            new_note = choice(note_list)
            octave = choice(allowed_chord_octaves)
    else:
        while get_note_abs_index(new_note + octave) < get_note_abs_index(min_notes[0]):
            new_note = choice(note_list)
            octave = choice(allowed_melody_octaves)

    return new_note + octave + timing


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
    '''
        Finds a random beat with more than one note and swaps the timing of the notes
    '''
    melody = phenotype.genes[0].copy()

    beats = []  # len(beat) > 1
    for index in range(len(melody)):
        if len(melody[index]) > 1:
            beats.append(index)

    if len(beats) == 0:
        apply_mutation(phenotype)  # Try other mutation type
        return

    timing_1, timing_2 = 0, 0
    tries_left = len(melody)
    while timing_1 == timing_2 and tries_left > 0:
        beat_index = choice(beats)
        beat = melody[beat_index]

        note_indices = [i for i in range(len(beat))]
        note1_index = choice(note_indices)
        note_indices.remove(note1_index)
        note2_index = choice(note_indices)

        note1 = beat[note1_index]
        note2 = beat[note2_index]

        mel_index_1 = -1
        if isinstance(note1, list):
            mel_index_1 = randint(0, len(note1) - 1)

        mel_index_2 = -1
        if isinstance(note2, list):
            mel_index_2 = randint(0, len(note2) - 1)

        timing_1 = get_note_timing(note1 if mel_index_1 < 0 else note1[mel_index_1])
        timing_2 = get_note_timing(note2 if mel_index_2 < 0 else note2[mel_index_2])

        tries_left -= 1

    if tries_left == 0:
        apply_mutation(phenotype)  # Try other mutation type
        return

    if mel_index_1 > -1:
        melody[beat_index][note1_index][mel_index_1] = remove_note_timing(note1[mel_index_1]) + timing_2
    else:
        melody[beat_index][note1_index] = remove_note_timing(note1) + timing_2

    if mel_index_2 > -1:
        melody[beat_index][note2_index][mel_index_2] = remove_note_timing(note2[mel_index_2]) + timing_1
    else:
        melody[beat_index][note2_index] = remove_note_timing(note2) + timing_1

    phenotype.genes[0] = melody


def mutate_divide_note(phenotype):
    '''
        Divides a note, i.e. note larger than 16
        and makes it a melisma.
        The second note is chosen at random from either the scale or totally random
        Dotted notes are not considered, as it's difficult to handle
        IGNORED: 29.04.20.
    '''

    apply_mutation(phenotype)  # Try other mutation type
    return

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

        if tries > 50:
            apply_mutation(phenotype)  # Try other mutation type
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
            apply_mutation(phenotype)  # Try other mutation type
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

    beat_i = randint(0, len(melody) - 1)
    tries = 0
    while len(melody[beat_i]) == 0:
        beat_i = randint(0, len(melody) - 1)
        tries += 1

        if tries == 100:
            apply_mutation(phenotype)
            break

    note_i = randint(0, len(melody[beat_i]) - 1)
    init_beat_count = accurate_beat_counter([[melody[beat_i][note_i]]], True)

    beat_swap = randint(0, len(melody) - 1)
    note_swap = -1
    tries = 0
    while (len(melody[beat_swap]) == 0
            or note_swap == -1
            or init_beat_count != accurate_beat_counter([[melody[beat_swap][note_swap]]], True)):
        beat_swap = randint(0, len(melody) - 1)
        tries += 1

        if tries == 100:
            apply_mutation(phenotype)
            break

        if len(melody[beat_swap]) == 0:
            continue

        note_swap = randint(0, len(melody[beat_swap]) - 1)

    try:
        note_a = melody[beat_i][note_i]
        note_b = melody[beat_swap][note_swap]
    except IndexError:
        apply_mutation(phenotype)
        return

    melody[beat_i][note_i] = note_b
    melody[beat_swap][note_swap] = note_a

    phenotype.genes[0] = melody


'''''''''''''''
Chord mutations
'''''''''''''''


def mutate_random_chord(phenotype, root=None):  # IGNORED 1.5.
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
    with no possibility for an extra note
    '''
    chords = phenotype.genes[1].copy()
    scale = get_scale_notes(phenotype.key)
    root = choice(scale)
    octave = choice(allowed_chord_octaves)
    tries = 0
    while get_note_abs_index(root + octave) < get_note_abs_index(min_notes[1]):
        octave = choice(allowed_chord_octaves)
        root = choice(scale)
        tries += 1

        if tries == 20:
            apply_mutation(phenotype)
            return

    chord = [root + octave]
    distances = get_triad_distances(scale.index(root), phenotype.key)
    root_note_index = get_note_abs_index(root + octave)
    root_sharp_flats = get_key_sharps_flats([root, distances[1]])

    for i in range(1, 3):
        next_note = absolute_note_list[root_note_index + distances[0][i]]

        if isinstance(next_note, list):
            next_note = next_note[0] if root_sharp_flats == 'is' else next_note[-1]

        chord.append(next_note)

    new_chord = '< '

    for element in chord:
        new_chord += element + ' '

    new_chord = new_chord + '>'

    index = randint(0, len(chords) - 1)
    timing = chords[index].replace('< ', '').replace('>', '').split(' ')[-1]

    chords[index] = new_chord + timing
    phenotype.genes[1] = chords


def mutate_extra_note_in_chord(phenotype):
    '''
        Add/modifies an extra note in a chord
        # TODO: Choose whether the note should be random (but from scale) or chosen by rules
    '''
    chords = phenotype.genes[1].copy()
    chord_index = randint(0, len(chords) - 1)
    chord = chords[chord_index].replace('< ', '').replace('>', '').split(' ')
    root_key = [chord[0], choice(['maj', 'min'])]
    timing = chord[-1]
    chord = chord[:-1]

    if len(chord) == 4:
        chord = chord[:3]

    last_note = chord[-1]  # For resolving distance issues
    new_note = get_random_scale_note(root_key, '', True)

    tries = 20
    while tries > 0 and get_note_abs_index(new_note) <= get_note_abs_index(last_note):
        new_note = get_random_scale_note(root_key, '', True)
        tries -= 1

    if tries <= 0:
        apply_mutation(phenotype)  # Try other mutation type
        return

    chord.append(new_note)

    new_chord = '< '

    for element in chord:
        new_chord += element + ' '

    phenotype.genes[1][chord_index] = new_chord + '>' + timing


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
        apply_mutation(phenotype)  # Try other mutation type
        return

    a_chord = chords[a]
    b_chord = chords[b]

    chords[a] = b_chord
    chords[b] = a_chord

    phenotype.genes[1] = chords


mutation_tries = 0  # Prevents infinite retry-loops for succesful mutation


def apply_mutation(phenotype, reset=False):
    '''
        Applies a mutation function based on probabilites defined below
        Probabilites are defined as the number space between the previous variable and current variable
        max should be 100
    '''
    global mutation_tries

    random_note = 5
    scale_note = 30
    timing_in_beat = 45
    divide_note = 45
    switch_notes = 60
    random_chord = 60
    random_scale_note_chord = 80
    switch_chords = 90
    extra_note_chord = 100

    p = randint(0, switch_chords)

    mutation_tries = 0 if reset else mutation_tries + 1

    if mutation_tries >= 100:
        return

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
