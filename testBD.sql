CREATE TABLE accounts(id NUMBER(10) PRIMARY KEY, login VARCHAR(30) UNIQUE, passwordHash VARCHAR(40) NOT NULL);

CREATE TABLE users(
    id NUMBER REFERENCES accounts (id) PRIMARY KEY,
    name VARCHAR(50) NOT NULL,
    age NUMBER(3) NOT NULL CHECK(age BETWEEN 0 AND 110),
    sex CHAR(1),
    weight NUMBER(3),
    height NUMBER(3),
    registration_date DATE DEFAULT SYSDATE
);

CREATE TABLE foods(
    id NUMBER PRIMARY KEY,
    name VARCHAR (50) NOT NULL,
    calories NUMBER(4),
    portion_size NUMBER(4)
);

CREATE TABLE history(
    user_id NUMBER REFERENCES users (id),
    food_id NUMBER REFERENCES foods (id),
    meal_time DATE,
    grammage NUMBER (4),
    calories NUMBER(4),

    CONSTRAINT history_PK PRIMARY KEY (user_id, food_id, meal_time)
);


create sequence user_id
increment by 1;


create sequence food_id
increment by 1;
