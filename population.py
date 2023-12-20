import os
import random
from datetime import timedelta, datetime

import numpy as np
import pandas as pd

SCORE_CONFIG = {
    "evaluate_more_than_7_days": 25,
    "evaluate_employee_of_week": 17,
    "evaluate_duplicate_employee": 17,
    "evaluate_on_call_possible": 25,
    "evaluate_employees_quantity": 16
}


def _sort_employees(employees: list):
    ordered_employees = []
    for index in random.sample(range(len(employees)), len(employees)):
        ordered_employees.append(employees[index])
    return ordered_employees


def _select_next_employee(sorted_employees: list, employees: list, employees_of_week: list):
    if not sorted_employees:
        sorted_employees = _sort_employees(employees)

    employee = sorted_employees.pop()
    employee_aux = []
    while employee in employees_of_week:
        employee_aux.append(employee)
        if not sorted_employees:
            sorted_employees = _sort_employees(employees)
        employee = sorted_employees.pop()
    for e in employee_aux:
        sorted_employees.append(e)
    return employee, sorted_employees


class Population:
    def __init__(self, on_call_schedule: list, on_call_not_possible: dict, employees: list):
        self.on_call_schedule = pd.DataFrame(on_call_schedule)
        self.employees = employees
        self.score = None
        self.invalid = False
        self.duplicate_employee_score = None
        self.score_more_than_7_days = None
        self.employee_of_week_score = None
        self.employees_quantity_score = None
        self.on_call_possible_score = None
        self.on_call_not_possible = on_call_not_possible

    def evaluate(self):
        self.score = None
        self.invalid = False
        self.duplicate_employee_score = None
        self.score_more_than_7_days = None
        self.employee_of_week_score = None
        self.employees_quantity_score = None
        score = self._evaluate_duplicate_employee()
        score += self._evaluate_employee_of_week()
        score += self._evaluate_more_than_7_days()
        score += self._evaluate_on_call_possible()
        score += self._evaluate_employees_quantity()
        self.score = score

    def get_score_to_str(self):
        return f"duplicate_employee_score: {self.duplicate_employee_score:.2f}, score_more_than_7_days: {self.score_more_than_7_days:.2f}, employee_of_week_score: {self.employee_of_week_score:.2f}, on_call_possible_score: {self.on_call_possible_score:.2f}, employees_quantity_score: {self.employees_quantity_score:.2f}"

    def _evaluate_employees_quantity(self):
        # Checks how many days each employee does support
        max_score = SCORE_CONFIG["evaluate_employees_quantity"]
        df = pd.DataFrame(self.on_call_schedule.values)
        count_df = df.apply(pd.Series.value_counts, axis=0).sum(axis=1).sort_values(ascending=False)
        if count_df.shape[0] == len(self.employees):
            self.employees_quantity_score = max_score - max(0, count_df[0:1].values[0] - count_df[-1:].values[0] - 5)
        else:
            self.employees_quantity_score = 0
        return self.employees_quantity_score

    def _evaluate_on_call_possible(self):
        # Checks if the employees are available to do on-call on
        # the days which was attributed to her/him.
        # It raises an invalid flag
        max_score = SCORE_CONFIG["evaluate_on_call_possible"]
        df = pd.DataFrame(self.on_call_schedule.values)
        df = pd.concat([df, pd.DataFrame(self.on_call_not_possible)], axis=1)
        count_df = df.apply(pd.Series.value_counts, axis=1).drop(columns=[""])
        count_df = count_df[(count_df >= 2)].dropna(axis=0, how="all")

        if count_df.shape[0] > 0:
            self.invalid = True

        self.on_call_possible_score = (df.shape[0] - count_df.shape[0]) * (max_score / df.shape[0])
        return self.on_call_possible_score

    def _evaluate_more_than_7_days(self):
        # Low score if employee do on-call support for more than 7 days.
        # It raises an invalid flag
        max_score = SCORE_CONFIG["evaluate_more_than_7_days"]
        values = self.on_call_schedule.values
        df = pd.DataFrame(values)
        for i in range(8):
            zeros = [['0'] * values.shape[1]]
            values = np.concatenate([zeros, values])
            columns = [(i + 1) * values.shape[1] + c for c in range(values.shape[1])]

            df = pd.concat([df, pd.DataFrame(values, columns=columns)], axis=1)
        count_df = df.apply(pd.Series.value_counts, axis=1).drop(columns=['0'])
        count_df = count_df[(count_df >= 8)].dropna(axis=0, how='all')

        if count_df.shape[0] > 0:
            self.invalid = True
        self.score_more_than_7_days = max_score * (1 - (count_df.shape[0] / values.shape[0]))
        return self.score_more_than_7_days

    def _evaluate_employee_of_week(self):
        # Returns a low score if there are multiple employees doing support in
        # just one week. It tries to add the same employee in the whole week
        max_score = SCORE_CONFIG["evaluate_employee_of_week"]
        score = 0
        for week_start in range(0, len(self.on_call_schedule), 7):
            week = self.on_call_schedule[week_start:week_start + 7]
            for support_order in range(week.shape[1]):
                support = week[support_order].value_counts().sort_values(ascending=False)
                score += support.values[0]
        score *= max_score / (len(self.on_call_schedule) * self.on_call_schedule.shape[1])
        self.employee_of_week_score = score
        return self.employee_of_week_score

    def _evaluate_duplicate_employee(self):
        # Returns a low score if the same employee appears twice on the same day
        # it means, if the support is done in pairs, the same person cannot do
        # on-call support twice on the same day.
        # It raises an invalid flag
        max_score = SCORE_CONFIG["evaluate_duplicate_employee"]
        score = 0
        for week_start in range(0, len(self.on_call_schedule), 7):
            week = self.on_call_schedule[week_start:week_start + 7]
            score += week[week[0] != week[1]].shape[0]

        score *= max_score / len(self.on_call_schedule)
        self.duplicate_employee_score = score

        if score != max_score:
            self.invalid = True
        return self.duplicate_employee_score

    def save(self, start_date):
        dates = [(start_date + timedelta(days=i)).strftime("%d/%m/%Y") for i in range(self.on_call_schedule.shape[0])]
        day_of_week = [datetime.strptime(i, "%d/%m/%Y").date().strftime('%A') for i in dates]

        self.on_call_schedule["Date"] = dates
        self.on_call_schedule["Day Of Week"] = day_of_week
        self.on_call_schedule.rename(inplace=True, columns={0: "On-Call 1", 1: "On-Call 2"})
        self.on_call_schedule[["Date", "Day Of Week", "On-Call 1", "On-Call 2"]].to_csv("./resources/result.csv",
                                                                                        index=False)

    @staticmethod
    def create_population(employees: list, number_of_employees_doing_on_call: int, on_call_not_possible: dict,
                          possibilities: list):
        # Creates the on-call support schedule
        schedule = []
        sorted_employees = _sort_employees(employees)
        for p in possibilities:
            employees_of_week = []
            for employee_index in range(number_of_employees_doing_on_call):
                employee, sorted_employees = _select_next_employee(sorted_employees, employees,
                                                                   p["excludedEmployees"] + employees_of_week)
                employees_of_week.append(employee)
            for day in range(p["days"]):
                schedule.append(employees_of_week)
        return Population(on_call_schedule=schedule, on_call_not_possible=on_call_not_possible, employees=employees)

    @staticmethod
    def create_possibilities(number_of_employees_doing_on_call: int, employees: list, week_quantity: int,
                             on_call_not_possible: dict):
        # Creates a list of employees unavailable to do on-call support
        # The list contains 2 fields:
        # excludedEmployees: a list of employees whom cannot do on-call on the next days
        # days: the amount of days, i.e. 3
        should_split_week = len(employees) - number_of_employees_doing_on_call == 1
        df_on_call_not_possible = pd.DataFrame(on_call_not_possible)
        possibilities = []
        for week in range(week_quantity):
            sum_days = 0
            while sum_days < 7:

                # If the variable days is high (i.e. 7), on-call schedule is more stable
                # it means the same person will do support in the whole week,
                # but it becomes more difficult to find a schedule
                days = int(os.getenv("DAYS", "3")) if not should_split_week else 2
                columns = None
                count = 0
                while columns is None or (
                        days - count > 0 and len(columns) + number_of_employees_doing_on_call > len(employees)):
                    df = df_on_call_not_possible[(week * 7) + sum_days:(week * 7) + sum_days + days - count]
                    columns = df.apply(pd.Series.value_counts, axis=1).drop(columns=[""]).columns.values
                    count += 1
                sum_days += days - count + 1
                possibilities.append({
                    "excludedEmployees": list(columns),
                    "days": days - count + 1
                })
        return possibilities
