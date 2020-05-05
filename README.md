# Master's Thesis (Masteroppgave)
An implementation of a system that takes an input lyric and generates a melody line with some harmony for the given lyric by using the NSGAII algorithm.

## Usage
Python version should be ``Python 3.6.9``, and the library [NLTK](https://www.nltk.org/) must be installed (e.g. by using [pip](https://pip.pypa.io/en/stable/installing/)). Some packages such as [VADER](https://github.com/cjhutto/vaderSentiment) and SonorityTokezier are bundled with NLTK, and must be installed through NLTK's installer.

An example of use is found in the ``main.py`` file. The `load_lyrics` function takes a directory name as input and loads all files from it. The `Lyric` class handles the lyric (syllabification, sentiment analysis etc.). The `GA` class handles the main NSGAII algorithm, which generates the music. It takes a population size and a lyric as input. The number of generations is specified directly in the main file. The `LilyPondFileGenerator` takes one `Phenotype` class instance from the GA population, GA musical key, GA time signature and the syllabified lyric as input, and generates a [LilyPond](http://lilypond.org/) file as output.
