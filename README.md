# Login System
 Flask + SQLAlchemy simple login/registration system. In the system there is the admin user who has permission to create users. Ordinary users cannot create users.


## Setup

Install the Python requirements:

```
python3 -m pip install -r requirements.txt
```

Initialize the database:

```
cd server
python3 app.py initdb
```

## Server

Run with the builtin (debug) server:

```
python3 app.py runserver -h 0.0.0.0 -p 8080 --threaded

```
The server should now be accessible on http://localhost:8080

## Images

![image](https://user-images.githubusercontent.com/29102315/231795695-0ce85887-9e49-4ed7-8dc9-564e3e9c33d1.png)

![image](https://user-images.githubusercontent.com/29102315/231796036-769d8cdf-e620-440c-bfc1-67303117b5be.png)

![image](https://user-images.githubusercontent.com/29102315/231796997-b6ca8c96-cbd8-4e7d-bc6a-35d3e10163d3.png)

![image](https://user-images.githubusercontent.com/29102315/231797212-f003cbbd-b5e2-4909-9d0e-a888a4c6f92d.png)


