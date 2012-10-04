BEGIN TRANSACTION;
CREATE TABLE author (
	id INTEGER NOT NULL, 
	name VARCHAR, 
	PRIMARY KEY (id)
);
INSERT INTO author VALUES(1,'A222uthor12222');
INSERT INTO author VALUES(2,'Author2');
INSERT INTO author VALUES(3,'Author3');
INSERT INTO author VALUES(4,'asdfasdfasdf');
INSERT INTO author VALUES(5,'asdfasdfas3');
CREATE TABLE authors_books (
	book_id INTEGER, 
	author_id INTEGER, 
	FOREIGN KEY(book_id) REFERENCES book (id), 
	FOREIGN KEY(author_id) REFERENCES author (id)
);
INSERT INTO authors_books VALUES(2,2);
INSERT INTO authors_books VALUES(5,1);
INSERT INTO authors_books VALUES(5,3);
INSERT INTO authors_books VALUES(6,2);
CREATE TABLE book (
	id INTEGER NOT NULL, 
	title VARCHAR, 
	PRIMARY KEY (id)
);
INSERT INTO book VALUES(2,'Book21333');
INSERT INTO book VALUES(3,345);
INSERT INTO book VALUES(4,'atata');
INSERT INTO book VALUES(5,123123123123);
INSERT INTO book VALUES(6,'asdasdasd');
CREATE TABLE user (
	id INTEGER NOT NULL, 
	email VARCHAR, 
	password VARCHAR, 
	is_active BOOLEAN, 
	PRIMARY KEY (id), 
	CHECK (is_active IN (0, 1))
);
INSERT INTO user VALUES(1,'minouts@gmail.com','a1s1d1f1',1);
COMMIT;