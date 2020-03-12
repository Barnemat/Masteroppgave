from syllable_handling.syllable_handling import SyllableDetector
from syllable_handling.measure_handling import MeasureHandler
from load_and_store import load_lyrics

# TODO Need to implement methods for defining verses, choruses, breaks etc.
# For initial development, use only verses.

class Lyric:
  def __init__(self, lyric):
    self.lyric = lyric
    self.syllable_detector = SyllableDetector(lyric)
    self.measure_handler = MeasureHandler(self.get_syllables())

  def get_syllables(self):
    return self.syllable_detector.find_syllables_lyric()

def main():
  texts = load_lyrics('/syllable_handling/testtekster/')
  lyrics = [Lyric(texts[title]) for title in texts]
  # lyric = Lyric(text)
  # lyric.syllable_detector.print_syllables()


main()