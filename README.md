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
**Django Deployment on EC2 with Gunicorn, Nginx, and Cloudflare**

---

1. SSH into EC2:

   ```bash
   ssh -i your-key.pem ubuntu@your-ec2-public-ip
   ```

2. Update server:

   ```bash
   sudo apt update && sudo apt upgrade
   ```

3. Install Python, pip, and virtualenv:

   ```bash
   sudo apt install python3-pip python3-venv
   ```

4. Install Nginx:

   ```bash
   sudo apt install nginx
   ```

5. Install Gunicorn inside your project virtual environment:

6. Clone or upload your Django project to the server.

7. Create and activate a virtual environment:

   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```

8. Install project requirements:

   ```bash
   pip install -r requirements.txt
   ```

9. Set `ALLOWED_HOSTS` in `settings.py`.

10. Collect static files:

    ```bash
    python manage.py collectstatic
    ```

11. Test Gunicorn manually:

    ```bash
    gunicorn --bind 0.0.0.0:8000 your_project_name.wsgi:application
    ```

12. Create a Gunicorn systemd service file `/etc/systemd/system/yourproject.service`.

13. Start and enable Gunicorn service:

    ```bash
    sudo systemctl start yourproject
    sudo systemctl enable yourproject
    ```

14. Configure Nginx server block `/etc/nginx/sites-available/yourproject`.

15. Enable Nginx configuration:

    ```bash
    sudo ln -s /etc/nginx/sites-available/yourproject /etc/nginx/sites-enabled
    sudo nginx -t
    sudo systemctl reload nginx
    ```

16. Open EC2 Security Group inbound rules:

    - Allow ports 22 (SSH), 80 (HTTP), 443 (HTTPS).

17. Link domain to EC2 IPv4 address in Cloudflare (or other DNS provider).

**End of Deployment Steps**

