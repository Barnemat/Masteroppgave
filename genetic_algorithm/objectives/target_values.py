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
    'repeated_pitches_patterns',
    'repeated_melismas',
    'ends_on_tonic'
]

objective_3_indices = [
    'start_end_tonic_triad',
    'dominant_triad_chords',
    'dominant_resolved_tonic',
    'repeated_chords',
    'measures_note_on_first_beat',
    'num_tonic_triad_chords',
    'num_distinct_chords',
    'num_chords_with_4th',
    'start_end_dom_triad',
    'tonic_triads_w_flavor',
    'chord_roots_in_key',
    'following_scale_degrees',
    'semi_tone_dis_flavor_note'
]

objective_4_indices = [
    'lyric_stress_constraints',
    'lyric_line_ends_measure',
    'lyric_line_end_on_long_duration',
    'lyric_line_end_on_tonic_dom',
    'syls_span_multiple_measures'
]

objective_2_values = {
    'pitch_variety': 0.50,  # Var 0.4
    'pitch_range': 0.50,
    'key_focus': 0.35,  # Var 0.45
    'non_scale_notes': 0.00,  # IGNORED - 29.04
    'dissonant_intervals': 0.00,
    'count_direction': 0.55,
    'count_stability': 0.60,
    'diatonic_step_movement': 0.40,
    'note_density': 0.30,
    'rest_density': 0.15,
    'rhythmic_variety': 0.70,
    'rhythmic_range': 0.70,  # IGNORED - 29.04.
    'repeated_pitches': 0.15,
    'repeated_rhythms': 0.20,  # 0.25-0.30? Var 0.35
    'on_beat_pitches': 0.35,  # IGNORED - 29.04.
    'rep_pitch_patterns_3': 0.10,  # 0.1? Var 0.15
    'rep_rh_patterns_3': 0.10,
    'rep_pitch_patterns_4': 0.05,  # 0.05? Var 0.10
    'rep_rh_patterns_4': 0.10,
    'semitone_steps': 0.10,  # 0.1? Var 0.20
    '16th_notes': 0.05,
    'whole_notes': 0.05,
    'repeated_pitches_patterns': 0.00,
    'repeated_melismas': 0.20,  # IGNORED - 29.04.
    'ends_on_tonic': 1.00
}

objective_3_values = {
    'start_end_tonic_triad': 1.00,
    'dominant_triad_chords': 0.30,
    'dominant_resolved_tonic': 1.00,
    'repeated_chords': 0.10,
    'measures_note_on_first_beat': 1.00,  # Probably obsolete
    'num_tonic_triad_chords': 0.40,
    'num_distinct_chords': 0.50,
    'num_chords_with_4th': 0.30,
    'start_end_dom_triad': 0.00,
    'tonic_triads_w_flavor': 0.30,
    'chord_roots_in_key': 1.00,
    'following_scale_degrees': 1.00,
    'semi_tone_dis_flavor_note': 0.00
}

objective_4_values = {
    'lyric_stress_constraints': 1.00,
    'lyric_line_ends_measure': 1.00,
    'lyric_line_end_on_long_duration': 1.00,
    'lyric_line_end_on_tonic_dom': 0.60,
    'syls_span_multiple_measures': 0.00
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


def get_o4_values_as_list(sentiment_value=None):
    return get_values_as_list(objective_4_values, objective_4_indices)


def get_o2_values(sentiment_value=None):
    if sentiment_value and (sentiment_value > 0.1 or sentiment_value < -0.1):
        values = objective_2_values.copy()

        if sentiment_value < -0.75:
            values['pitch_variety'] = 0.25
            values['dissonant_intervals'] = 0.20
            values['count_stability'] = 0.65
            values['count_direction'] = 0.25
            values['diatonic_step_movement'] = 0.50
            values['note_density'] = 0.25
            values['rhythmic_variety'] = 0.50
            values['on_beat_pitches'] = 0.40
            values['semitone_steps'] = 0.30
            values['whole_notes'] = 0.15
            values['repeated_pitches'] = 0.20
        elif sentiment_value < -0.5:
            values['pitch_variety'] = 0.30
            values['dissonant_intervals'] = 0.20
            values['count_stability'] = 0.60
            values['count_direction'] = 0.30
            values['diatonic_step_movement'] = 0.45
            values['on_beat_pitches'] = 0.35
            values['semitone_steps'] = 0.25
            values['whole_notes'] = 0.10
            values['repeated_pitches'] = 0.20
        elif sentiment_value < -0.1:
            values['pitch_variety'] = 0.40
            values['dissonant_intervals'] = 0.15
            values['count_stability'] = 0.55
            values['count_direction'] = 0.40
            values['semitone_steps'] = 0.20
        elif sentiment_value < 0.5:
            values['dissonant_intervals'] = 0.00
            values['semitone_steps'] = 0.10
            values['count_direction'] = 0.60
        elif sentiment_value < 0.75:
            values['count_stability'] = 0.45
            values['count_direction'] = 0.70
            values['rhythmic_variety'] = 0.70
            values['semitone_steps'] = 0.10
            values['key_focus'] = 0.45
            values['rep_pitch_patterns_3'] = 0.20
            values['rep_rh_patterns_3'] = 0.20
            values['rep_pitch_patterns_4'] = 0.15
            values['rep_rh_patterns_4'] = 0.15
        else:
            values['count_stability'] = 0.40
            values['count_direction'] = 0.75
            values['rhythmic_variety'] = 0.65
            values['semitone_steps'] = 0.10
            values['key_focus'] = 0.50
            values['16th_notes'] = 0.25
            values['rep_pitch_patterns_3'] = 0.25
            values['rep_rh_patterns_3'] = 0.25
            values['rep_pitch_patterns_4'] = 0.15
            values['rep_rh_patterns_4'] = 0.15

        return values

    return objective_2_values


def get_o3_values(sentiment_value=None):
    if sentiment_value and (sentiment_value >= 0.1 or sentiment_value <= -0.1):
        values = objective_3_values.copy()

        if sentiment_value < -0.75:
            values['dominant_triad_chords'] = 0.20
            values['repeated_chords'] = 0.30
            values['num_tonic_triad_chords'] = 0.60
            values['num_distinct_chords'] = 0.35
        elif sentiment_value < -0.5:
            values['dominant_triad_chords'] = 0.20
            values['repeated_chords'] = 0.20
            values['num_tonic_triad_chords'] = 0.50
            values['num_distinct_chords'] = 0.40
        elif sentiment_value < -0.1:
            values['repeated_chords'] = 0.15
            values['num_tonic_triad_chords'] = 0.45
            values['num_distinct_chords'] = 0.40
        elif sentiment_value < 0.5:
            values['num_tonic_triad_chords'] = 0.50
        elif sentiment_value < 0.75:
            values['repeated_chords'] = 0.20
            values['num_tonic_triad_chords'] = 0.55
            values['num_distinct_chords'] = 0.40
            values['dominant_triad_chords'] = 0.40
        else:
            values['dominant_triad_chords'] = 0.40
            values['repeated_chords'] = 0.20
            values['num_tonic_triad_chords'] = 0.55
            values['num_distinct_chords'] = 0.50

        return values

    return objective_3_values
