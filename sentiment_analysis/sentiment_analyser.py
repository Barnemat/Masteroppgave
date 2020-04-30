import string
from nltk.sentiment.vader import SentimentIntensityAnalyzer
from statistics import mean

from load_and_store import load_lyrics  # TODO FIX
from sentiment_analysis.cosine_similarity import get_cosine_similarities

# Add more cleaning, if needed
def string_cleaner(sentence):
  sentence = ''.join([word for word in sentence if word not in string.punctuation])
  sentence = sentence.lower()

  return sentence


def text_cleaner(sentences):
  return list(map(string_cleaner, sentences))


# Used to remove repeated or overly similar song lines in the evaluation (chorus, etc.)
def clean_lyric(lyric):
  cleaned_lyric = text_cleaner(lyric)
  cosine_sims = get_cosine_similarities(cleaned_lyric)
  sim_threshold = 0.8 # Kan muligens tweakes
  removed_indices = set()

  for index in range(len(cleaned_lyric)):
    similarities = cosine_sims[index]
    for sim_index in range(index, len(similarities)):
      if index == sim_index: continue

      if similarities[sim_index] >= sim_threshold and sim_index not in removed_indices:
        removed_indices.add(sim_index)
        break

  removed_indices = list(removed_indices)
  removed_indices.sort(reverse = True)

  for i in removed_indices:
    cleaned_lyric.pop(i)

  #print(removed_indices)
  #print(cleaned_lyric)
  #print(cosine_sims)
  return cleaned_lyric


def lyric_analyser(sentences, directory = None, lyric = None):
  if not directory and not lyric: return

  lyrics = load_lyrics(directory) if directory else lyric
  sid = SentimentIntensityAnalyzer()

  for title in lyrics:
    print(title)

    acc_scores = { 'neg': 0.0, 'neu': 0.0, 'pos': 0.0, 'compound': 0.0 }
    scores = []

    complete_lyric = ''
    lines = 0
    #for line in clean_lyric(lyrics[title]):
    for line in lyrics[title]:
      if line.strip() == '': continue

      line_scores = sid.polarity_scores(line)
      scores.append(line_scores)
      complete_lyric += line

      for key in line_scores:
        acc_scores[key] += line_scores[key]

      # print(line, line_scores)
      lines += 1
    acc_scores_sum = 0
    for key in acc_scores:
      #if key == 'compound': continue

      acc_scores[key] = acc_scores[key] / lines
      if key != 'compound':
        acc_scores_sum += acc_scores[key]

    complete_lyric_scores = sid.polarity_scores(complete_lyric)
    data = find_sentiment_compounds(scores, complete_lyric_scores)
    #print('Accumulated scores: ', acc_scores)
    #print('Accumulated scores total: ', acc_scores_sum)
    print('Full text score: ', complete_lyric_scores)
    print('From find_sentiment: ', data) # Find sentiment scans each line in the lyric independently
    #print('Normalized: ', normalize(data, -4, 4))
    print('')

    return data


# Result based on accumulated compound values from sentences
# Extra negative and extra positive values are introduced
def find_sentiment(scores):
  neg_threshold = -0.04 # originaly -0.05
  ex_neg_threshold = -0.45 # novel
  pos_threshold = 0.04 # originaly 0.05
  ex_pos_threshold = 0.75 # novel
  lines = len(scores)

  # defines boost values for extra negative/positive lines
  ex_neg_multiplier = 2.0
  ex_pos_multiplier = 1.5

  #acc_sentences = { 'ex_neg': 0.0, 'neg': 0.0, 'neu': 0.0, 'pos': 0.0, 'ex_pos': 0.0 }
  #acc_sentences = { 'neg': 0.0, 'neu': 0.0, 'pos': 0.0 }
  acc_sentences = { 'neg': 0.0, 'neu': 0.0, 'pos': 0.0, 'compound': 0.0 }

  for score in scores:
    compound = score['compound']

    acc_sentences['compound'] += compound

    if compound < neg_threshold:
      if compound <= ex_neg_threshold:
        acc_sentences['neg'] += ex_neg_multiplier
        lines += ex_neg_multiplier - 1
      else:
        acc_sentences['neg'] += 1
    elif compound >= pos_threshold:
      if compound >= ex_pos_threshold:
        acc_sentences['pos'] += ex_pos_threshold
        lines += ex_pos_multiplier - 1
      else:
        acc_sentences['pos'] += 1
    else:
      acc_sentences['neu'] += 1

  # Trengs mest sannsynligvis ikke -v
  chances = {}
  for key in acc_sentences:
    chances[key] = round((acc_sentences[key] / lines), 2)

  print(normalize(acc_sentences, -1, 1))

  # Kanskje også fjerne nøytral helt, men si at nøytral gir (noe) større sannsynlighet for dur?
  # neu = acc_sentences['neu'] / 2
  # acc_sentences['neu'] = 0.0
  # acc_sentences['pos'] += neu
  # acc_sentences['neg'] += neu
  #return chances
  return acc_sentences

# Result based on accumulated compound values from sentences
# Extra negative and extra positive values are introduced
def find_sentiment_compounds(scores, lyric_scores = None):
  neg_threshold = -0.05 # originaly -0.05
  ex_neg_threshold = -0.40 # novel
  pos_threshold = 0.05 # originaly 0.05
  ex_pos_threshold = 0.8 # novel
  lines = len(scores)

  # defines boost values for extra negative/positive lines
  neg_multiplier = 1.5
  pos_multiplier = 1.0
  ex_neg_multiplier = 2
  ex_pos_multiplier = 1.25

  compounds = []
  i = 1
  for score in scores:
    compound = score['compound']
    if compound == 0:
        continue

    # print(i, score)

    if compound < neg_threshold:
      if compound < ex_neg_threshold:
        compound *= ex_neg_multiplier
      else:
        compound *= neg_multiplier
    elif compound > pos_threshold:
      if compound > ex_pos_threshold:
        compound *= ex_pos_multiplier
      else:
        compound *= pos_multiplier

    compounds.append(compound)
    i += 1
  # print(compounds)
  # print([normalize_compounds(compounds, -1, 1)] + [lyric_scores['compound']])

  return round(normalize_compounds(compounds, -1, 1), 1)


def normalize_compounds(data, a, b, x = None):
  x_min = min(data) if min(data) < -1 else -1
  x_max = max(data) if max(data) > 1 else 1

  x_max_min = x_max - x_min if x_max - x_min != 0 else x_max

  x = x if x else mean(data)
  return a + (((x - x_min) * (b - a)) / (x_max_min))

# Min-Max Feature scaling
# TODO Gjør mer effektiv, hvis brukt flittig
def normalize(data, a, b):
  x_min = -1.0
  x_max = 1.0

  # choice([-1, 1])
  data_as_values = [-1.0 for x in range(int(data['neg']))] + [0.0 for x in range(int(data['neu']))] + [1.0 for x in range(int(data['pos']))]
  print(data_as_values)
  x = sum(data_as_values) / len(data_as_values)

  return a + ((x - x_min) * (b - a) / (x_max - x_min))


def sentence_analyser(sentence):
  pass

lyric_analyser(True, '/testtekster/')
