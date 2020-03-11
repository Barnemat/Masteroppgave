'''
Contains some constant values that should be easily accessable from all files
'''

# All notes and possible semitones (physically)
# E.g. a-b could be either A sharp or B flat in music, but they have the same frequencies
# r is rest, # TODO: Implement later
possible_notes = ['a', 'a-b', 'b', 'c', 'c-d', 'd', 'd-e', 'e', 'f', 'f-g', 'g', 'g-a']

# Defines if "black tangents" should be sharp/flat in a given key in both major and minor scales
# E.g. If the key is G major, it's 'black tangent' notes ends with 'is' not 'es'
# LilyPond needs this to be specified
major = [['g', 'd', 'a', 'e', 'b', 'fis', 'cis'], ['ces', 'ges', 'des', 'aes', 'ees', 'bes', 'f']]
minor = [['e', 'b', 'fis', 'cis', 'gis', 'dis'], ['ees', 'bes', 'f', 'c', 'g', 'd']]

# Sets the maximum alloved note division
# E.g. max_note_divisor = 16 means that 16th notes are the shortest notes available
max_note_divisor = 16

# In absolute octave mode of LilyPond octaves are changed by adding commas or quote marks
# c' is middle C
allowed_octaves = ['', '\'', '\'\'']
