import os
import time
import pandas as pd
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.dialects.oracle import FLOAT, NUMBER, VARCHAR2, DATE
import cx_Oracle

def load_env_variables():
    load_dotenv('./.env')
    return os.getenv('hostname'), os.getenv('port'), os.getenv('sid'), os.getenv('username'), os.getenv('password')

def load_data():
    df = pd.read_parquet('./transaction_data.parquet')
    df["TransactionTime"] = pd.to_datetime(df['TransactionTime'])
    return df.sort_values(by='TransactionTime', ascending=True)

def create_oracle_connection(hostname, port, sid, username, password):
    dsn = cx_Oracle.makedsn(host=hostname, port=port, sid=sid)
    return cx_Oracle.connect(user=username, password=password, dsn=dsn)

def create_sqlalchemy_engine(username, password, dsn):
    return create_engine(f'oracle+cx_oracle://{username}:{password}@{dsn}')

def insert_rows(df, connection, schema_name, table_name):
    dtype = {
        "UserId" : NUMBER,
        "TransactionId" : NUMBER,      
        "TransactionTime": DATE,
        "ItemCode": NUMBER,
        "ItemDescription": VARCHAR2(255),
        "NumberOfItemsPurchased": NUMBER,
        "CostPerItem": FLOAT,
        "Country": VARCHAR2(124),
    }

    for i, row in df.iterrows():
        transaction = connection.begin()
        try:
            row_df = pd.DataFrame(row).T
            lower_case_table_name = table_name.lower()
            row_df.to_sql(lower_case_table_name, connection, schema=schema_name, if_exists='append', index=False, dtype=dtype)
            print(f"Inserted row {i + 1} into table {lower_case_table_name}")
            transaction.commit()
            time.sleep(5)
        except Exception as e:
            transaction.rollback()
            print("Error occurred:", e)

def main():
    # hostname, port, sid, username, password = load_env_variables()
    hostname="midtown-32"
    sid="ORCLCDB"
    port="1521"
    # service_name=ORCLPDB1
    username="C##MYUSER"
    password="password"
    df = load_data()
    connection = create_oracle_connection(hostname, port, sid, username, password)
    engine = create_sqlalchemy_engine(username, password, connection.dsn)
    schema_name = 'C##MYUSER'
    table_name = "TRANSACTIONS"

    with engine.connect() as connection:
        insert_rows(df, connection, schema_name, table_name)

    print("All rows inserted successfully!")

if __name__ == "__main__":
    main()