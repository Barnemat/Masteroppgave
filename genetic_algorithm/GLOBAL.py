'''
Contains some constant values that should be easily accessable from all files
'''

from math import ceil

# All notes and possible semitones (physically)
# E.g. a-b could be either A sharp or B flat in music, but they have the same frequencies
possible_notes = ['a', 'a-b', 'b', 'c', 'c-d', 'd', 'd-e', 'e', 'f', 'f-g', 'g', 'g-a']

# LilyPond in absolute mode starts with middle c
note_order = ['c', 'd', 'e', 'f', 'g', 'a', 'b']

# Both scales are defined as a set of distances from one note to the next
# Might add other scales later (most likely not)
major_scale_distances = [0, 2, 2, 1, 2, 2, 2, 1]
minor_scale_distances = [0, 2, 1, 2, 2, 1, 2, 2]

# Defines if "black tangents" should be sharp/flat in a given key in both major and minor scales
# E.g. If the key is G major, it's 'black tangent' notes ends with 'is' not 'es'
# LilyPond needs this to be specified
# TODO: Check for faults here
major = [['g', 'd', 'a', 'e', 'b', 'fis'], ['ges', 'des', 'aes', 'ees', 'bes', 'f']]
minor = [['e', 'b', 'fis', 'cis', 'gis', 'dis', 'ais'], ['ees', 'bes', 'f', 'c', 'g', 'd']]

# Sets the maximum alloved note division
# E.g. max_note_divisor = 16 means that 16th notes are the shortest notes available
max_note_divisor = 16

# In absolute octave mode of LilyPond octaves are changed by adding commas or quote marks
# c' is middle C
allowed_melody_octaves = ['', '\'', '\'\'']
allowed_chord_octaves = [',', '']

# Chords usually found in a given scale follow some rules, as to their tonality for given notes in scales
# Corresponding harmonies(chords) for a note in scales:
major_scale_chords = ['maj', 'min', 'min', 'maj', 'maj', 'min', 'dim']
minor_scale_chords = ['min', 'dim', 'maj_aug', 'min', 'maj', 'maj', 'dim']

# Different triad distances from root note. Same pattern as for scales
maj_triad_distances = [0, 4, 7]
min_triad_distances = [0, 3, 7]
dim_distances = [0, 3, 6]
maj_aug = [0, 4, 8]

triads = [min_triad_distances, maj_triad_distances, dim_distances, maj_aug]


def get_absolute_note_list():
    octaves = allowed_chord_octaves + allowed_melody_octaves[1:]
    notes = possible_notes[3:] + possible_notes[:3]  # Need to move a and b to the back of list

    absolute_list = []
    for octave in octaves:
        for note in notes:
            if len(note) > 1:
                absolute_list.append([note[0] + 'is' + octave, note[-1] + 'es' + octave])
            else:
                absolute_list.append(note + octave)

    return absolute_list


# LilyPond counts from middle c in absolute mode
# As such an ordered list of all notes migt sometimes be needed
absolute_note_list = get_absolute_note_list()

'''''''''''''''
GLOBAL FUNCTIONS
'''''''''''''''


def get_triad_distances(index, key):
    '''
        Returns the triad distances for the given note index in major/minor scales
    '''

    maj_min = key[1]
    scale_chords = major_scale_chords if maj_min == 'maj' else minor_scale_chords
    chord = scale_chords[index]

    if chord == 'min':
        return min_triad_distances
    elif chord == 'dim':
        return dim_distances
    elif chord == 'maj_aug':
        return maj_aug
    else:
        return maj_triad_distances


# Should be pregerenerated if time
def get_scale_notes(key):
    key_note = key[0]
    key_flavor = key[1]
    sharp_flat = get_key_sharps_flats(key)

    notes = []
    for note in possible_notes:
        if len(note) > 1:
            notes.append(note[-1] + sharp_flat if sharp_flat == 'es' else note[0] + sharp_flat)
        else:
            notes.append(note)

    distances = major_scale_distances.copy() if key_flavor == 'maj' else minor_scale_distances.copy()
    scale = []
    root_note_index = notes.index(key_note)
    distance = distances.pop(0)
    for _ in range(len(distances)):
        scale.append(notes[(root_note_index + distance) % len(notes)])
        distance += distances.pop(0)

    return scale


def get_key_sharps_flats(key):
    key_note = key[0]
    key_flavor = key[1]

    if key_flavor == 'maj':
        return 'is' if key_note in major[0] else 'es'

    return 'is' if key_note in minor[0] else 'es'


def remove_note_timing(note):
    while note[-1].isnumeric() or note[-1] == '.':
        note = note[:-1]

    return note


def get_note_timing(note):

    dotted = ''
    if note.endswith('.'):
        dotted = '.'
        note = note[:len(note) - 1]

    while not note[0].isdigit():
        note = note[1:]

    return note + dotted


def get_note_dec_timing(note):
    timing = get_note_timing(note)

    if timing.endswith('.'):
        timing = int(timing[:-1]) + (int(timing[:-1]) * 2)
    else:
        timing = int(timing)

    return 4 / timing


def remove_note_octave(note):
    return ''.join([char for char in note if char.isalpha() or char.isnumeric()])


def get_note_octave(note):
    return ''.join([char for char in note if not char.isalpha() and not char.isnumeric()])


def get_note_abs_index(note):
    '''
        Return the index of said note in the absolute_note_list
        es/is notes are concidered as having the same index
    '''
    for i in range(len(absolute_note_list)):
        if isinstance(absolute_note_list[i], list):
            for sub_note in absolute_note_list[i]:
                if note == sub_note:
                    return i
        else:
            if note == absolute_note_list[i]:
                return i
    return -1


def get_note_distance(note1, note2):
    '''
        Gets the semitone distance between two notes
        Timing needs to be removed first
    '''
    if not note1 or not note2:
        return 0

    note1_index = get_note_abs_index(note1)
    note2_index = get_note_abs_index(note2)

    if note1_index == -1 or note2 == -1:
        return 0

    return abs(note1_index - note2_index)


def beat_count(note):
    timing = get_note_timing(note)
    dotted = timing.endswith('.')

    if dotted:
        timing = int(timing[:-1])
        timing += timing // 2
    else:
        timing = int(timing)

    return 4 / timing


def accurate_beat_counter(melody):
    count = 0

    for beat in melody:
        for note in beat:
            if isinstance(note, list):
                for mel_note in note:
                    count += beat_count(mel_note)
            else:
                count += beat_count(note)

    return int(ceil(count))


def get_all_notes(melody):
    notes = []

    for beat in melody:
        for note in beat:
            if isinstance(note, list):
                for mel_note in note:
                    notes.append(mel_note)
            else:
                notes.append(note)

    return notes
