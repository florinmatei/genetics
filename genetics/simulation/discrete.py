def pairwise(iterable):
    x = iter(iterable)
    return zip(x, x)


class DiscreteSimulation:
    def __init__(self, population_size, mutation_mask, crossover_mask,
            selection_function, elite_size,
            initial_generator, fitness_function=None):
        self.population_size = population_size
        self.mutation_mask = mutation_mask
        self.crossover_mask = crossover_mask
        self.selection_function = selection_function
        self.elite_size = elite_size
        self.initial_generator = initial_generator
        self.fitness_function = fitness_function

        self.parents_per_selection = population_size - elite_size

    def parents(self, scored_population):
        '''
        Given a scored population, yield pairs of parents
        '''
        selected = self.selection_function(scored_population,
                                           self.parents_per_selection)
        return pairwise(selected)

    def find_scores(self, population):
        if self.fitness_function is not None:
            for member in population:
                member.score = self.fitness_function(member)
        return population

    def initial_population(self):
        '''Create an initial populaton'''
        return list(self.initial_generator() for _ in
                    range(self.population_size))

    def step_generator(self, population):
        '''Run a whole genetic step on a scored population'''
        # Sort population and score if nessesary
        scored_population = sorted(self.find_scores(population), reverse=True)

        # Yield the elite elements
        yield from scored_population[:self.elite_size]
        # Generate parents
        for parent1, parent2 in self.parents(scored_population):
            # crossover parents
            mask = self.crossover_mask(parent1.total_length())
            for child in parent1.combine(parent2, mask):
                # mutate
                yield child.mutate(self.mutation_mask(child.total_length()))

    def step(self, population):
        return list(self.step_generator(population))
