# General information

The following steps are required to install a local verison of codrspace.com.
You can see the full hosted solution via linode at http://www.codrspace.com.
Please keep in mind that there are a few limitations to running just the local
version:

1. We are using Github OAuth for signup/authentication, which only allows a
   single callback url for the final part of the OAuth process.  Thus, this
   callback url is set to the hosted version.
2. You will not be able to have a nice profile and missing a lot of Github
   integration if you run locally without an external Internet connection.
   Please connect to the Internet :)
3. Running locally will always authenticate and use the same github user.
   This is because we can't get a real access token running
   locally from the 'faked' instance.  So, the local instance always
   assumes your the same user.  However, you can modify this in your
   local_settings.py using `GITHUB_USER`. It defaults to user `durden`

* See section on 'Running project' for information on how to run both
* instances locally

## General environment setup

### Non-virtualenv install

- Install python 2.6 or 2.7
- Install setuptools
    - Download project from: `http://pypi.python.org/pypi/setuptools#files`
    - Run the following: `sh setuptools-0.6c9-py2.4.egg (replace with egg file from above)`
- install pip
    - `easy_install pip`
- Clone project
    - `git clone git@github.com:durden/dash.git`
- Use pip to install all project dependencies
    - `pip install -r requirements.pip (requirements file is in root of project)`

### Install with virtualenv

- Use python 2.6 or 2.7
- Install virtualenv
    - `pip install virtualenv`
    - `pip install virtualenvwrapper`
- Add the following to your .bashrc and restart your shell

    export WORKON_HOME=$HOME/.virtualenv
    source /usr/local/bin/virtualenvwrapper.sh
    export PIP_VIRTUALENV_BASE=$WORKON_HOME
    export PIP_RESPECT_VIRTUALENV=true

- Make a virtualenv called `codrspace`
    - `mkvirtualenv codrspace`
- Activate the virtual environment
    - `workon codrspace`
- Use requirements file to install all project libraries:
    - `pip install -r requirements.pip`

**NOTE**: django-syntax-colorize isn't installed via pip b/c it doesn't have a setup.py.
- Not a big deal b/c we can easily 'install' it by moving syntax_color.py
  to our templatetags directory
- Thus, this file is already in the repo.

### Running project locally after environment setup

Due to limitation #1, we have developed a solution to 'fake' out the OAuth
callbacks for local testing.  Unforunately it requires a bit of manual setup.

1. Clone the project twice (1 for the 'normal' access and 1 for faked Github OAuth.

    - `git clone git://github.com/durden/dash.git codrspace`
    - `git clone git://github.com/durden/dash.git codrspace_oauth_instance`
    - `cd codrspace_oauth_instance`
    - `cp example_local_settings.py local_settings.py`
    - set `GITHUB_USER` in your local settings to your github username
    - `python manage.py syncdb`
    - `python manage.py runserver localhost:9000`

Next sync and start the main codrspace instance.

    - `cd codrspace`
    - `python manage.py sncydb`
    - `python manage.py runserver`

Now you have two instances of the django development server running.
One for `codrspace` and one for `codrspace_oauth_instance`. 

The `codrspace_oauth_instance` is only to **fake validate** the user so you don't 
have to set up a new application on github. 

Use the site as you normally would through `http://121.0.0.1:8000`
