#!/bin/bash

# Run Redis initialization script
python initialize_redis.py

# Then run Django server
python manage.py runserver
