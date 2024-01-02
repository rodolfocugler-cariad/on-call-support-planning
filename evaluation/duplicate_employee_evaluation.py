from evaluation.evaluation import Evaluation


class DuplicateEmployeeEvaluation(Evaluation):
    def __init__(self, population):
        super().__init__()
        self.max_score = 17
        self.population = population
        self.score = 0
        self.invalid = False

    def evaluate(self):
        # Returns a low score if the same employee appears twice on the same day
        # it means, if the support is done in pairs, the same person cannot do
        # on-call support twice on the same day.
        # It raises an invalid flag
        score = 0
        for week_start in range(0, len(self.population.on_call_schedule), 7):
            week = self.population.on_call_schedule[week_start:week_start + 7]
            score += week[week[0] != week[1]].shape[0]

        score *= self.max_score / len(self.population.on_call_schedule)
        self.score = score

        if score != self.max_score:
            self.invalid = True
        return self.score

    def get_score_to_str(self):
        return f"duplicate_employee_score: {self.score:.2f}"
