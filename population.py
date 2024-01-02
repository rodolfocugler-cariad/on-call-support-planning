import os
import random
from datetime import timedelta, datetime

import pandas as pd

from evaluation.duplicate_employee_evaluation import DuplicateEmployeeEvaluation
from evaluation.employee_of_week_evaluation import EmployeeOfWeekEvaluation
from evaluation.employees_quantity_evaluation import EmployeeQuantityEvaluation
from evaluation.more_than_7_days_evaluation import MoreThan7DaysEvaluation
from evaluation.on_call_possible_evaluation import OnCallPossibleEvaluation


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
        self.on_call_not_possible = on_call_not_possible
        self.evaluation = None

    def evaluate(self):
        self.evaluation = [DuplicateEmployeeEvaluation(self), EmployeeOfWeekEvaluation(self),
                           EmployeeQuantityEvaluation(self), MoreThan7DaysEvaluation(self),
                           OnCallPossibleEvaluation(self)]
        self.score = sum([e.evaluate() for e in self.evaluation])
        self.invalid = any([e.invalid for e in self.evaluation])

    def get_score_to_str(self):
        return ', '.join(e.get_score_to_str() for e in self.evaluation)

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
