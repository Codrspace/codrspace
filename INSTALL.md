# Installation Instruction

The following steps are required to install a local verison of codrspace.com.
You can see the full hosted solution on EC2 at http://codrspace.com.
Please keep in mind that there are a few limitations to running just the local
version:

1. We are using Github OAuth for signup/authentication, which only allows a
   single callback url for the final part of the OAuth process.  Thus, this
   callback url is set to the hosted version and faked on a local development version.
2. You will not be able to have a nice profile and missing a lot of Github
   integration if you run locally without an external Internet connection.
   Please connect to the Internet :)

**See section on 'Running project' for information on how to run both instances locally**

## General environment setup

### Non-virtualenv install

- Install python 2.6 or 2.7 `http://www.python.org`
- Install setuptools
    - Download project from: `http://pypi.python.org/pypi/setuptools#files`
    - Run the following: `sh setuptools-0.6c9-py2.4.egg` (replace with egg file from above)
- install pip
    - `easy_install pip`
- Clone project
    - `git clone git@github.com:Codrspace/codrspace.git codrspace_app`
- Use pip to install all project dependencies
    - `pip install -r requirements_dev.pip` (requirements file is in root of project)

### Install with virtualenv

- Install python 2.6 or 2.7 `http://www.python.org`
- Install virtualenv
    - `pip install virtualenv`
    - `pip install virtualenvwrapper`
- Add the following lines to your .bashrc and restart your shell

    - `export WORKON_HOME=$HOME/.virtualenv`
    - `source /usr/local/bin/virtualenvwrapper.sh`
    - `export PIP_VIRTUALENV_BASE=$WORKON_HOME`
    - `export PIP_RESPECT_VIRTUALENV=true`

- Make a virtualenv called `codrspace_app`
    - `mkvirtualenv codrspace_app`
- Activate the virtual environment
    - `workon codrspace_app`
- Clone project
    - `git clone git@github.com:Codrspace/codrspace.git codrspace_app`
- Use requirements file to install all project libraries:
    - `pip install -r requirements_dev.pip`

### Running project locally after environment setup

Due to limitation #1, we have developed a solution to 'fake' out the OAuth
callbacks for local testing.  Unfortunately it requires running two Django dev servers.

1. Clone the project, copy the example local_settings, start the server on port 9000 for oAuth.

  - `git clone git://github.com/durden/dash.git codrspace_app`
  - `cd codrspace_app`
  - `workon codrspace_app` (only if you used the virtualenv route)
  - `cp example_local_settings.py local_settings.py`
  -  set `username` key in `GITHUB_AUTH` in your `local_settings.py` to your github username
  - `python manage.py syncdb`
  - `python manage.py runserver 9000`

2. Open another shell and start the dev server on port 8000 for the site.

  - `cd codrspace_app`
  - `workon codrspace` (only if you used the virtualenv route)
  - `python manage.py runserver `

Now you have two instances of the django development server running.
The instance on port 9000 is only for fake oAuth validation.

Use the site as you normally would through `http://localhost:8000`.

### Setting up API keys

- Manually apply the following patch to tastypie:
    [tastypie bugfix](https://github.com/toastdriven/django-tastypie/commit/520b33f)

- Now you have a few choices:
    1. Delete your database and run `python manage.py syncdb` again
    2. Back-fill any existing users with api keys by running:
        - `python manage.py backfill_api_keys`
