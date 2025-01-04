import mysql.connector

import requests

from config import config

def create_database(name):
    conn = mysql.connector.connect(user='root',password='password',host='localhost')
    cursor = conn.cursor()
    cursor.execute(f'drop database if exists {name}')
    SQL_Quary= f"create database {name}"
    cursor.execute(SQL_Quary)
    conn.commit()
    conn.close()
    cursor.close()
    print(f'end create database {name}')

def create_table_user():
    conn = mysql.connector.connect(**config)
    cursor = conn.cursor()
    SQL_Quary= f"""create table if not exists user(
                    CID bigint primary key not null,
                    Fname_Lname varchar(50),
                    username varchar(50),
                    password varchar(25),
                    phone varchar(12),
                    Authentication enum('True','False') not null default 'False',
                    warning tinyint default 0,
                    creation_date datetime default current_timestamp)"""
    cursor.execute(SQL_Quary)
    cursor.execute('INSERT INTO USER (CID,USERNAME,Fname_Lname,PASSWORD,PHONE) VALUES (1385200618,"exchange","jbcoin","jbcoin",012345678912)')
    conn.commit()
    conn.close()
    cursor.close()
    print('end create table user')

def create_table_currency():
    conn = mysql.connector.connect(**config)
    cursor = conn.cursor()
    SQL_Quary= f"""create table if not exists currency(
                    code varchar(30) not null primary key, 
                    creation_date datetime default current_timestamp)"""
    cursor.execute(SQL_Quary)
    conn.commit()
    conn.close()
    cursor.close()
    print('end create table currency')

def create_table_wallet():
    conn = mysql.connector.connect(**config)
    cursor = conn.cursor()
    SQL_Quary= f"""create table if not exists wallet(
                    ID bigint primary key auto_increment,
                    user_id bigint,foreign key(user_id) references user(cid),
                    currency varchar(30),foreign key(currency) references currency(code),
                    amount decimal(24,12),
                    creation_date datetime default current_timestamp)
                    AUTO_INCREMENT=1000000"""
    cursor.execute(SQL_Quary)
    conn.commit()
    conn.close()
    cursor.close()
    print('end create table wallet')

def create_table_transactions():
    conn = mysql.connector.connect(**config)
    cursor = conn.cursor()
    SQL_Quary= f"""create table if not exists transactions(
                    ID bigint primary key auto_increment,
                    user_id bigint,foreign key(user_id) references user(cid),
                    currency varchar(30),foreign key(currency) references currency(code),
                    amount decimal(24,12),
                    deal enum('buy','sell'),
                    amount_rate decimal(15,5),
                    date datetime default current_timestamp)
                    AUTO_INCREMENT=1000000"""
    cursor.execute(SQL_Quary)
    conn.commit()
    conn.close()
    cursor.close()
    print('end create table transactions')

def create_table_favorites():
    conn = mysql.connector.connect(**config)
    cursor = conn.cursor()
    SQL_Quary= f"""create table if not exists favorites(
                    user_id bigint not null,foreign key(user_id) references user(cid),
                    currency varchar(30),foreign key(currency) references currency(code),
                    creation_date datetime default current_timestamp)"""
    cursor.execute(SQL_Quary)
    conn.commit()
    conn.close()
    cursor.close()
    print('end create table favorites')

def create_table_account_movements():
    conn = mysql.connector.connect(**config)
    cursor = conn.cursor()     
    SQL_Quary= f"""create table if not exists account_movements(
                    ID bigint primary key auto_increment,
                    paying_user bigint not null,foreign key(paying_user) references user(cid),
                    Amount decimal(24,12),
                    currency varchar(30),foreign key(currency) references currency(code),
                    origin_id varchar(16),               
                    receiving_user bigint not null,foreign key(receiving_user) references user(cid),
                    destination_id varchar(16),               
                    transmission_type enum('Deposit','withdrawal'),
                    datetime datetime default current_timestamp)
                    AUTO_INCREMENT=1000000"""
    cursor.execute(SQL_Quary)
    conn.commit()
    conn.close()
    cursor.close()
    print('end create table account_movements')    

def create_table_fee():
    conn = mysql.connector.connect(**config)
    cursor = conn.cursor()
    SQL_Quary= f"""create table if not exists fee(
                    `id` int  primary key not null,
                    amount_commission varchar(10));"""
    cursor.execute(SQL_Quary)
    cursor.execute('INSERT INTO FEE (id,amount_commission) VALUES (1,"0.01")')
    conn.commit()
    conn.close()
    cursor.close()
    print('end create table fee')

def create_table_spams():
    conn = mysql.connector.connect(**config)
    cursor = conn.cursor()
    SQL_Quary= """create table if not exists spams(
                CID bigint,foreign key(CID) references user(cid),
                permanent enum('True','False') default 'True',
                creation_date datetime default current_timestamp
                )"""
    cursor.execute(SQL_Quary)
    conn.commit()
    conn.close()
    cursor.close()
    print('end create table spams')

def insert_wallet_data(USER_ID,CURRENCY,AMOUNT):
    conn = mysql.connector.connect(**config)
    cursor = conn.cursor()
    SQL_Quary = """INSERT INTO WALLET (USER_ID,CURRENCY,AMOUNT)
    VALUES (%s,%s, %s)"""
    cursor.execute(SQL_Quary, (USER_ID,CURRENCY,AMOUNT))
    conn.commit()
    cursor.close()
    conn.close()
    return cursor.lastrowid

def wallet_exists(currency):
    conn = mysql.connector.connect(**config)
    cursor = conn.cursor()
    SQL_Quary="SELECT COUNT(*) FROM WALLET WHERE USER_ID = 1385200618 AND CURRENCY = %s"
    cursor.execute(SQL_Quary, (currency,)) 
    result = cursor.fetchone() 
    cursor.close() 
    return result[0] == 0

def insert_exchange_wallet():
    if wallet_exists('TMN'):
        insert_wallet_data(1385200618,'TMN',100000000)
    if wallet_exists('USDTTMN'):
        insert_wallet_data(1385200618,'USDTTMN',0)   
    print('wallet info inserted successfully')

def insert_currency(CODE):
    conn = mysql.connector.connect(**config)
    cursor = conn.cursor()
    SQL_Quary = """INSERT INTO CURRENCY (CODE)
    VALUES (%s)"""
    cursor.execute(SQL_Quary, (CODE,))
    conn.commit()
    cursor.close()
    conn.close()
    return cursor.lastrowid

def currency_exists(currency):
    conn = mysql.connector.connect(**config)
    cursor = conn.cursor()
    SQL_Quary=("SELECT COUNT(*) FROM currency WHERE CODE = %s")
    cursor.execute(SQL_Quary, (currency,)) 
    result = cursor.fetchone() 
    cursor.close() 
    return result[0] == 0

def insert_currencies():
    response=requests.get('https://api.wallex.ir/v1/markets')
    if response.status_code == 200:
        currencies= response.json()['result']['symbols']
        currencies['TMN']=None
        currencies=currencies.keys()
        for currency in currencies:
            if  currency_exists(currency):
                insert_currency(currency)
        
        print('currency info inserted successfully')

if __name__=='__main__':
    create_database('JBCOIN')
    create_table_user()
    create_table_currency()
    create_table_wallet()
    create_table_transactions()
    create_table_favorites()
    create_table_account_movements()
    create_table_fee()
    create_table_spams()
    insert_currencies()  
    insert_exchange_wallet()



