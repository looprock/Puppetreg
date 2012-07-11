CREATE table registered (
id int(10) auto_increment NOT NULL,
status int(1) NOT NULL,
node varchar(512) NOT NULL,
entered TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
PRIMARY KEY (id)
);

CREATE table client (
lastupdate TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
lastnode varchar(512) NOT NULL
);

insert into client (lastnode) values ('notarealnode');

CREATE table update_check (
lastcheck TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
lastnode varchar(512) NOT NULL
);
insert into update_check (lastnode) values ('notarealnode');
