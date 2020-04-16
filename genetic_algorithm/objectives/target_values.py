'''
    Contains target values for objective 2 and 3
'''

'''
    Precaution to map values to correct indices in list representation
'''
objective_2_indices = [
    'pitch_variety',
    'pitch_range',
    'key_focus',
    'non_scale_notes',
    'dissonant_intervals',
    'count_direction',
    'count_stability',
    'diatonic_step_movement',
    'note_density',
    'rest_density',
    'rhythmic_variety',
    'rhythmic_range',
    'repeated_pitches',
    'repeated_rhythms',
    'on_beat_pitches',
    'rep_pitch_patterns_3',
    'rep_rh_patterns_3',
    'rep_pitch_patterns_4',
    'rep_rh_patterns_4',
    'semitone_steps',
    '16th_notes',
    'whole_notes',
    'repeated_pitches_patterns'
]

objective_3_indices = [
    'lyric_stress_constraints',
    'start_end_tonic_triad',
    'dominant_triad_chords',
    'dominant_resolved_tonic',
    'lyric_line_ends_measure',
    'lyric_line_end_on_long_duration',
    'lyric_line_end_on_tonic',
    'repeated_chords',
    'measures_note_on_first_beat',
    'num_major_minor_chords',
    'num_tonic_triad_chords',
    'num_distinct_chords'
]

objective_2_values = {
    'pitch_variety': 0.30,
    'pitch_range': 0.60,
    'key_focus': 0.35,
    'non_scale_notes': 0.00,
    'dissonant_intervals': 0.10,
    'count_direction': 0.50,
    'count_stability': 0.50,
    'diatonic_step_movement': 0.30,
    'note_density': 0.30,
    'rest_density': 0.10,
    'rhythmic_variety': 0.40,
    'rhythmic_range': 0.80,
    'repeated_pitches': 0.10,
    'repeated_rhythms': 0.50,
    'on_beat_pitches': 0.30,
    'rep_pitch_patterns_3': 0.20,
    'rep_rh_patterns_3': 0.20,
    'rep_pitch_patterns_4': 0.10,
    'rep_rh_patterns_4': 0.10,
    'semitone_steps': 0.20,
    '16th_notes': 0.10,
    'whole_notes': 0.10,
    'repeated_pitches_patterns': 0.00
}

objective_3_values = {
    'lyric_stress_constraints': 1.00,
    'start_end_tonic_triad': 1.00,
    'dominant_triad_chords': 0.25,
    'dominant_resolved_tonic': 1.00,
    'lyric_line_ends_measure': 1.00,
    'lyric_line_end_on_long_duration': 1.00,
    'lyric_line_end_on_tonic': 0.60,
    'repeated_chords': 0.10,
    'measures_note_on_first_beat': 0.80,
    'num_major_minor_chords': 0.60,
    'num_tonic_triad_chords': 0.50,
    'num_distinct_chords': 0.50
}


def get_values_as_list(values, indices):
    value_list = []

    for key in indices:
        value_list.append(values[key])

    return value_list


def get_o2_values_as_list(sentiment_value=None):
    return get_values_as_list(get_o2_values(sentiment_value), objective_2_indices)


def get_o3_values_as_list(sentiment_value=None):
    return get_values_as_list(get_o3_values(sentiment_value), objective_3_indices)


def get_o2_values(sentiment_value=None):
    if sentiment_value and (sentiment_value >= 0.5 or sentiment_value <= -0.5):
        values = objective_2_values.copy()

        if sentiment_value < -3:
            values['pitch_variety'] = 0.20
            values['dissonant_intervals'] = 0.20
            values['count_stability'] = 0.65
            values['count_direction'] = 0.25
            values['diatonic_step_movement'] = 0.40
            values['note_density'] = 0.25
            values['rhythmic_variety'] = 0.30
            values['on_beat_pitches'] = 0.40
            values['semitone_steps'] = 0.30
            values['whole_notes'] = 0.20
            values['repeated_pitches'] = 0.20
        elif sentiment_value < -1.5:
            values['pitch_variety'] = 0.25
            values['dissonant_intervals'] = 0.15
            values['count_stability'] = 0.60
            values['count_direction'] = 0.30
            values['diatonic_step_movement'] = 0.40
            values['on_beat_pitches'] = 0.35
            values['semitone_steps'] = 0.25
            values['whole_notes'] = 0.15
            values['repeated_pitches'] = 0.15
        elif sentiment_value < -0.5:
            values['pitch_variety'] = 0.25
            values['dissonant_intervals'] = 0.15
            values['count_stability'] = 0.55
            values['count_direction'] = 0.40
            values['semitone_steps'] = 0.25
        elif sentiment_value < 1.5:
            values['dissonant_intervals'] = 0.00
            values['semitone_steps'] = 0.10
            values['count_direction'] = 0.65
        elif sentiment_value < 3:
            values['pitch_variety'] = 0.40
            values['dissonant_intervals'] = 0.00
            values['count_stability'] = 0.45
            values['count_direction'] = 0.70
            values['rhythmic_variety'] = 0.50
            values['semitone_steps'] = 0.10
            values['whole_notes'] = 0.05
            values['key_focus'] = 0.40
            values['rep_pitch_patterns_3'] = 0.30
            values['rep_rh_patterns_3'] = 0.30
            values['rep_pitch_patterns_4'] = 0.15
            values['rep_rh_patterns_4'] = 0.15
        else:
            values['pitch_variety'] = 0.40
            values['dissonant_intervals'] = 0.00
            values['count_stability'] = 0.40
            values['count_direction'] = 0.75
            values['note_density'] = 0.40
            values['rhythmic_variety'] = 0.50
            values['on_beat_pitches'] = 0.25
            values['semitone_steps'] = 0.10
            values['whole_notes'] = 0.05
            values['key_focus'] = 0.45
            values['16th_notes'] = 0.25
            values['rep_pitch_patterns_3'] = 0.30
            values['rep_rh_patterns_3'] = 0.30
            values['rep_pitch_patterns_4'] = 0.15
            values['rep_rh_patterns_4'] = 0.15

        return values

    return objective_2_values


def get_o3_values(sentiment_value=None):
    if sentiment_value and (sentiment_value >= 0.5 or sentiment_value <= -0.5):
        values = objective_3_values.copy()

        if sentiment_value < -3:
            values['dominant_triad_chords'] = 0.25
            values['repeated_chords'] = 0.30
            values['num_tonic_triad_chords'] = 0.60
            values['num_distinct_chords'] = 0.35
        elif sentiment_value < -1.5:
            values['dominant_triad_chords'] = 0.30
            values['repeated_chords'] = 0.20
            values['num_tonic_triad_chords'] = 0.50
            values['num_distinct_chords'] = 0.40
        elif sentiment_value < -0.5:
            values['repeated_chords'] = 0.15
            values['num_tonic_triad_chords'] = 0.45
            values['num_distinct_chords'] = 0.40
        elif sentiment_value < 1.5:
            values['repeated_chords'] = 0.15
            values['num_tonic_triad_chords'] = 0.45
        elif sentiment_value < 3:
            values['repeated_chords'] = 0.20
            values['num_tonic_triad_chords'] = 0.50
            values['num_distinct_chords'] = 0.40
        else:
            values['dominant_triad_chords'] = 0.40
            values['num_tonic_triad_chords'] = 0.40
            values['num_distinct_chords'] = 0.50

        return values

    return objective_3_values
