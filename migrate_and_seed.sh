# !/bin/bash

# Generate migrations
poetry run python manage.py makemigrations

# Apply migrations 
poetry run python manage.py migrate

# Load initial data into the database from seed files
fixtures=$(ls seed/)
while IFS= read -r fixture; do
    echo -n "Seeding "
    echo $fixture
    poetry run python3 manage.py loaddata seed/$fixture
done <<< "$fixtures"