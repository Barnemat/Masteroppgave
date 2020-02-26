import sys
import string
from nltk.corpus import cmudict
d = cmudict.dict()

sys.path.append('../')
from load_and_store import load_lyrics

legal_punctuation = '\''
punctuation = [x for x in string.punctuation if x not in legal_punctuation]
def string_cleaner(sentence):
  sentence = ''.join([word for word in sentence if word not in punctuation])
  # sentence = sentence.lower() SJEKK DENNE IGJEN
  return sentence


def text_cleaner(sentences):
  return list(map(string_cleaner, sentences))

# WORKS ONLY WITH PERFECT GRAMMAR
# https://stackoverflow.com/a/4103234
def count_syllables_word(word):
  try:
    return [len(list(y for y in x if y[-1].isdigit())) for x in d[word.lower()]]
  except KeyError:
    return [-1]

def count_syllables_line(line):
  words = {}
  words['line_total'] = 0

  line = line.split()
  for word in line:
    num_syl = count_syllables_word(word.strip())[0]
    words[word] = num_syl
    words['line_total'] += num_syl

  return words

def count_syllables_lyric(lyric):
  lines = {}
  lines['lyric_total'] = 0
  lyric = text_cleaner(lyric)
  
  for line_num in range(len(lyric)):
    num_syl = count_syllables_line(lyric[line_num])
    lines[line_num] = num_syl
    lines['lyric_total'] += num_syl['line_total']

  return lines

def lyrics_from_dir_syllable_count(directory):
  raw_lyrics = load_lyrics(directory)
  lyrics = {}

  for title in raw_lyrics:
    lyrics[title] = count_syllables_lyric(raw_lyrics[title])

  return lyrics

def print_syllable_count_lyrics(syllable_count):
  print(syllable_count)
  for lyric in syllable_count:
    print(lyric)

    for line in syllable_count[lyric]:
      print(line, syllable_count[lyric][line])
    
      for word in syllable_count[lyric][line]:
        print(syllable_count[lyric][line][word])

#print_syllable_count_lyrics(lyrics_from_dir_syllable_count('/testtekster/'))

from nltk.tokenize import SyllableTokenizer
from nltk import word_tokenize

vowels = ['a', 'e', 'i', 'o', 'u', 'y']
def is_vowel(letter): return letter.lower() in vowels

def vowel_in(sequence):
  for letter in sequence:
    if letter in vowels:
      return True

  return False

# Yes, I needs to be there, sadly
# Warning both e and u maybe straying in some cases - Upper case letters are OK, as they are pointless midword
def is_straying_vowel(letter): return letter in ['a', 'i', 'o'] or letter.isupper()

# Vokalen E (matematisk e, etc, etc.) ABC as easy as 123 etc. etc I, vurder om U skal kunne stå alene, si så fall fjern ting som .lower()
# TODO Trenger funskjon for å vaske stavelser. Vokaler som (ar)E, (you)U skal vel ikke brukes, så slå sammen med ordet før HUSK å sjekke om neste element er bindestrek (SJEKK AT rensefunk. ikke fjerner bindestrek)
# our må sjekkes!
# TODO Trenger kanskje funskjon for å vaske didnt, dont etc. Fungerer kanskje best å anta at teksten inn er ganske ren, men tja
# TODO se på flere endelser, samt midtvokaler som bør stå alene 'the-a-tre', 'ar-e-a' (mulig?)

def sequence_endswith(text, sequence):
  for item in sequence:
    if text.endswith(item):
      return True

  return False

def has_proper_phoneme(syllables):
  word = ''.join(x for x in syllables)

  if word in d:
    print(word)
    print(d[word])

def handle_straying_vowels(syllables):
  index = 0
  for last_syllable in syllables:
    if len(syllables) > 2: break # Only considers syllables that are two syllables, but should be three
    if len(last_syllable) < 3: # if the syllable is less than two letters it's fair to presume that it should still be one syllable
      index += 1
      continue

    last_syllable_letter = last_syllable[len(last_syllable) - 1]
    last_syllable_prev_letter = last_syllable[len(last_syllable) - 2]

    if last_syllable_letter == 'i' and index < len(syllables) - 1: continue # I-letters could be trailing, but are not alone in the middle of words

    if last_syllable_letter != last_syllable_prev_letter and is_straying_vowel(last_syllable_letter) and is_vowel(last_syllable_prev_letter):
      has_proper_phoneme(syllables)
      last_syllable = last_syllable[:len(last_syllable) - 1]
      syllables = syllables[:index] + [last_syllable] + [last_syllable_letter] + syllables[index + 1:]

    index += 1
  return syllables

