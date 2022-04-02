CREATE TABLE users (id SERIAL PRIMARY KEY, username TEXT, password TEXT);
CREATE TABLE apartments (id SERIAL PRIMARY KEY, area INT, rooms INT, building TEXT, location TEXT, rent INT, condition TEXT, descr TEXT);

