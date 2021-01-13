# Database deployment:

`sudo -u postgres psql`  
`create role imdb_admin with password 'imdb_pass';`  
`alter role imdb_admin with login;`  
`create database imdb_parser with owner imdb_admin;`

# Migration mechanism:
`python3 manage.py makemigrations`  
`python3 manage.py migrate`

# Starting server:
`python3 manage.py runserver 0.0.0.0:8000`

# Main project logic contains in utils.py and views.py
