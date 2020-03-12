from math import gcd

from syllable_handling.syllable_handling import SyllableDetector

# Measures should perhaps be somewhat harcoded or moved to EA
class MeasureHandler:

  def __init__(self, syllabified_lyric):
    self.syllables = syllabified_lyric
    self.line_syl_nums = [SyllableDetector.count_syllables_line(line) for line in self.syllables]
    
    # For testing
    # print(SyllableDetector.count_syllables_lyric(self.syllables))

    '''
    for line in self.syllables:
      print(line, SyllableDetector.count_syllables_line(line))
    '''
    self.descide_3_or_4()

  # A bare minimum function for decsiding the time signature to be either 4/4 or 3/4
  # Is often wrong, because of some irregularities in syllable handling
  def descide_3_or_4(self):
    line_syl_nums = self.line_syl_nums.copy()
    i = 0
    for syl_num in line_syl_nums:
      while syl_num % 3 != 0 and syl_num % 4 != 0 and not syl_num == 2: # 2 can go either way, either add rest (3/4) or fit in a bar (4/4)
        syl_num += 1
      line_syl_nums[i] = syl_num
      i += 1

    if len(list(filter(lambda x: x % 4 == 0, line_syl_nums))) > len(list(filter(lambda x: x % 3 == 0, line_syl_nums))):
      self.measure = [4, 4]
    else:
      self.measure = [3, 4]

    # print(line_syl_nums)
    # print(self.line_syl_nums)
    # print(self.measure)
