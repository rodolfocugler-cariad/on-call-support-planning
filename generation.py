import random

from population import Population


class Generation:
    def __init__(self, populations: list, number_of_populations: int, number_of_employees_doing_on_call: int,
                 employees: list, week_quantity: int, on_call_not_possible: dict, possibilities: list, epoch=0):
        self.populations = populations
        self.on_call_not_possible = on_call_not_possible
        self.epoch = epoch
        self.number_of_populations = number_of_populations
        self.number_of_employees_doing_on_call = number_of_employees_doing_on_call
        self.employees = employees
        self.week_quantity = week_quantity
        self.possibilities = possibilities
        self.best_population = None

    def get_best_population(self):
        for population in self.populations:
            population.evaluate()
        self._sort_populations()
        self.populations = sorted(self.populations, key=lambda p: (0 if p.invalid else 1, p.score))
        self.populations.reverse()
        return self.populations[0]

    def _sort_populations(self):
        self.populations = sorted(self.populations, key=lambda p: (0 if p.invalid else 1, p.score))
        self.populations.reverse()

    def next_generation(self):
        populations = []
        self.epoch += 1
        if self.best_population is None or self.best_population.score < self.populations[0].score:
            self.best_population = self.populations[0]
        else:
            self.populations = [self.best_population] + self.populations
        max_index = len(self.populations) if len(self.populations) % 2 == 0 else len(self.populations) - 1
        for index in range(0, max_index, 2):
            population_0 = self.populations[index].on_call_schedule.values
            population_1 = self.populations[index + 1].on_call_schedule.values
            new_population = []

            for week in range(self.week_quantity):
                alpha = 7 if self.epoch < 30 else random.randrange(1, 7)
                for day in range(week * 7, (week * 7) + alpha):
                    schedule = population_0[day] if week % 2 == 0 else population_1[day]
                    new_population.append(schedule)
                for day in range((week * 7) + alpha, (week + 1) * 7):
                    schedule = population_0[day] if week % 2 != 0 else population_1[day]
                    new_population.append(schedule)

            populations.append(Population(new_population, self.on_call_not_possible, employees=self.employees))

        populations = [
            Population.create_population(self.employees, self.number_of_employees_doing_on_call,
                                         self.on_call_not_possible,
                                         self.possibilities) for i in range(int(self.number_of_populations / 2))]
        self.populations = populations

    @staticmethod
    def create_generation(number_of_populations: int, number_of_employees_doing_on_call: int, employees: list,
                          week_quantity: int, on_call_not_possible: dict):
        possibilities = Population.create_possibilities(number_of_employees_doing_on_call, employees, week_quantity,
                                                        on_call_not_possible)
        populations = [Population.create_population(employees, number_of_employees_doing_on_call, on_call_not_possible,
                                                    possibilities) for i in range(number_of_populations)]
        return Generation(populations, number_of_populations, number_of_employees_doing_on_call, employees,
                          week_quantity, on_call_not_possible, possibilities)
