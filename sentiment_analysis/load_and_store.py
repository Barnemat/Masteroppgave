import os

def load_lyric(lyric): #TODO kanskje
  if not lyric: return

def load_lyrics(directory):
  path = os.getcwd() + directory

  if not os.path.isdir(path): return {}

  file_names = [x for x in os.listdir(path) if os.path.isfile(path + x)]

  lyrics = {}
  for file_name in file_names:
    with open(path + file_name, 'r') as file:
      lyrics[file_name] = []

      for line in file:
        lyrics[file_name].append(line.strip())

  return lyrics
