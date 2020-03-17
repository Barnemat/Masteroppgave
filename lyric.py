from syllable_handling.syllable_handling import SyllableDetector
from syllable_handling.measure_handling import MeasureHandler

# TODO Need to implement methods for defining verses, choruses, breaks etc.
# For initial development, use only verses.


class Lyric:
    def __init__(self, lyric):
        self.lyric = lyric
        self.syllable_detector = SyllableDetector(lyric)
        self.measure_handler = MeasureHandler(self.get_syllables())

    def get_syllables(self):
        return self.syllable_detector.find_syllables_lyric()
