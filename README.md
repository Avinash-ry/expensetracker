# auth-gateway
Manage Authentication for pdx and other applications

### **Setup auth-gateway Django project:**
***

1. Installing the Packages from the Ubuntu Repositories (do this one time when you setup your machine)
    `sudo apt install python3-venv python3-dev libpq-dev postgresql postgresql-contrib`
2. Create a blank postgres database in your local machine (do this when you need new blank database)
    `CREATE DATABASE <database_name>;`
    `GRANT ALL PRIVILEGES ON DATABASE <database_name> TO <db_user>;`
4. Clone the project repo from Github.
5. Move the `.env` file into pdx_auth_gateway/settings/. (Ask the latest env files from team)
6. Make sure you have updated database settings in env file
7. Create virtual environment (do this when you need new environment)
    `python3 -m venv <env_name>`  (env_name can be anything. Eg: env)
8. Activate virtual environment (need to activate each time when we run development server)
    `source <env_name>/bin/activate`
9. Go to the project root directory (where manage.py file is located)
10. Install all the dependicies from requirements.txt file (do this when there is a change in requirements)
    `pip install -r requirements.txt`
11. Run existing migrations (do this when there are unapplied migrations)
    `python manage.py migrate`
12. Create a superuser
    `python manage.py createsuperuser`
13. Run development server
    `python manage.py runserver 8008`

### **Setting Up OAuth Application:**
***

1. Log in to the Django admin panel using the superuser credentials you established earlier. You can access it [here](http://127.0.0.1:8008/admin/).

2. Navigate to the [OAuth Applications section](http://127.0.0.1:8008/oauth/applications) and create a new application using the provided link.

3. Before submitting the application form, securely store both the `client_id` and `client_secret`.

4. On the application form, ensure that you select `client_type = confidential` and `grant_type = authorization_code`.

5. Set the `redirect_uri` to something like `http://127.0.0.1:8000/auth-gateway/callback/`. Make sure that this endpoint exists on your resource server.

Now Auth-server is up and running. All the task for user authentication will be done from resource server using apis.