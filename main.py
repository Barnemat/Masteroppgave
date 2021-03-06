import os
from load_and_store import load_lyrics
from lyric import Lyric
from genetic_algorithm.GA import GA
from output.output import LilyPondFileGenerator
from random import randint, choice

if __name__ == '__main__':
    texts = load_lyrics('/lyrics/')
    lyric_title = 'nellie-dean'
    lyric = Lyric(texts[lyric_title], lyric_title)

    population_size = 1500
    num_generations = 1000

    ga = GA(population_size, lyric)
    print('key', ga.key)
    print('time signature', ga.time_signature)
    print('sentiment value', ga.sentiment)

    for i in range(num_generations):
        print('iteration', i)
        should_terminate = ga.iterate()

        if i % 100 == 0 or i == num_generations - 1 or should_terminate:
            for _ in range(5):
                phenotype = None

                if len(ga.tournament_winner_indices) > 50:
                    phenotype = ga.population[choice(ga.tournament_winner_indices)]
                else:
                    phenotype = ga.population[randint(0, len(ga.population) - 1)]

                file_generator = LilyPondFileGenerator(phenotype.genes, ga.key, ga.time_signature, lyric.get_syllables())
                file_generator.generate_file(os.getcwd() + '/output/outfiles/done/' + str(i) + '/')

        if should_terminate:
            break
