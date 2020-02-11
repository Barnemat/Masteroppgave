'''
  Main inspiration taken from: 
  https://towardsdatascience.com/calculating-string-similarity-in-python-276e18a7d33a
'''

from sklearn.metrics.pairwise import cosine_similarity
from sklearn.feature_extraction.text import CountVectorizer

# Remember to clean the sentences
def get_cosine_similarities(sentences):
  #sentences = text_cleaner(sentences)

  vectorizer = CountVectorizer().fit_transform(sentences)
  vectors = vectorizer.toarray()

  similarities = cosine_similarity(vectors)
  return similarities

def get_cosine_sim_between_vectors(v1, v2):
  v1 = v1.reshape(1, -1)
  v2 = v2.reshape(1, -1)

  return cosine_similarity(v1, v2)[0][0]

