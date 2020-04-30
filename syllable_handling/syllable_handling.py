import sys
import string
from nltk.corpus import cmudict
from nltk.tokenize import SyllableTokenizer

sys.path.append('../') # Finn bedre løsning på dette
from load_and_store import load_lyrics # Kan fjernes. Input blir fra hoevklasse

# TODO Cmudict-løsningen husker ikke på stor forbokstav
# TODO: Fix indentation if time. Ha tunga rett i munnen i så fall.
class SyllableDetector:
  d = cmudict.dict()
  vowels = ['a', 'e', 'i', 'o', 'u', 'y']
  legal_punctuation = '\''
  punctuation = None

  def __init__(self, lyric):
    self.lyric = lyric
    self.syllables = []
    self.punctuation = [x for x in string.punctuation if x not in self.legal_punctuation]
    self.syllables = self.find_syllables_lyric()


  def string_cleaner(self, sentence):
    sentence = ''.join([word for word in sentence if word not in self.punctuation])
    return sentence


  def text_cleaner(self, sentences):
    return list(map(self.string_cleaner, sentences))


  def is_vowel(self, letter): return letter.lower() in self.vowels


  # Not used, might be deleted
  def vowel_in(self, sequence):
    for letter in sequence:
      if letter in vowels:
        return True

    return False

  # Yes, I needs to be there, sadly
  # Warning both e and u maybe straying in some cases - Upper case letters are OK, as they are pointless midword
  def is_straying_vowel(self, letter): return letter in ['a', 'i', 'o'] or letter.isupper()


  def sequence_endswith(self, text, sequence):
    for item in sequence:
      if text.endswith(item):
        return True

    return False

  # Checks if a syllable exists as word in cmudict and checks if it has one syllable
  def has_one_syl_phoneme(self, syllable):
    vowel_sum = 0
    if syllable.lower() in self.d:
      syl_phonemes = self.d[syllable.lower()]

      for phoneme in syl_phonemes[0]:
        if self.is_vowel(phoneme[0]):
          vowel_sum += 1

        if vowel_sum > 1: return False

      if vowel_sum == 1: return True
    return False


  def handle_straying_vowels(self, syllables):
    index = 0
    for last_syllable in syllables:
      if len(syllables) > 2: break # Only considers syllables that are two syllables, but should be three
      if len(last_syllable) < 3 or self.has_one_syl_phoneme(last_syllable): # if the syllable is less than two letters it's fair to presume that it should still be one syllable
        index += 1
        continue

      last_syllable_letter = last_syllable[-1]
      last_syllable_prev_letter = last_syllable[-2]

      if last_syllable_letter == 'i' and index < len(syllables) - 1: continue # I-letters could be trailing, but are not alone in the middle of words

      if last_syllable_letter != last_syllable_prev_letter and self.is_straying_vowel(last_syllable_letter) and self.is_vowel(last_syllable_prev_letter):
        # self.has_proper_phoneme(syllables)
        last_syllable = last_syllable[:len(last_syllable) - 1]
        syllables = syllables[:index] + [last_syllable] + [last_syllable_letter] + syllables[index + 1:]

      index += 1
    return syllables

  def split_on_er(self, syllables):
    syllable = syllables[-1]
    if syllable.endswith('er') and len(syllable) > 2:
      syl_without_er = syllable[:len(syllable) - 2]

      if self.is_vowel(syl_without_er[-1]):
        return syllables
      else:
        new_elements = syllables[:len(syllables) - 1] if len(syllables) > 1 else ['']
        new_elements[-1] += syl_without_er
        return new_elements + ['er']

    return syllables

  # Checks if combining first and last letters of syllables should be combined
  def cons_to_correct_syl(self, syllables):
    return syllables

  def handle_eds(self, syllables):
    if len(syllables) < 2: return syllables

    last_syllable = syllables[-1]
    prev_syllable = syllables[-2]
    prev_syllable_letter = prev_syllable[-1]

    if len(last_syllable) < 4 and last_syllable.endswith('ed') and (last_syllable[0] == prev_syllable_letter or (self.is_vowel(prev_syllable_letter) and (prev_syllable_letter == 'i' or not self.is_straying_vowel(prev_syllable_letter)))):
      return syllables[:len(syllables) - 2] + [prev_syllable + last_syllable]

    return syllables

  def syllable_as_list_cleaner(self, syl_list):
    num_syls = len(syl_list)
    last_index = num_syls - 1

    syl_index = 0
    while syl_index < num_syls:
      item = syl_list[syl_index]
      prev_item = '' if syl_index == 0 else syl_list[syl_index - 1]

      # 're-and-s-cleaner - are and derived words are weird are, you're, she's (...) should all be 1 syllable - Noe her må flyttes til linjerens
      one_syl_special_endings = ['\'m', '\'re', '\'s', 'ur', '\'t', '\'ll', '\'d', 're\'s']
      combining_syllable_suffixes = ['es'] # ed?!

      # Handles straying vowels - '['yo', 'u'] should e.g. be ['you']'
      #print(syl_list)
      if num_syls > 1:
        if syl_index == num_syls - 1 and self.is_vowel(item):
          syl_list[syl_index - 1] = prev_item + item
          del syl_list[syl_index]
          num_syls -= 1
          continue
        elif syl_index == 1 and self.is_vowel(prev_item):
          syl_list[syl_index - 1] = prev_item + item
          del syl_list[syl_index]
          num_syls -= 1
          continue

        lowered_item = item.lower()
        if syl_index == num_syls - 1 and (len(lowered_item) < 3 and lowered_item.endswith('e') or lowered_item in one_syl_special_endings or (len(lowered_item) < 4 and self.sequence_endswith(lowered_item, combining_syllable_suffixes))):
          syl_list[syl_index - 1] = prev_item + item
          del syl_list[syl_index]
          num_syls -= 1
          syl_index -= 1
          continue
        elif syl_index < num_syls - 1 and item == '\'':
          syl_list[syl_index] = item + syl_list[syl_index + 1]
          del syl_list[syl_index + 1]
          num_syls -= 1
          continue

        if syl_index > 0 and self.is_vowel(prev_item[-1]) and self.is_vowel(item[0]):
          syl_list[syl_index - 1] = prev_item + item
          del syl_list[syl_index]
          num_syls -= 1
          continue

      syl_index += 1
    # print(syl_list)
    return self.cons_to_correct_syl(self.handle_eds(self.split_on_er(self.handle_straying_vowels(syl_list)))) # Remove uneseccary methods

  # Combines vowels in char_array that are combined in phonemes and combines neighboring consonants
  # Trailing consonants are added to last vowel
  def combine_vowels_and_neighboring_consts(self, main_char_list, main_phonemes):
    new_parts = []
    char_list = main_char_list.copy()
    phonemes = main_phonemes.copy()

    # Eks. på char_list og phonemes fra cmudict
    # ['r', 'e', 'a', 'd', 'y']
    # R EH1 D IY0

    char = char_list.pop(0)
    current_phoneme = phonemes.pop(0)
    first = False
    while len(phonemes) > 0:
      if not current_phoneme: break
      word = ''

      while len(char_list) > 0 and not self.is_vowel(char):
        if first:
          new_parts.append(char)
        else:
          word += char
        char = char_list.pop(0)

      if len(word) > 0:
        new_parts.append(word)
        word = ''

      while len(phonemes) > 0 and not current_phoneme[len(current_phoneme) - 1].isnumeric():
        current_phoneme = phonemes.pop(0)
        first = True

      while len(char_list) > 0 and self.is_vowel(char):
        if len(phonemes) > 0 and current_phoneme[-1].isnumeric() and phonemes[0][-1].isnumeric():
          if len(word) > 0:
            new_parts.append(word)

          new_parts.append(char)
          char = char_list.pop(0)
          current_phoneme = phonemes.pop(0)
          word = ''
          continue
        else:
          word += char
          char = char_list.pop(0)

      if len(char_list) == 0 and not word.endswith(char):
        word += char
        new_parts.append(word)
        break


      if len(word) > 0: new_parts.append(word)
      current_phoneme = phonemes.pop(0) if len(phonemes) > 0 else None

    chars_in_new_parts = ''.join(new_parts)
    if len(main_char_list) > len(chars_in_new_parts):
      difference = len(main_char_list) - len(chars_in_new_parts)
      chars = ''.join([main_char_list[x] for x in range(len(main_char_list) - difference, len(main_char_list))])
      new_parts.append(chars)

    # Handles silent e in word endings
    last_element = new_parts[-1]
    last_phonemes = main_phonemes[len(main_phonemes) - 2:]
    if last_element == 'e':
      new_parts[-2] = new_parts[-2] + last_element
      del new_parts[-1]
    elif last_element == 'ed' and self.is_vowel(last_phonemes[0][0]) and last_phonemes[1].lower() == 'd':
      new_parts[-1] = 'e'
      new_parts.append('d')

    last_element = new_parts[-1]
    if len(last_element) > 2 and last_element.endswith('re') and main_phonemes[-1].startswith('ER'):
      new_parts[-1] = last_element[:len(last_element) - 2]
      new_parts.append('re')

    return new_parts

  def combine_phonemes(self, phonemes, char_list):
    new_parts = []

    part = ''
    first = False
    for phoneme in phonemes:
      if self.is_vowel(phoneme[0]):
        first = True
        if len(part) > 0:
          new_parts.append(part)
          part = ''

        new_parts.append(phoneme)
      else:
        if first:
          new_parts.append(phoneme)
        else:
          part += phoneme

    if len(part) > 0:
      new_parts.append(part)

    c_list_len = len(char_list)
    last_element = new_parts[-1]

    if len(last_element) == 2 and not self.is_vowel(last_element[0]) and not self.is_vowel(last_element[1]):
      new_parts[-1] = last_element[:len(last_element) - 1]
      new_parts.append(last_element[1:])

    return new_parts

  def update_syllable_matrix(self, indices, syllable_matrix, start_index):
    for i in reversed(indices):
      syllable_matrix[i] = start_index

      if i > 0 and not syllable_matrix[i - 1]:
        syllable_matrix[i - 1] = start_index
      if i < len(syllable_matrix) - 1 and not syllable_matrix[i + 1]:
        syllable_matrix[i + 1] = start_index
      start_index += 1

  def get_syllable_matrix(self, phonemes, char_list):
    syllable_matrix = [None for x in range(len(phonemes))]

    for i in range(len(syllable_matrix)):
      last_phoneme_element = phonemes[i][-1]

      if last_phoneme_element.isnumeric():
        syllable_matrix[i] = last_phoneme_element


    one_indices = [x for x in range(len(syllable_matrix)) if syllable_matrix[x] == '1']
    two_indices = [x for x in range(len(syllable_matrix)) if syllable_matrix[x] == '2']
    zero_indices = [x for x in range(len(syllable_matrix)) if syllable_matrix[x] == '0']

    index = 1
    self.update_syllable_matrix(one_indices, syllable_matrix, index)
    index += len(one_indices)
    self.update_syllable_matrix(two_indices, syllable_matrix, index)
    index += len(two_indices)
    self.update_syllable_matrix(zero_indices, syllable_matrix, index)


    for i in range(len(syllable_matrix) - 1, 0, -1):
      if not syllable_matrix[i]:
        syllable_matrix[i] = syllable_matrix[i - 1]

    return syllable_matrix

  def syllables_from_cmudict(self, word):
    lowered = word[0].isupper()
    word = word.lower()
    phonemes = self.d[word]
    char_list = [x for x in word]
    # print(char_list)
    # print(phonemes)

    char_list = self.combine_vowels_and_neighboring_consts(char_list, phonemes[0])
    combined_phonemes = self.combine_phonemes(phonemes[0], char_list)

    # print(char_list)
    # print(combined_phonemes)
    # TODO - figure out a way to handle different lengths
    if len(char_list) != len(combined_phonemes):
      raise Exception('char_list and combined_phonemes should be equal in length')

    syllable_matrix = self.get_syllable_matrix(combined_phonemes, char_list)
    # print(syllable_matrix)
    # print(char_list)

    syllables = []
    last_index = syllable_matrix[0]
    syllable = ''
    for i in range(len(syllable_matrix)):
      if last_index != syllable_matrix[i]:
        syllables.append(syllable)
        syllable = char_list[i]
        last_index = syllable_matrix[i]
      else:
        syllable += char_list[i]

    syllables.append(syllable)

    # print('Syllables: ', syllables)

    return syllables

  # no_clean ignores words from cmudict
  def syllabified_line_cleaner(self, line):
    if len(line) == 0: return []

    num_words = len(line)
    word_index = 0
    while word_index < num_words:

      '''
      # Handles straying puntuation and adds them to the previous word - MAY BE REMOVED
      if word_index == 0 and line[0][0][0] in string.punctuation:
        del line[0][0][0]
        num_words -= 1
        continue
      elif word_index > 0 and line[word_index][0][0] in string.punctuation:
        line[word_index - 1][0] += line[word_index][0]
        del line[word_index][0]
        num_words -= 1
        continue
      '''

      line[word_index][0] = self.syllable_as_list_cleaner(line[word_index][0]) if not line[word_index][1] else line[word_index][0]
      word_index += 1

    '''
    # Handle edge case where the last syllable in line is punctuation - MAY BE REMOVED
    last_index = len(line) - 1
    if line[last_index][0] in string.punctuation:
      line[last_index - 1] += line[last_index]
      del line[last_index]
      '''
    line = [x[0] for x in line if len(x[0]) > 0]
    return line

  def find_syllables_word_from_cmudict(self, word):
    lowered_word = word.lower()

    # if lowered_word in d and len(d[lowered_word][0]) > 0: Add if-test back if the try-block is removed
    return self.syllables_from_cmudict(word)

  def find_syllables_word(self, word):
    lowered_word = word.lower()

    SSP = SyllableTokenizer()
    return SSP.tokenize(word)


  def find_syllables_line(self, line):
    words = []

    line = line.split()
    for word in line:
      try:
        syls = [self.find_syllables_word_from_cmudict(word), True]
      except:
        syls = [self.find_syllables_word(word), False]
      words.append(syls)

    return self.syllabified_line_cleaner(words) # Her skjer det noe veldig rart med bl.a. 'eas, y' og 'read, y' og 'ar - e - a' - Disse er riktig fra funksjon

  def find_syllables_lyric(self):
    if len(self.syllables) > 0: return self.syllables

    lines = []
    lyric = self.text_cleaner(self.lyric)

    for line_num in range(len(lyric)):
      syls = self.find_syllables_line(lyric[line_num])

      if len(syls) > 0:
        lines.append(syls)

    self.syllables = lines
    return lines

  def print_syllables(self):
    if len(self.syllables) > 0:

      for line in self.syllables:
        print(line)


  def count_syllables_word(word):
    return len(word)


  def count_syllables_line(line):
    syl_sum = 0

    for word in line:
      syl_sum += SyllableDetector.count_syllables_word(word)

    return syl_sum


  def count_syllables_lyric(lyric):
    syl_sum = 0

    for line in lyric:
      syl_sum += SyllableDetector.count_syllables_line(line)

    return syl_sum


# Flyttes til annen klasse
def lyrics_from_dir_syllable_find(directory):
  raw_lyrics = load_lyrics(directory)
  lyrics = {}

  for title in raw_lyrics:
    lyrics[title] = find_syllables_lyric(raw_lyrics[title])

  return lyrics

#Flyttes til annen klasse
def print_syllable_find_lyrics(syllables_found):
  for title in syllables_found:
    print(title)

    for line in syllables_found[title]:
      print(line, syllables_found[title][line])
