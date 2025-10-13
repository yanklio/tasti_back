#!/bin/bash

# Run database migrations
python src/manage.py migrate

# Create superuser if it doesn't exist
python src/manage.py shell -c "
import os
from django.contrib.auth import get_user_model

User = get_user_model()
username = os.environ.get('DJANGO_SUPERUSER_USERNAME')
email = os.environ.get('DJANGO_SUPERUSER_EMAIL')
password = os.environ.get('DJANGO_SUPERUSER_PASSWORD')
print(f'Superuser username: {username}')
print(f'Superuser email: {email}')
print(f'Superuser password set: {bool(password)}')
if username and not User.objects.filter(username=username).exists():
    print('Creating superuser...')
    User.objects.create_superuser(
        username=username,
        email=email,
        password=password
    )
    print('Superuser created.')
else:
    print('Superuser already exists or username not provided.')
"

# Execute the main command
exec "$@"
