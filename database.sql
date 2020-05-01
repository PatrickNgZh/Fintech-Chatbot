create table tb_users
(
    id     varchar(50) primary key,
    avatar varchar(200),
    name   varchar(200)
);

create table tb_insurance
(
    id      varchar(50) primary key,
    user_id varchar(50) null,
    foreign key (user_id) references tb_users (id)
);

create table tb_records
(
    id int auto_increment primary key,
    image        varchar(200),
    user_id      varchar(50),
    insurance_id varchar(50),
    location     varchar(200),
    create_time  datetime,
    foreign key (insurance_id) references tb_insurance(id),
    foreign key (user_id) references tb_users(id)
);





