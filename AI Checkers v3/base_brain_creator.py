import numpy
import copy
import pickle
import predictor


def integer_to_real_mapper(integers):
    """Define Integer Mapping Function Here(If Needed.)"""

    real_numbers = []
    range_of_integers = 32767  # each value goes from 0-32767(2 ^ length_of_chromosome)
    integer_to_real_number_mapper = 1 / range_of_integers  # will produce number between 0-1 when multiplied by a value
    # in the range of 0 to 32767 (1/32767 * 32767 = 1) AND (1/32767 * 0 = 0)

    for integer in integers:
        real_numbers.append(integer * integer_to_real_number_mapper)

    return real_numbers


def f_function(chromosome):
    """Define Fitness Function Here."""
    x = chromosome.convert_to_integer()

    return (15 * x[0]) - (x[0] * x[0])

    # return (((15 * x[0]) - (x[0] * x[0])) * -1) + 1000 To Find Minimum Solution


def m_function(chromosome):
    """Define Mutation Function Here."""
    for i in range(384):
        mutated_gene = numpy.random.randint(0, chromosome.chromosome_size * chromosome.number_of_variables)

        if chromosome.chromosome[mutated_gene] == 1:
            chromosome.chromosome[mutated_gene] = 0
        else:
            chromosome.chromosome[mutated_gene] = 1

    chromosome.fitness = chromosome.fitness_function(chromosome)


def c_function(population, pair):
    """Define Crossover Function Here."""
    split_position = numpy.random.randint(1, (population.chromosome_size * population.variables))
    parent_one = copy.deepcopy(pair[0].get_chromosome())
    parent_two = copy.deepcopy(pair[1].get_chromosome())
    child_chromosomes = []

    for gene in range(split_position):
        child_chromosomes.append(parent_one[gene])

    for gene in range(split_position, (population.chromosome_size * population.variables)):
        child_chromosomes.append(parent_two[gene])

    child = Chromosome(population.chromosome_size, True, child_chromosomes,
                       population.variables, 0, 0, f_function, m_function)

    return child


class Chromosome:
    def convert_to_integer(self):
        """If chromosome represents binary number."""
        values = []
        current_value = 0
        current_position = 1
        exp = 1

        for i in reversed(self.chromosome):
            current_value += i * exp
            exp *= 2

            if current_position == self.chromosome_size:
                values.insert(0, current_value)
                current_value = 0
                current_position = 1
                exp = 1

            else:
                current_position += 1

        return values

    def __init__(self, length, chromosome_defined, chromosome, number_of_variables, lower_bound, upper_bound,
                 fitness_function, mutation_function):
        """Lower bound INCLUDING, Upper bound EXCLUDING. Number of variables refer to variables in chromosome that will
        be involved in calculating the chromosome's fitness"""
        self.chromosome = []
        self.number_of_variables = number_of_variables

        if chromosome_defined:
            self.chromosome = chromosome

        else:
            for i in range(length * number_of_variables):
                self.chromosome.append(numpy.random.randint(lower_bound, upper_bound))

        self.chromosome_size = length
        self.fitness_function = fitness_function
        self.fitness_ratio = 0
        self.mutation_function = mutation_function
        self.fitness = 50

    def set_fitness_ratio(self, fitness_ratio):
        self.fitness_ratio = fitness_ratio

    def get_fitness(self):
        return self.fitness

    def get_chromosome(self):
        return self.chromosome

    def print_binary_chromosome(self):
        print(self.chromosome, " Integer : ", self.convert_to_integer(), "Fitness : ", self.fitness, "Fitness Ratio : ",
              self.fitness_ratio)

    def print_real_chromosome(self):
        print("Real Numbers : ", [round(real_number, 2) for real_number in
                                  integer_to_real_mapper(self.convert_to_integer())],
              "Fitness : ", self.fitness, "Fitness Ratio : ",
              self.fitness_ratio)

    def is_twin(self, chromosome):
        if chromosome.get_chromosome() == self.chromosome:
            return True

    def mutate(self):
        self.mutation_function(self)

    def get_real_numbers(self):
        return integer_to_real_mapper(self.convert_to_integer())


