# ProjetoBD2 - Installation
There are 3 steps to get the project running
1. create a venv
2. install dependencies
3. run

# 1. Create a venv
 ```
 python -m venv venv
 ```
 Then activate it
 ```
 venv\Scripts\activate
 cd bd2project
 ```
# 2. Install Dependencies
```
pip install django djongo psycopg2 dash pandas
```

# 3. Run it!
```
py manage.py runserver
```
# 4. Technical Issues
Currently there is no way to quiclky change the database links
