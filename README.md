# challenges
django python tool to do some dart challenges.

#Run
```bash
$ git clone https://github.com/spezi/challenges.git 
$ virtualenv -p python3 venv
$ source venv/bin/activate
$ pip install -r requirements.txt
```

#init django
```bash
$ ./manage.py createsuperuser
$ ./manage.py makemigrations
$ ./manage.py migrate
$ ./manage.py collectstatic
```
#run debug django
```bash
$  ./manage.py runserver
```
point your browser to (https://127.0.0.1:8000)