class Population:
    def is_present(self, chromosome):
        for member in self.population:
            if member.is_twin(chromosome):
                return True

        return False

    def set_fitness_ratios(self):
        for member in self.population:
            fitness_ratio = (member.get_fitness() / self.total_fitness) * 100
            self.fitness_ratios.append(fitness_ratio)
            member.set_fitness_ratio(fitness_ratio)

    def __init__(self, population_size, chromosome_size, number_of_variables, crossover_probability, elites,
                 mutation_probability, lower_limit, upper_limit, fitness_function, mutation_function,
                 crossover_function):
        """Number of elites cannot exceed population size."""
        self.chromosome_size = chromosome_size
        self.variables = number_of_variables
        self.population_size = population_size
        self.crossover_probability = crossover_probability
        self.chromosome_size = chromosome_size
        self.mutation_probability = mutation_probability
        self.total_fitness = 0
        self.population = []
        self.fitness_ratios = []
        self.elitism_rate = elites
        self.lower_limit = lower_limit
        self.upper_limit = upper_limit
        self.fitness_function = fitness_function
        self.mutation_function = mutation_function
        self.crossover_function = crossover_function

        for i in range(population_size):

            chromosome = Chromosome(chromosome_size, False, None, number_of_variables, lower_limit, upper_limit,
                                    fitness_function, mutation_function)
            while self.is_present(chromosome):
                chromosome = Chromosome(chromosome_size, False, None, number_of_variables, lower_limit, upper_limit,
                                        fitness_function, mutation_function)

            self.total_fitness += chromosome.get_fitness()

            self.population.append(chromosome)

        self.set_fitness_ratios()
        self.average_fitness = self.total_fitness / population_size
        self.population.sort(key=lambda c: c.fitness_ratio, reverse=True)

    def print_population(self):
        for member in self.population:
            member.print_binary_chromosome()
        print("Average Fitness : ", self.average_fitness)
        print("")

    def print_population_real(self):
        for member in self.population:
            member.print_real_chromosome()
        print("Average Fitness : ", self.average_fitness)
        print("")

    @staticmethod
    def present_in_new_population(new_population, chromosome):
        for member in new_population:
            if member.is_twin(chromosome):
                return True

        return False

    def add_elites(self, new_population):
        no_of_elites = 0
        member_index = 0

        while member_index < len(self.population) and no_of_elites < self.elitism_rate:
            if self.present_in_new_population(new_population, self.population[member_index]):
                member_index += 1

            else:
                new_population.append(self.population[member_index])
                no_of_elites += 1
                member_index += 1

        if len(new_population) == 1:
            chromosome = Chromosome(self.chromosome_size, False, None, self.variables,
                                    self.lower_limit, self.upper_limit,
                                    self.fitness_function, self.mutation_function)

            while self.present_in_new_population(new_population, chromosome):
                chromosome = Chromosome(self.chromosome_size, False, None, self.variables,
                                        self.lower_limit, self.upper_limit,
                                        self.fitness_function, self.mutation_function)

            new_population.append(chromosome)
            no_of_elites += 1

        return no_of_elites

    def roulette_wheel(self, cdf):
        selector = numpy.random.uniform(0, 100)
        for index, i in enumerate(cdf):
            if selector <= i:
                return self.population[index]

    def create_chromosome_pair(self):
        chromosome_pair = []
        population_cdf = numpy.cumsum(self.fitness_ratios)
        first_chromosome = self.roulette_wheel(population_cdf)

        chromosome_pair.append(first_chromosome)
        mate = self.roulette_wheel(population_cdf)

        while mate.is_twin(chromosome_pair[0]):
            mate = self.roulette_wheel(population_cdf)

        chromosome_pair.append(mate)

        return chromosome_pair

    def recalculate_fitness(self):
        self.total_fitness = 0
        for member in self.population:
            self.total_fitness += member.get_fitness()

        self.set_fitness_ratios()
        self.average_fitness = self.total_fitness / self.population_size

    def save_chromosomes(self):
        with open("player.dat", "wb") as c:
            pickle.dump(self.population, c)

    def load_chromosomes(self):
        with open("player.dat", "rb") as c:
            self.population = pickle.load(c)

    def run_tournament(self, number_of_matches, generation_number):

        highest_number_won = 0

        for chromosome in range(len(self.population)):
            chromosome_brain = self.population[chromosome].get_real_numbers()
            number_matches_won = 0
            previous_opponents = [chromosome]

            for match in range(number_of_matches):
                opponent_chromosome = numpy.random.randint(len(self.population))
                while opponent_chromosome in previous_opponents:
                    opponent_chromosome = numpy.random.randint(len(self.population))

                previous_opponents.append(opponent_chromosome)
                opponent_brain = self.population[opponent_chromosome].get_real_numbers()

                selected_side = numpy.random.uniform(0, 1)
                print("***********************************************************************************************")
                print("Match Number : ", match, " Generation : ", generation_number, " Highest Wins : ",
                      highest_number_won)

                if selected_side <= 0.5:
                    fitness = predictor.start_match(chromosome_brain, opponent_brain, 1)

                else:
                    fitness = predictor.start_match(opponent_brain, chromosome_brain, 2)

                self.population[chromosome].fitness += fitness[1]

                if fitness[0]:
                    number_matches_won += 1

                print("Current Contender : ", chromosome, "Already Racked : ", number_matches_won, " wins")
                print("Current Contender : ", chromosome, "Fitness Level at : ", self.population[chromosome].fitness)
                print("***********************************************************************************************")

                if number_matches_won > highest_number_won:
                    highest_number_won = number_matches_won

        self.recalculate_fitness()
        self.population.sort(key=lambda c: c.fitness_ratio, reverse=True)

    def create_new_generation(self):
        new_population = []
        no_of_elites = self.add_elites(new_population)

        for next_member in range(no_of_elites, self.population_size):
            pair = self.create_chromosome_pair()

            will_crossover = numpy.random.uniform(0, 1)
            if will_crossover <= self.crossover_probability:
                child = self.crossover_function(self, pair)
                will_mutate = numpy.random.uniform(0, 1)

                if will_mutate <= self.mutation_probability:
                    child.mutate()

            else:
                child = pair[numpy.random.randint(0, 2)]

            while self.present_in_new_population(new_population, child):
                pair = self.create_chromosome_pair()
                will_crossover = numpy.random.uniform(0, 1)
                if will_crossover <= self.crossover_probability:
                    child = self.crossover_function(self, pair)
                    will_mutate = numpy.random.uniform(0, 1)

                    if will_mutate <= self.mutation_probability:
                        child.mutate()

                else:
                    child = pair[numpy.random.randint(0, 2)]

            new_population.append(child)

        self.population = new_population
        for chromosome in self.population:
            chromosome.fitness = 50

        self.recalculate_fitness()


