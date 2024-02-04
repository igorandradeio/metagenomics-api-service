from .models import Country
import csv


def seed_countries():
    # Path to the countries file
    countries_file_path = "countries.csv"

    # Create instances of the Country model and save to the database
    with open(countries_file_path, "r", encoding="utf-8") as file:
        reader = csv.reader(file)
        for row in reader:
            name, code = row
            Country.objects.get_or_create(name=name, code=code)
