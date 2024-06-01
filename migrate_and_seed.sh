# !/bin/bash

# Generate migrations
poetry run python manage.py makemigrations

# Run migrations
poetry run python manage.py migrate

# Run seeders 
fixtures=$(ls seed/)
while IFS= read -r fixture; do
    echo -n "Seeding "
    echo $fixture
    poetry run python3 manage.py loaddata seed/$fixture
done <<< "$fixtures"