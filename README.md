# **KOKO NETWORKS INTERVIEW EXERCISE**

## Prerequisites
1. Python 3.7 (or above)
2. [Poetry](https://python-poetry.org)
3. Docker & Docker Compose


## Configuration & Installation

1. Rename the **sample settings.py** to **settings.py** and update it  in odoo_api/app/
2. Create a **odoo-server.log** file in odoo12/etc/
3. Change the folder permission to make sure that the container is able to access the directory:
````
$ sudo chmod -R 777 addons
$ sudo chmod -R 777 etc
$ mkdir -p postgresql
$ sudo chmod -R 777 postgresql
````
4. Run `docker-compose up -d`


