import os


class LilyPondFileGenerator:

    def __init__(self, output, key, time_signature, lyric_syls):
        self.data = output
        self.key = key
        self.time_signature = time_signature if time_signature else '4/4'
        self.file_start = []
        self.file_end = []
        self.lyric_syls = lyric_syls

        self.set_start_of_file(os.getcwd() + '/output/lilypond_defaults/default_start')
        self.set_end_of_file(os.getcwd() + '/output/lilypond_defaults/default_end')

    def set_start_of_file(self, filename):
        with open(filename) as file:
            self.file_start = [line for line in file]

    def set_end_of_file(self, filename):
        with open(filename) as file:
            self.file_end = [line for line in file]

    def generate_file(self, path):
        if not os.path.isdir(path):
            os.mkdir(path)

        file_names = [x for x in os.listdir(path) if os.path.isfile(path + x)]
        len_files = len([file for file in file_names if file.endswith('.ly')]) + 1
        name = 'output_number_' + str(len_files) + '.ly'

        with open(path + name, 'w') as file:
            file.write(self.format_output_for_file())

    def format_output_for_file(self):
        output = ''

        for out in self.file_start:
            output += out + '\n'

        output += '<<' + self.get_frontmatter()
        output += self.get_melody_format() + '}\n'
        output += self.get_frontmatter('bass')
        output += self.get_chord_format() + '}>>'

        for out in self.file_end:
            output += out + '\n'

        return output

    def get_frontmatter(self, clef=None):
        maj_min = ' \\major' if self.key[1] == 'maj' else ' \\minor'

        output = '\\new Staff {\n'
        output += '\\absolute\n'
        output += '\\clef treble\n' if not clef else '\\clef ' + clef + '\n'
        output += '\\time ' + self.time_signature + '\n'
        output += '\\key ' + self.key[0] + maj_min + '\n'

        return output + '\n'

    def get_melody_format(self):
        output = '{\n\\autoBeamOff\n'

        for beat in self.data[0]:
            if len(beat) == 0:
                continue

            for note in beat:
                if isinstance(note, list):
                    first_mel_note = note[0]
                    sub_mel_notes = note[1:]

                    output += first_mel_note + '([ '

                    for sub_mel_note in sub_mel_notes:
                        output += sub_mel_note + ' '

                    output += ']) '
                else:
                    output += note + ' '
            output += '\n'

        output += '}\n'
        output += '\\addlyrics {\n'

        for line in self.lyric_syls:
            line[0][0] = line[0][0].capitalize()
            for word in line:
                for syl in word:
                    output += syl + ' -- '
                output += ' '
                output = output[:-4] + '\n'

        return output + '}\n'

    def get_chord_format(self):
        output = ''

        for chord in self.data[1]:
            output += chord + '\n'

        return output
