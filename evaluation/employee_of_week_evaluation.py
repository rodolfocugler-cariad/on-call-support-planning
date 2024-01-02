from evaluation.evaluation import Evaluation


class EmployeeOfWeekEvaluation(Evaluation):
    def __init__(self, population):
        super().__init__()
        self.max_score = 17
        self.population = population
        self.score = 0
        self.invalid = False

    def evaluate(self):
        # Returns a low score if there are multiple employees doing support in
        # just one week. It tries to add the same employee in the whole week
        score = 0
        for week_start in range(0, len(self.population.on_call_schedule), 7):
            week = self.population.on_call_schedule[week_start:week_start + 7]
            for support_order in range(week.shape[1]):
                support = week[support_order].value_counts().sort_values(ascending=False)
                score += support.values[0]
        score *= self.max_score / (len(self.population.on_call_schedule) * self.population.on_call_schedule.shape[1])
        self.score = score
        return self.score

    def get_score_to_str(self):
        return f"score_more_than_7_days: {self.score:.2f}"
