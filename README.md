# Pet-rating
Fork from gitlab.utu.fi/tithei/pet-rating  
**See branch: master**  
An online experiment **platform** for research

# Set env
Anaconda + MySQL

# Usage
- Anaconda Prompt / base env:
  `conda create -n pet python=3.6`
- Anaconda Prompt / base env:
  `conda activate pet`
- Change dir to pet folder:
  `pip install -r requirements.txt`
- Config MySQL:
  1. `sudo mysql -u user -p`
  2. `CREATE DATABASE rating_db;`
  3. `CREATE USER 'rating'@'localhost' IDENTIFIED BY 'rating';`
  4. `GRANT ALL PRIVILEGES ON rating_db.* TO 'rating'@'localhost';`
- execute **new** create_rating_db.sql:
  `mysql -u rating -p -D rating_db < db/create_rating_db.sql;`
- run flask app:
  `flask run --host=0.0.0.0`
- allow local network access:
  `sudo ufw allow 5000/tcp`

# Change MySQL setting
- user pwd: change syntax `CREATE USER 'username'@'host' IDENTIFIED BY 'password';`
- modify config.py Line 10 `MYSQL_PASSWORD = config('MYSQL_PASSWORD', default='password')`
