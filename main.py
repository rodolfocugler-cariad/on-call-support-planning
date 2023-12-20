import json
import logging
import os
from datetime import datetime, timedelta

from generation import Generation


def map_on_call_not_possible(config: dict):
    start_date = datetime.strptime(config["startDate"], "%d/%m/%Y").date()
    week_quantity = config["weekQuantity"]
    employee_names = [e.lower() for e in config["employeeNames"]]

    obj = {}
    for employee_name in employee_names:
        obj[employee_name] = []
    for days in range(7 * week_quantity):
        for employee_name in employee_names:
            employee_name = employee_name.lower()
            names = config[(start_date + timedelta(days=days)).strftime("%d/%m/%Y")].lower()
            obj[employee_name].append(employee_name if employee_name in names else "")
    return obj


def run_algorithm():
    with open("./resources/template.json", "r") as f:
        config = json.load(f)

    week_quantity = config["weekQuantity"]
    number_of_populations = config["numberOfPopulations"]
    number_of_epochs = config["numberOfEpochs"]
    number_of_employees_doing_on_call = config["numberOfEmployeesDoingOnCall"]
    employee_names = [e.lower() for e in config["employeeNames"]]
    on_call_not_possible = map_on_call_not_possible(config)

    generation = Generation.create_generation(number_of_populations, number_of_employees_doing_on_call, employee_names,
                                              week_quantity, on_call_not_possible)
    best_population = None
    while generation.epoch < number_of_epochs and (best_population is None or best_population.score < 100):
        new_best_population = generation.get_best_population()
        if ((best_population is None or best_population.score < new_best_population.score)
                and not new_best_population.invalid):
            best_population = new_best_population

        invalid_str = " (invalid schedule)" if new_best_population.invalid else " (valid schedule)"
        logging.info(f"epoch: {generation.epoch} - score: {new_best_population.score:.2f} {invalid_str}")
        logging.debug(new_best_population.get_score_to_str())
        generation.next_generation()

    if best_population is not None:
        logging.debug(best_population.on_call_schedule)
        logging.info(f"Best score: {best_population.score:.2f}")
        logging.info("Result was saved on ./resources/result.csv")
        best_population.save(datetime.strptime(config["startDate"], "%d/%m/%Y").date())
    else:
        logging.info("No valid result was found - run again")


def create_template():
    date_str = input("Enter the date (dd/MM/YYYY) to start calculating the on-call support:\n").strip()
    date = datetime.strptime(date_str, "%d/%m/%Y").date()

    week_quantity = int(input("Enter the quantity of weeks to be calculated:\n").strip())
    config = {
        "weekQuantity": week_quantity,
        "numberOfPopulations": 40,
        "numberOfEpochs": 300,
        "numberOfEmployeesDoingOnCall": 2,
        "employeeNames": ["A", "B", "C"],
        "startDate": date.strftime("%d/%m/%Y")
    }
    for days in range(7 * week_quantity):
        config[(date + timedelta(days=days)).strftime("%d/%m/%Y")] = ""

    with open("./resources/template.json", "w") as f:
        f.write(json.dumps(config, indent=2, sort_keys=False))

    logging.info("template saved on ./resources/template.json")


def configure_logging():
    logger = logging.getLogger()
    if os.getenv("VERBOSE", "false").lower() != "false":
        logger.setLevel(logging.DEBUG)
    else:
        logger.setLevel(logging.INFO)

    stdout_handler = logging.StreamHandler()
    formatter = logging.Formatter(fmt='%(asctime)s %(pathname)s:%(lineno)d - %(levelname)s - %(message)s',
                                  datefmt='%d-%b-%y %H:%M:%S')
    stdout_handler.setFormatter(formatter)
    logger.addHandler(stdout_handler)


if __name__ == "__main__":
    configure_logging()
    options = int(input("Enter: \n1 - Create template for input data\n2 - Run algorithm\n").strip())

    if options == 1:
        create_template()
    elif options == 2:
        run_algorithm()
