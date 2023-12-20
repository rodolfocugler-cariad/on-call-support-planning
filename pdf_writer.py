import json
import logging
import os
import typing as T
from datetime import datetime

import numpy as np
import pandas as pd
import pypdf
import pypdf.constants
import pypdf.generic


def _fix_acroform(writer: pypdf.PdfWriter, reader: pypdf.PdfReader) -> None:
    reader_root = T.cast(pypdf.generic.DictionaryObject, reader.trailer[pypdf.constants.TrailerKeys.ROOT])
    acro_form_key = pypdf.generic.NameObject(pypdf.constants.CatalogDictionary.ACRO_FORM)

    if pypdf.constants.CatalogDictionary.ACRO_FORM in reader_root:
        reader_acro_form = reader_root[pypdf.constants.CatalogDictionary.ACRO_FORM]
        writer._root_object[acro_form_key] = writer._add_object(reader_acro_form.clone(writer))
    else:
        writer._root_object[acro_form_key] = writer._add_object(pypdf.generic.DictionaryObject())

    writer.set_need_appearances_writer()


def read_schedule(schedule_name):
    df = pd.read_csv("./resources/result.csv")
    df = df[(df["On-Call 1"] == schedule_name) | (df["On-Call 2"] == schedule_name)]
    df["Week"] = df["Date"].apply(lambda d: datetime.strptime(d, "%d/%m/%Y").date().isocalendar().week)
    return df


def write_header(config, writer):
    writer.update_page_form_field_values(writer.pages[0], fields={
        "Name": config["Name"],
        "Vorname": config["Vorname"],
        "OE": config["OE"],
        "Kostenstelle": config["Kostenstelle"],
        "Personalnummer": config["Personalnummer"],
        "Telefonnummer": config["Telefonnummer"],
        "Begründung in Kurzform": config["Begrundung"]
    })


def write_page(weeks, schedule, writer):
    fields = {}
    for wk_index in range(len(weeks)):
        fields[f"KWRow{wk_index + 1}"] = weeks[wk_index]

        df = schedule[schedule["Week"] == weeks[wk_index]]
        for index, row in df.iterrows():
            date = datetime.strptime(row["Date"], "%d/%m/%Y").date()
            date_index = (wk_index * 7) + date.weekday() + 1
            fields[f"Datum{date_index}"] = date.strftime("%m/%d/%Y")

            name = f"AnmerkungRow{date_index}" if date_index <= 14 else f"AnmerkungRow{date.weekday() + 1}_{wk_index + 1}"
            fields[name] = ""

    for page in writer.pages:
        writer.update_page_form_field_values(page, fields=fields)


def write_pdf():
    with open("./resources/personal-data.json", "r") as f:
        config = json.load(f)

    schedule = read_schedule(config["scheduleName"].lower())
    reader = pypdf.PdfReader("./public/pdf-template.pdf")

    writer = pypdf.PdfWriter()
    _fix_acroform(writer, reader)

    writer.append_pages_from_reader(reader)
    write_header(config, writer)

    weeks = np.sort(schedule["Week"].unique()).tolist()
    write_page(weeks, schedule, writer)

    date = datetime.strptime(schedule["Date"][0], "%d/%m/%Y").date()

    filename = f"{date.strftime('%b')}_{date.strftime('%Y')}_{config['Name'].replace(' ', '_')}_{config['Vorname'].replace(' ', '_')}"
    with open(f"./resources/{filename}.pdf", "wb") as output_stream:
        writer.write(output_stream)


def create_template():
    name = input("Enter your name: ").strip()
    vorname = input("Enter your Vorname: ").strip()
    oe = input("Enter your OE: ").strip()
    kostenstelle = input("Enter your Kostenstelle: ").strip()
    personalnummer = input("Enter your Personalnummer: ").strip()
    telefonnummer = input("Enter your Telefonnummer: ").strip()
    begrundung = input("Enter the Begründung in Kurzform: ").strip()
    scheduleName = input("Enter the name used in the schedule csv file: ").strip()

    config = {
        "Name": name,
        "Vorname": vorname,
        "OE": oe,
        "Kostenstelle": kostenstelle,
        "Personalnummer": personalnummer,
        "Telefonnummer": telefonnummer,
        "Begrundung": begrundung,
        "scheduleName": scheduleName
    }

    with open("./resources/personal-data.json", "w") as f:
        f.write(json.dumps(config, indent=2, sort_keys=False))

    logging.info("personal data saved on ./resources/personal-data.json")


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
    options = int(input("Enter: \n1 - Create for input data file\n2 - Create pdf file\n").strip())

    if options == 1:
        create_template()
    if options == 2:
        write_pdf()
