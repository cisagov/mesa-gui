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
python manage.py runserver
```

# Migrations
```bash
python manage.py makemigrations mesa -n <name_of_file>
python manage.py sqlmigrate mesa 0008
python manage.py migrate
```

# Template Used

https://startbootstrap.com/theme/sb-admin-2


