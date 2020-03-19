import os
from load_and_store import load_lyrics
from lyric import Lyric
from genetic_algorithm.GA import GA
from output.output import LilyPondFileGenerator

if __name__ == '__main__':
    texts = load_lyrics('/syllable_handling/testtekster/')
    # lyrics = [Lyric(texts[title]) for title in texts]
    lyric = Lyric(texts['john-lennon-mother-1v'])

    ga = GA(1, lyric)

    # print(ga.population[0].genes)
    file_generator = LilyPondFileGenerator(ga.population[0].genes, ga.key, ga.time_signature, lyric.get_syllables())
    file_generator.generate_file(os.getcwd() + '/output/outfiles/')
