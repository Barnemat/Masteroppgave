import os
from load_and_store import load_lyrics
from lyric import Lyric
from genetic_algorithm.GA import GA
from output.output import LilyPondFileGenerator

if __name__ == '__main__':
    texts = load_lyrics('/syllable_handling/testtekster/')
    # lyrics = [Lyric(texts[title]) for title in texts]
    lyric = Lyric(texts['nj-v12'])

    population_size = 500
    num_generations = 500

    ga = GA(population_size, lyric)

    for i in range(num_generations):
        print('iteration', i)
        ga.iterate()

    for phenotype in ga.population[:len(ga.population) // (len(ga.population) // 2)]:
        file_generator = LilyPondFileGenerator(phenotype.genes, ga.key, ga.time_signature, lyric.get_syllables())
        file_generator.generate_file(os.getcwd() + '/output/outfiles/mutation/')
