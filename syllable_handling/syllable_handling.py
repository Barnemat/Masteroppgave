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

# FIKS there's you're etc..!!
def syllable_as_list_cleaner(syl_list):
  num_syls = len(syl_list)
  last_index = num_syls - 1
  
  syl_index = 0
  while syl_index < num_syls:
    item = syl_list[syl_index]
    prev_item = '' if syl_index == 0 else syl_list[syl_index - 1]

    # 're-and-s-cleaner - are and derived words are weird are, you're, she's (...) should all be 1 syllable - Noe her må flyttes til linjerens
    one_syl_special_endings = ['\'m', '\'re', '\'s', 'ur', '\'t', '\'ll']
    combining_syllable_suffixes = ['es', 'ed']

    # Handles straying vowels - '['yo', 'u'] should e.g. be ['you']'
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
      if syl_index == num_syls - 1 and (len(lowered_item) < 3 and lowered_item.endswith('e') or lowered_item in one_syl_special_endings or sequence_endswith(lowered_item, combining_syllable_suffixes)):
        syl_list[syl_index - 1] = prev_item + item
        del syl_list[syl_index]
        num_syls -= 1
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

  return syl_list

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

    # I'm - don't cleaner

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
