CREATE TABLE users (id SERIAL PRIMARY KEY, username TEXT, password TEXT);
CREATE TABLE apartments (id SERIAL PRIMARY KEY, area INT, rooms INT, building TEXT, location TEXT, rent INT, condition TEXT, descr TEXT);
CREATE TABLE applied (id SERIAL PRIMARY KEY, user_id INTEGER REFERENCES users, apartment_id INTEGER REFERENCES apartments);
CREATE TABLE faved (id SERIAL PRIMARY KEY, user_id INTEGER REFERENCES users, apartment_id INTEGER REFERENCES apartments);
CREATE TABLE admins (id SERIAL PRIMARY KEY, username TEXT, password TEXT);
