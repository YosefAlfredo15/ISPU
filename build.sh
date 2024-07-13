#!/bin/bash

# Mengaktifkan virtual environment
source $VIRTUAL_ENV_PATH

# Menginstal dependensi
pip install -r requirements.txt

# Perintah build lainnya jika diperlukan
# Misalnya: python manage.py collectstatic --noinput