def split_on_er(syllables):
  syllable = syllables[len(syllables) - 1]
  if syllable.endswith('er') and len(syllable) > 2:
    syl_without_er = syllable[:len(syllable) - 2]

    if is_vowel(syl_without_er[len(syl_without_er) - 1]):
      return syllables
    else:
      new_elements = syllables[:len(syllables) - 1] if len(syllables) > 1 else ['']
      new_elements[len(new_elements) - 1] += syl_without_er
      return new_elements + ['er']
  
  return syllables

# Checks if combining first and last letters of syllables should be combined
def cons_to_correct_syl(syllables):
  return syllables

def handle_eds(syllables):
  if len(syllables) < 2: return syllables

  last_syllable = syllables[len(syllables) - 1]
  prev_syllable = syllables[len(syllables) - 2]
  prev_syllable_letter = prev_syllable[len(prev_syllable) - 1]

  if len(last_syllable) < 4 and last_syllable.endswith('ed') and (last_syllable[0] == prev_syllable_letter or (is_vowel(prev_syllable_letter) and (prev_syllable_letter == 'i' or not is_straying_vowel(prev_syllable_letter)))):
    return syllables[:len(syllables) - 2] + [prev_syllable + last_syllable]

  return syllables

def syllable_as_list_cleaner(syl_list):
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
    print(syl_list)
    if num_syls > 1:
      if syl_index == num_syls - 1 and is_vowel(item):
        syl_list[syl_index - 1] = prev_item + item
        del syl_list[syl_index]
        num_syls -= 1
        continue
      elif syl_index == 1 and is_vowel(prev_item):
        syl_list[syl_index - 1] = prev_item + item
        del syl_list[syl_index]
        num_syls -= 1
        continue

      lowered_item = item.lower()
      if syl_index == num_syls - 1 and (len(lowered_item) < 3 and lowered_item.endswith('e') or lowered_item in one_syl_special_endings or (len(lowered_item) < 4 and sequence_endswith(lowered_item, combining_syllable_suffixes))):
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

      if syl_index > 0 and is_vowel(prev_item[len(prev_item) - 1]) and is_vowel(item[0]):
        syl_list[syl_index - 1] = prev_item + item
        del syl_list[syl_index]
        num_syls -= 1
        continue 

    syl_index += 1
  print(syl_list)
  return cons_to_correct_syl(handle_eds(split_on_er(handle_straying_vowels(syl_list)))) # Remove uneseccary methods

# Combines vowels in char_array that are combined in phonemes and combines neighboring consonants
# Trailing consonants are added to last vowel
def combine_vowels_and_neighboring_consts(main_char_list, main_phonemes):
  new_parts = []
  char_list = main_char_list.copy()
  phonemes = main_phonemes.copy()

  # ['r', 'e', 'a', 'd', 'y']
  # R EH1 D IY0
  
  char = char_list.pop(0)
  current_phoneme = phonemes.pop(0)
  first = False
  while len(phonemes) > 0:
    if not current_phoneme: break
    word = ''

    while len(char_list) > 0 and not is_vowel(char):
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

    while len(char_list) > 0 and is_vowel(char):
      if len(phonemes) > 0 and current_phoneme[len(current_phoneme) - 1].isnumeric() and phonemes[0][len(phonemes[0]) - 1].isnumeric():
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
  last_element = new_parts[len(new_parts) - 1]
  last_phonemes = main_phonemes[len(main_phonemes) - 2:]
  if last_element == 'e':
    new_parts[len(new_parts) - 2] = new_parts[len(new_parts) - 2] + last_element
    del new_parts[len(new_parts) - 1]
  elif last_element == 'ed' and is_vowel(last_phonemes[0][0]) and last_phonemes[1].lower() == 'd':
    new_parts[len(new_parts) - 1] = 'e'
    new_parts.append('d')
  
  last_element = new_parts[len(new_parts) - 1]
  if len(last_element) > 2 and last_element.endswith('re') and main_phonemes[len(main_phonemes) - 1].startswith('ER'):
    new_parts[len(new_parts) - 1] = last_element[:len(last_element) - 2]
    new_parts.append('re')

  return new_parts

def combine_phonemes(phonemes, char_list):
  new_parts = []

  part = ''
  first = False
  for phoneme in phonemes:
    if is_vowel(phoneme[0]):
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
  last_element = new_parts[len(new_parts) - 1]
  
  if len(last_element) == 2 and not is_vowel(last_element[0]) and not is_vowel(last_element[1]):
    new_parts[len(new_parts) - 1] = last_element[:len(last_element) - 1]
    new_parts.append(last_element[1:])

  return new_parts

