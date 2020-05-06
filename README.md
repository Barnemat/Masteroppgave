# Master's Thesis (Masteroppgave)
An implementation of a system that takes an input lyric and generates a melody line with some harmony for the given lyric by using the NSGAII algorithm.

## Usage
Python version should be ``Python 3.6.9``, and the library [NLTK](https://www.nltk.org/) must be installed (e.g. by using [pip](https://pip.pypa.io/en/stable/installing/)). Some packages such as [VADER](https://github.com/cjhutto/vaderSentiment) and SonorityTokezier are bundled with NLTK, and must be installed through NLTK's installer.

An example of use is found in the ``main.py`` file. The `load_lyrics` function takes a directory name as input and loads all files from it. The `Lyric` class handles the lyric (syllabification, sentiment analysis etc.). The `GA` class handles the main NSGAII algorithm, which generates the music. It takes a population size and a lyric as input. The number of generations is specified directly in the main file. The `LilyPondFileGenerator` takes one `Phenotype` class instance from the GA population, GA musical key, GA time signature and the syllabified lyric as input, and generates a [LilyPond](http://lilypond.org/) file as output.

The first line in the lyrics are removed, as this is used for source specification in the example code. This can be manually edited by switching from `self.lyric = lyric[1:]` to `self.lyric = lyric` in the `Lyric` class.

## Run-time (time complexity)
Run-time for each generation is heavily dependent on the population size and the size of the first verse of the lyrics. Verse separation is a line break.

My computer runs for 4-6 hours when generating a melody based on the current input parameters specified in the `main.py` file.

## Examples
Five video examples of generated melodies have been made as part of a questionnaire. Each video contains the generated MIDI-melody, as well as the corresponding sheet music.

[Nellie Dean](https://www.youtube.com/watch?v=VOas8VHKUik)
[Henry Martyn](https://www.youtube.com/watch?v=JfhC4a2zvAo)
[Early one morning](https://www.youtube.com/watch?v=VEknI_B2byI)
[Bridget O'Malley](https://www.youtube.com/watch?v=P2HoOBl4toc)
[Billy Lyons and Stack O'Lee](https://www.youtube.com/watch?v=P1EQ4mrtVB4)
