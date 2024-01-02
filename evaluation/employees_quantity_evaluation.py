import pandas as pd

from evaluation.evaluation import Evaluation


class EmployeeQuantityEvaluation(Evaluation):
    def __init__(self, population):
        super().__init__()
        self.max_score = 16
        self.population = population
        self.score = 0
        self.invalid = False

    def evaluate(self):
        # Checks how many days each employee does support
        df = pd.DataFrame(self.population.on_call_schedule.values)
        count_df = df.apply(pd.Series.value_counts, axis=0).sum(axis=1).sort_values(ascending=False)
        if count_df.shape[0] == len(self.population.employees):
            self.score = self.max_score - max(0, count_df[0:1].values[0] - count_df[-1:].values[0] - 5)
        else:
            self.score = 0
        return self.score

    def get_score_to_str(self):
        return f"employee_of_week_score: {self.score:.2f}"
