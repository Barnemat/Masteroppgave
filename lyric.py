from syllable_handling.syllable_handling import SyllableDetector
from syllable_handling.measure_handling import MeasureHandler
from sentiment_analysis.sentiment_analyser import lyric_analyser

# TODO Need to implement methods for defining verses, choruses, breaks etc.
# For initial development, use only verses.


class Lyric:
    def __init__(self, lyric, title):
        self.title = title
        self.lyric = lyric[1:]
        self.syllable_detector = SyllableDetector(get_first_verse(self.lyric))
        self.measure_handler = MeasureHandler(self.get_syllables())
        self.sentiment = lyric_analyser(True, lyric={title: self.lyric})

    def get_syllables(self):
        return self.syllable_detector.find_syllables_lyric()

    def get_sentiment(self):
        return self.sentiment


def get_first_verse(lyric):
    '''
        For the sake of testing only the first verse should be part of music generation
        For the time being sentiment value is based on whole lyric # TODO: Might change
    '''
    first_verse = []

    for line in lyric:
        if len(line) == 0:
            break

        first_verse.append(line)

    return first_verse
