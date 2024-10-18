<p align="center">                                                                                                                                
    <img width="200" src="./assets/logo.png" />
</p>
<div align=center>                                                                                                                              
    <a href="https://test.pypi.org/project/mictlanx/"><img src="https://img.shields.io/badge/version-0.0.1--alpha.0-green" alt="build - 0.0.1-alpha.0"></a>                                                                                                                                     
</div>
<div align=center>
<h1>Axo: <span style="font-weight:normal;"> Backend</span></h1>
</div>   

# Axo - Backend
The Axo Backend is the core system for a platform designed to allow users to manage active objects dynamically and efficiently. This backend service provides comprehensive REST API to handle all business logic, and database interactions related to active object creation, modification, and retrieval.


# Getting started

Deploy the MongoDB Cluster:

```bash
docker compose -f ./db_cluster.yml up -d
```

Execute the next command in the mongo1 container: 

```bash
mongosh
```

Copy the init_repset.sh content in the mongo1 command line.

Install dependencies :

```bash
poetry lock 
poetry install
poetry shell
```

Run development server:

```bash
./run.sh
```

Now you can perform operation request on 17000 port.

## Test 🧪
Run the tests: Once everything is installed, you can run the tests using pytest with the following command:

```
pytest ./test/test_users.py
```
