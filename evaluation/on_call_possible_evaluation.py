import pandas as pd

from evaluation.evaluation import Evaluation


class OnCallPossibleEvaluation(Evaluation):
    def __init__(self, population):
        super().__init__()
        self.max_score = 25
        self.population = population
        self.score = 0
        self.invalid = False

    def evaluate(self):
        # Checks if the employees are available to do on-call on
        # the days which was attributed to her/him.
        # It raises an invalid flag
        df = pd.DataFrame(self.population.on_call_schedule.values)
        df = pd.concat([df, pd.DataFrame(self.population.on_call_not_possible)], axis=1)
        count_df = df.apply(pd.Series.value_counts, axis=1).drop(columns=[""])
        count_df = count_df[(count_df >= 2)].dropna(axis=0, how="all")

        if count_df.shape[0] > 0:
            self.invalid = True

        self.score = (df.shape[0] - count_df.shape[0]) * (self.max_score / df.shape[0])
        return self.score

    def get_score_to_str(self):
        return f"employees_quantity_score: {self.score:.2f}"
