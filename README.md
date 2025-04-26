# CloudBloodBank
Creating a blood bank database tool for the Charlotte area. Built to be deployed on EC2.

# Set-up locally
You must have postgres installed, which you can do through [here](https://www.postgresql.org/download/).

Set up a python virtual environment and activate it

Run the following command inside the bloodbank directory:

`pip install -r requirements.txt`

Create a postgres database and enter in the corresponding details into bloodbank/bloodbank/settings.py:
'NAME': 'NAME',
'USER': 'USER',
'HOST': 'localhost',
'PORT': '5432'

create an .env file in bloodbank and input the following,
>db_password=PASSWORD 
>G_KEY=GKEY
Where PASSWORD is the password to your database and GKEY is the Google Maps API key

From here you should be able to run 'python manage.py runserver' and run the application for testing and debugging

Additionally, for test data in the database you can run 'python  populate_db.py'

# To deploy
instal ngix
install gunicorn
set-up pats for static file
gunicorn request to serve files at host at the ports
in aws set inbound rules for who can access the site
link ipv4 address from the instance in cloudflare