def update_syllable_matrix(indices, syllable_matrix, start_index):
  for i in reversed(indices):
    syllable_matrix[i] = start_index
    
    if i > 0 and not syllable_matrix[i - 1]:
      syllable_matrix[i - 1] = start_index
    if i < len(syllable_matrix) - 1 and not syllable_matrix[i + 1]:
      syllable_matrix[i + 1] = start_index
    start_index += 1

def get_syllable_matrix(phonemes, char_list):
  syllable_matrix = [None for x in range(len(phonemes))]

  for i in range(len(syllable_matrix)):
    last_phoneme_element = phonemes[i][len(phonemes[i]) - 1]
    
    if last_phoneme_element.isnumeric():
      syllable_matrix[i] = last_phoneme_element


  one_indices = [x for x in range(len(syllable_matrix)) if syllable_matrix[x] == '1']
  two_indices = [x for x in range(len(syllable_matrix)) if syllable_matrix[x] == '2']
  zero_indices = [x for x in range(len(syllable_matrix)) if syllable_matrix[x] == '0']

  index = 1
  update_syllable_matrix(one_indices, syllable_matrix, index)
  index += len(one_indices)
  update_syllable_matrix(two_indices, syllable_matrix, index)
  index += len(two_indices)
  update_syllable_matrix(zero_indices, syllable_matrix, index)


  for i in range(len(syllable_matrix) - 1, 0, -1):
    if not syllable_matrix[i]:
      syllable_matrix[i] = syllable_matrix[i - 1]

  return syllable_matrix

def syllables_from_cmudict(word):
  lowered = word[0].isupper()
  word = word.lower()
  phonemes = d[word]
  char_list = [x for x in word]
  # print(char_list)
  # print(phonemes)

  char_list = combine_vowels_and_neighboring_consts(char_list, phonemes[0])
  combined_phonemes = combine_phonemes(phonemes[0], char_list)

  # print(char_list)
  # print(combined_phonemes)

  # TODO - figure out a way to handle different lengths
  if len(char_list) != len(combined_phonemes):
    raise Exception('char_list and combined_phonemes should be equal in length')

  syllable_matrix = get_syllable_matrix(combined_phonemes, char_list)
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

  print('Syllables: ', syllables)

  return syllables

def syllabified_line_cleaner(line):
  if len(line) == 0: return []

  num_words = len(line)
  word_index = 0
  while word_index < num_words:
    
    # Handles straying puntuation and adds them to the previous word - MAY BE REMOVED
    if word_index == 0 and line[0][0] in string.punctuation:
      del line[0]
      num_words -= 1
      continue
    elif word_index > 0 and line[word_index][0] in string.punctuation:
      line[word_index - 1] += line[word_index]
      del line[word_index]
      num_words -= 1
      continue

    line[word_index] = syllable_as_list_cleaner(line[word_index])
    word_index += 1

  '''
  # Handle edge case where the last syllable in line is punctuation - MAY BE REMOVED
  last_index = len(line) - 1
  if line[last_index][0] in string.punctuation:
    line[last_index - 1] += line[last_index]
    del line[last_index]
    '''
  line = [x for x in line if len(x) > 0]
  return line

def find_syllables_word(word):
  lowered_word = word.lower()
  try:
    # if lowered_word in d and len(d[lowered_word][0]) > 0: Add if-test back if the try-block is removed
    return syllables_from_cmudict(word)
  except:
    SSP = SyllableTokenizer()
    return SSP.tokenize(word)

def find_syllables_line(line):
  words = []
  
  line = line.split()
  #line = word_tokenize(line)
  for word in line:
    words.append(find_syllables_word(word))

  return syllabified_line_cleaner(words)

def find_syllables_lyric(lyric):
  lines = {}
  lyric = text_cleaner(lyric) #SJEKK DENNE IGJEN
  
  for line_num in range(len(lyric)):
    syls = find_syllables_line(lyric[line_num])
    
    if len(syls) > 0:
      lines[line_num] = syls

  lines['lyric_total'] = sum([len(lines[x]) for x in lines])

  return lines

def lyrics_from_dir_syllable_find(directory):
  raw_lyrics = load_lyrics(directory)
  lyrics = {}

  for title in raw_lyrics:
    lyrics[title] = find_syllables_lyric(raw_lyrics[title])

  return lyrics

def print_syllable_find_lyrics(syllables_found):
  for title in syllables_found:
    print(title)

    for line in syllables_found[title]:
      print(line, syllables_found[title][line])
    
      #for word in syllables_found[lyric][line]:
        #print(syllables_found[lyric][line][word])

print_syllable_find_lyrics(lyrics_from_dir_syllable_find('/testtekster/'))
# lyrics_from_dir_syllable_find('/testtekster/')
