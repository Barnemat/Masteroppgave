'''
Mutation functions
'''
from random import randint, choice


'''''''''''''''
Helping functions
'''''''''''''''


def get_note_timing(note):

    dotted = ''
    if note.endswith('.'):
        dotted = '.'
        note = note[:len(note) - 1]

    while not note[0].isdigit():
        note = note[1:]

    return note + dotted


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
        note = choice([i for i in range(len(melody[beat]))])

        while len(melody[beat]) == 0 or len([x for x in melody[beat] if x[0].isalpha() and not x[0] == 'r']) == 0:
            beat = choice([i for i in range(len(melody))])

    return note, beat


'''''''''''''''
Note mutations
'''''''''''''''


def mutate_random_note(phenotype):
    '''
    Chooses a random note in the melody and overrides it with a new note (with same timing)
    Must be set with only_pitch=True
    '''

    melody = phenotype.genes[0].copy()
    note, beat = get_random_note_indices(melody)

    if isinstance(melody[beat][note], list):
        melisma_index = choice([i for i in range(len(melody[beat][note]))])
        melody[beat][note][melisma_index] = phenotype.get_random_note(
            get_note_timing(melody[beat][note][melisma_index]),
            only_pitch=True
        )
    else:
        melody[beat][note] = phenotype.get_random_note(get_note_timing(melody[beat][note]), only_pitch=True)

    phenotype.genes[0] = melody


def mutate_scale_note(phenotype):
    pass


def mutate_timing_in_beat(phenotype):
    pass


def divide_note(phenotype):
    pass


def switch_random_notes(phenotype):
    pass


'''''''''''''''
Chord mutations
'''''''''''''''


def mutate_random_chord(phenotype):
    pass


def mutate_scale_note_chord(phenotype):
    pass


def mutate_extra_note_in_chord(phenotype):
    pass


def switch_random_chords(phenotype):
    pass


def apply_mutation(phenotype):
    '''
        Applies a mutation function based on probabilites defined below
        Probabilites are defined as the number space between the previous variable and current variable
        max should be 100
    '''
    random_note = 10
    scale_note = 30
    timing_in_beat = 45
    divide_note = 55
    switch_notes = 70
    random_chord = 75
    random_scale_note_chord = 90
    switch_chords = 100

    p = randint(0, switch_chords)

    if p <= random_note:
        mutate_random_note(phenotype)
    elif p <= scale_note:
        mutate_scale_note(phenotype)
    elif p <= timing_in_beat:
        mutate_timing_in_beat(phenotype)
    elif p <= divide_note:
        divide_note(phenotype)
    elif p <= switch_notes:
        switch_random_notes(phenotype)
    elif p <= random_chord:
        mutate_random_chord(phenotype)
    elif p <= random_scale_note_chord:
        mutate_scale_note_chord(phenotype)
    elif p <= switch_chords:
        switch_random_chords(phenotype)
