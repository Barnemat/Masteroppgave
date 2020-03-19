'''
Contains some constant values that should be easily accessable from all files
'''

# All notes and possible semitones (physically)
# E.g. a-b could be either A sharp or B flat in music, but they have the same frequencies
possible_notes = ['a', 'a-b', 'b', 'c', 'c-d', 'd', 'd-e', 'e', 'f', 'f-g', 'g', 'g-a']

# Both scales are defined as a set of distances from one note to the next
# Might add other scales later (most likely not)
major_scale_distances = [0, 2, 2, 1, 2, 2, 2, 1]
minor_scale_distances = [0, 2, 1, 2, 2, 1, 2, 2]

# Defines if "black tangents" should be sharp/flat in a given key in both major and minor scales
# E.g. If the key is G major, it's 'black tangent' notes ends with 'is' not 'es'
# LilyPond needs this to be specified
# TODO: Check for faults here
major = [['g', 'd', 'a', 'e', 'b', 'fis'], ['ges', 'des', 'aes', 'ees', 'bes', 'f']]
minor = [['e', 'b', 'fis', 'cis', 'gis', 'dis'], ['ees', 'bes', 'f', 'c', 'g', 'd']]

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
minor_scale_chords = ['min', 'dim', 'maj-aug', 'min', 'maj', 'maj', 'dim']

# Different triad distances from root note. Same pattern as for scales
maj_triad_distances = [0, 4, 7]
min_triad_distances = [0, 3, 7]
dim_distances = [0, 3, 6]
maj_aug = [0, 4, 8]


'''''''''''''''
GLOBAL FUNCTIONS
'''''''''''''''


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


def remove_note_octave(note):
    return ''.join([char for char in note if char.isalpha() or char.isnumeric()])
