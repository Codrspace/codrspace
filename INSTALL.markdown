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
    3. Running locally will always authenticate and setup profile as the same
       github user.  This is because we can't get a real access token running
       locally from the 'faked' instance.  So, the local instance always
       assumes your the same user.  However, you can modify this in your
       local_settings.py to at least run as your own user locally or just use
       the default user, 'durden'.

    * See section on 'Running project' for information on how to run both
    * instances locally

## General environment setup

### Non-virtualenv install

- Install python 2.6
- Install setuptools
    - Download project from: http://pypi.python.org/pypi/setuptools#files
    - Run the following: sh setuptools-0.6c9-py2.4.egg (replace with egg file from above)
- install pip
    - 'easy_install pip'
- Clone project
- Use pip to install all project dependencies
    - pip install -r requirements.pip (replace with location of file from this project)

### Install with virtualenv

- Use python 2.6
- Install virtualenv
    - easy_install virtualenv
- Create virtualenv for project
    - mkdir ~/.virtualenvs
    - virtualenv --no-site-packages -v -p python2.6 ~/.virtualenvs/codrspace
    - This installs pip into THIS virtualenv.
- Activate/switch to using virtualenv
    - source ~/.virtualenvs/codrspace/bin/activate
- Use requirements file to install all project libraries:
    - pip install -E ~/.virtualenvs/codrspace/ -v -r ~/Documents/codrspace/requirements.pip

    - NOTE: django-syntax-colorize isn't installed via pip b/c it doesn't have
            a setup.py so it won't install this way.
        - Not a big deal b/c we can easily 'install' it by moving syntax_color.py
          to our templatetags directory
        - Thus, this file is committed.

### Running project locally after environment setup

Due to limitation #1, we have developed a solution to 'fake' out the OAuth
callbacks for local testing.  Unforunately it requires a bit of manual setup.
    1. Clone the project twice (1 for the 'normal' access and 1 for faked
       Github OAuth.
        Example setup:
            - cd /var/tmp/
            - git clone git://github.com/durden/dash.git main_instance
            - git clone git://github.com/durden/dash.git fake_oauth_instance
            - cd /var/tmp/fake_oauth_instance
            - cp example_local_settings.py local_settings.py
            - Edit local_settings.py to use your own github user name if you
              want to run as someone other than the default 'durden'
            - python manage.py sncydb
            - python manage.py runserver localhost:9000

            ** Now you have your local github OAuth instance running that your
            main instance can authenticate against.

            - cd /var/tmp/main_instance
            - python manage.py sncydb
            - python manage.py runserver

            ** Now you can run as usual by going to http://localhost:8000

#### Normal virtualenv workflow
- Activate/switch to using virtualenv
    - source ~/.virtualenvs/codrspace/bin/activate
- Setup virtualenvwrapper.sh scripts
    - source virtualenvwrapper.sh
