import numpy as np
import pandas as pd

from evaluation.evaluation import Evaluation


class MoreThan7DaysEvaluation(Evaluation):
    def __init__(self, population):
        super().__init__()
        self.max_score = 25
        self.population = population
        self.score = 0
        self.invalid = False

    def evaluate(self):
        # Low score if employee do on-call support for more than 7 days.
        # It raises an invalid flag
        values = self.population.on_call_schedule.values
        df = pd.DataFrame(values)
        for i in range(8):
            zeros = [['0'] * values.shape[1]]
            values = np.concatenate([zeros, values])
            columns = [(i + 1) * values.shape[1] + c for c in range(values.shape[1])]

            df = pd.concat([df, pd.DataFrame(values, columns=columns)], axis=1)
        count_df = df.apply(pd.Series.value_counts, axis=1).drop(columns=['0'])
        count_df = count_df.drop(columns=[""], errors='ignore')
        count_df = count_df[(count_df >= 8)].dropna(axis=0, how='all')

        if count_df.shape[0] > 0:
            self.invalid = True
        self.score = self.max_score * (1 - (count_df.shape[0] / values.shape[0]))
        return self.score

    def get_score_to_str(self):
        return f"on_call_possible_score: {self.score:.2f}"
