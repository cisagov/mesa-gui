# Getting started

```bash
git clone https://github.com/cisagov/mesa-gui
cd mesa-gui

# create virtual environment
python3 -m venv venv
. ./venv/bin/activate

# install mesa-toolkit
pip install -e .

# run the application
cd mesa_gui
python manage.py migrate
python manage.py createsuperuser
python manage.py loaddata mesa/fixtures/mesajobs.json

# generate a self-signed SSL certificate
openssl req -x509 -newkey rsa:4096 -keyout key.pem -out cert.pem -days 365 -nodes -subj "/C=/ST=/L=/O=/OU=/CN="

# start the web application
python manage.py runserver --certificate cert.pem --key key.pem 0.0.0.0:8080
```

# Migrations
```bash
python manage.py makemigrations mesa -n <name_of_file>
python manage.py sqlmigrate mesa 0011
python manage.py migrate
```

# Template Used

https://startbootstrap.com/theme/sb-admin-2


