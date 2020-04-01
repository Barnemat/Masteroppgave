

class NonDominatedSorter:
    '''
        Class for sorting the population by objective fitness scores
        Sorts by using a non-dominated sorting approach
    '''

    def __init__(self, population, objectives):
        self.population = population
        self.objectives = objectives

        self.fronts = []
        self.population_values = []
        self.set_population_values()

        # [0, []], where 0 is the dominated_by_counter and [] is the dominates_list
        self.domination_list = [[0, []] for phoneme in population]

    def set_population_values(self):
        for phenotype in self.population:

            values = []
            for objective in self.objectives:
                values.append(objective.get_total_fitness_value(phenotype))

            self.population_values.append(values)

    def sort(self):
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

        for front_index in range(len(self.fronts)):
            print('Front: ', front_index + 1)
            print(self.fronts[front_index])
            print('')

    def index_is_in_front(self, index):
        for front in self.fronts:
            if index in front:
                return True
        return False


def get_fronts_length(fronts):
    length = 0

    for front in fronts:
        length += len(front)

    return length
