# MESA GUI

Micro Evaluation Security Assessments (MESAs) are designed to provide organizations with insights into their internal security posture. The MESA-GUI serves as a user-friendly front-end for the MESA-Toolkit command-line interface (https://github.com/cisagov/mesa-toolkit/). This project relies on the successful installation of the MESA-Toolkit and is not intended to function as a standalone application.

It is important to note that MESAs are not designed to furnish a comprehensive understanding of the entire internal environment. Instead, their purpose is to equip organizations with the essential information needed to establish a foundational security posture. This emphasis revolves around safeguarding against commonly exploited misconfigurations and vulnerabilities. MESAs lay the groundwork for organizations to initiate the process of fortifying their security stance, ensuring a proactive defense against prevalent risks.

# Getting started

Once the MESA-Toolkit has been successfully installed on a `Debian 12.7.0` instance, the following commands can be used to manually setup the MESA-GUI:

```bash
git clone https://github.com/cisagov/mesa-gui
cd mesa-gui

# create virtual environment
python3 -m venv venv
. ./venv/bin/activate

# install mesa-gui
pip install -e .

# run the application
cd mesa_gui
python manage.py migrate
python manage.py createsuperuser
python manage.py loaddata mesa/fixtures/mesajobs.json

# generate a self-signed SSL certificate
openssl req -x509 -newkey rsa:4096 -keyout key.pem -out cert.pem -days 365 -nodes -subj "/C=/ST=/L=/O=/OU=/CN="

# start the web application
python manage.py runsslserver --certificate cert.pem --key key.pem 0.0.0.0:8080
```

# Migrations
Migrations will need to be created when making alterations to the SQL database. The following commands can be used to create a migration:

```bash
python manage.py makemigrations mesa -n <name_of_file>
python manage.py sqlmigrate mesa 0011
python manage.py migrate
```

# Template Used

https://startbootstrap.com/theme/sb-admin-2


