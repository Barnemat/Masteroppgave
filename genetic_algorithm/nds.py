from math import factorial, inf
from random import randint

from genetic_algorithm.crossover import apply_crossover
from genetic_algorithm.mutation import apply_mutation


class NonDominatedSorter:
    '''
        Class for sorting the population by objective fitness scores
        Sorts by using a non-dominated sorting approach
    '''

    def __init__(self, population, objectives, pop_size):
        self.population = population
        self.objectives = objectives
        self.pop_size = pop_size

        self.fronts = []
        self.population_values = []
        self.set_population_values()

        # [0, []], where 0 is the dominated_by_counter and [] is the dominates_list
        self.domination_list = [[0, []] for phoneme in population]
        self.tournament_winner_indices = []

    def set_population_values(self):
        for phenotype in self.population:

            values = []
            for objective in self.objectives:
                values.append(objective.get_total_fitness_value(phenotype))

            self.population_values.append(values)

    def set_fronts(self):
        values = self.population_values
        len_values = len(values)

        for index in range(len_values):
            for check_index in range(len_values):

                check = [False for x in range(len(values[index]))]
                one_is_higher = False
                for value_index in range(len(values[index])):
                    if values[index][value_index] >= values[check_index][value_index]:
                        check[value_index] = True

                    if values[index][value_index] > values[check_index][value_index]:
                        one_is_higher = True

                if False not in check and one_is_higher:
                    self.domination_list[index][1].append(check_index)
                    self.domination_list[check_index][0] += 1

        # print(self.population_values)
        # print(self.domination_list)

        while get_fronts_length(self.fronts) < len(self.population_values):
            d_list = self.domination_list

            front = []
            for index in range(len(d_list)):
                if not self.index_is_in_front(index) and d_list[index][0] == 0:
                    front.append(index)

            self.fronts.append(front)

            for index in front:
                for dominated in d_list[index][1]:
                    d_list[dominated][0] -= 1

    def get_new_population(self):
        self.set_fronts()

        '''
        In case of NSGAIII
        p = 4  # num ref points for each objective plane
        get_reference_points(p, len(self.objectives))
        '''

        new_population = []
        new_fronts = []
        last_front = []
        distances = []

        for front in self.fronts:
            distances.append(self.get_crowding_distance(front))

            if len(new_population) + len(front) > self.pop_size:
                last_front.extend(front)
                break
            else:
                new_population.extend(front)
                new_fronts.append(front)

        distance_fix = []
        new_last_front = []
        while len(new_population) < self.pop_size:
            max_distance = max(distances[-1])
            add_index = distances[-1].index(max_distance)

            new_population.append(last_front[add_index])
            new_last_front.append(last_front[add_index])

            distance_fix.append([add_index, distances[-1][add_index]])
            distances[-1][add_index] = -inf

        if len(new_last_front) > 0:
            new_fronts.append(new_last_front)

        for distance in distance_fix:  # Sets distances to previous distances
            distances[-1][distance[0]] = distance[1]

        new_population = [self.population[x] for x in new_population]

        # Tournament selection for crossover
        for _ in range(len(new_population)):
            crossover = []

            for _ in range(2):
                try:
                    front_1 = randint(0, len(new_fronts) - 1)
                    front_2 = randint(0, len(new_fronts) - 1)
                except ValueError:
                    front_1, front_2 = 0, 0

                if front_1 == front_2:
                    try:
                        index_1 = randint(0, len(new_fronts[front_1]) - 1)
                        index_2 = randint(0, len(new_fronts[front_1]) - 1)
                    except ValueError:
                        index_1, index_2 = 0, 0

                    if distances[front_1][index_1] > distances[front_1][index_2]:
                        crossover.append(new_fronts[front_1][index_1])
                    else:
                        crossover.append(new_fronts[front_1][index_2])
                else:
                    index = min([front_1, front_2])
                    crossover.append(new_fronts[index][randint(0, len(new_fronts[index]) - 1)])

            offspring = apply_crossover(self.population[crossover[0]], self.population[crossover[1]])

            # Mutation and mutation probabilitiy
            if randint(0, 100) <= 30:  # Chance of offspring mutating
                apply_mutation(offspring, True)

            new_population.append(offspring)

            # Adds indices from crossover (tournament selection winners) to tournament_winner_indices
            self.tournament_winner_indices = []
            for index in crossover:
                if index not in self.tournament_winner_indices:
                    self.tournament_winner_indices.append(index)

        self.population = new_population
        return self.population, len(new_fronts)

    def get_crowding_distance(self, front):
        distances = [0 for x in range(len(front))]
        pop_values = self.population_values

        for o_index in range(len(self.objectives)):
            sorted_front = sorted(front, key=lambda x: pop_values[x][o_index])
            sorted_dist_indices = [front.index(x) for x in sorted_front]

            distances[sorted_dist_indices[0]] = inf
            distances[sorted_dist_indices[-1]] = inf

            for index in range(1, len(sorted_front) - 1):
                if (pop_values[sorted_front[-1]][o_index] - pop_values[sorted_front[0]][o_index]) == 0:
                    continue
                distances[sorted_dist_indices[index]] = (
                    distances[sorted_dist_indices[index]]
                    + ((pop_values[sorted_front[index + 1]][o_index] - pop_values[sorted_front[index - 1]][o_index])
                        / (pop_values[sorted_front[-1]][o_index] - pop_values[sorted_front[0]][o_index]))
                )
        return distances

    def index_is_in_front(self, index):
        for front in self.fronts:
            if index in front:
                return True
        return False


'''
Needed only if upgrade from NSGAII to NSGAIII
def get_reference_points(p, num_objectives):
    points = []
    num_points = combs(num_objectives + p - 1, p)
    decrement = 1 / p
    print(points)
    '''


def get_fronts_length(fronts):
    length = 0

    for front in fronts:
        length += len(front)

    return length


def combs(n, k):
    try:
        return factorial(n) // factorial(k) // factorial(n - k)
    except ValueError:
        return 0