def save_base_brain(base_brain):
    with open("bBrain.dat", "wb") as c:
        pickle.dump(base_brain, c)


def train_until_set_fitness(print_each_generation, save_to_file):
    global p_args

    city = Population(*p_args)

    city.run_tournament(20, 1)
    print("INITIAL POPULATION")
    city.print_population_real()

    global fitness_max
    highest = city.average_fitness
    generation_number = 2
    while city.average_fitness <= fitness_max:
        city.create_new_generation()
        city.run_tournament(20, generation_number)
        if print_each_generation:
            print("GENERATION NUMBER : ", generation_number)
            print("Highest Fitness : ", highest)
            city.print_population_real()

        generation_number += 1
        if city.average_fitness > highest:
            highest = city.average_fitness

    print("FINAL POPULATION")
    city.print_population_real()
    if save_to_file:
        base_brain = predictor.get_brain(city.population[0].get_real_numbers())
        save_base_brain(base_brain)


def train_for_set_number_generations(print_each_generation, save_to_file):
    global p_args

    city = Population(*p_args)

    city.run_tournament(20, 1)
    print("INITIAL POPULATION")
    city.print_population_real()

    global number_of_generations
    for generation_number in range(2, number_of_generations+1):
        city.create_new_generation()
        city.run_tournament(20, generation_number)
        if print_each_generation:
            print("GENERATION NUMBER : ", generation_number)
            city.print_population_real()

    print("FINAL POPULATION")
    city.print_population_real()
    if save_to_file:
        base_brain = predictor.get_brain(city.population[0].get_real_numbers())
        save_base_brain(base_brain)

size_of_population = 50
number_of_variables_in_chromosome = 128
probability_to_crossover = 0.7
probability_to_mutate = 0.05
number_of_elites = 4
length_of_chromosome = 15
upper_random_number_limit = 2
lower_random_number_limit = 0
number_of_generations = 20
fitness_max = 1800

p_args = [size_of_population, length_of_chromosome, number_of_variables_in_chromosome,
          probability_to_crossover, number_of_elites, probability_to_mutate,
          lower_random_number_limit, upper_random_number_limit,
          f_function, m_function, c_function]


