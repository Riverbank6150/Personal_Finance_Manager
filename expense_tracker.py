import os
import shutil

from functions import *

from decimal import Decimal
# from dotenv import load_dotenv
import json
import urllib
import csv
import requests
import mysql.connector
import pandas as pd
from sqlalchemy import create_engine
import numpy as np
import matplotlib.pyplot as plt
import MySQLdb
import MySQLdb.cursors
import re
import plotly.express as px
import seaborn as sns


# -----TODO: get banking information from plaid api referencing the quickstart file
def bank_statements_extraction():

    return 0
    # print("hello world")


def csv_to_dataframe():
    # read_file = pd.read_csv('cibc.csv', header=None)
    # initial_directory = 'C:/users/Cameron/downloads/cibc.csv'
    initial_directory = 'C:/Users/Cameron/Downloads/cibc.csv'

    # foo file for the sake of testing
    final_directory = 'C:/Users/Cameron/Desktop/Python_Projects/Personal_Finance_Manager/data/foo.csv'

    # ifExist = os.path.exists(path)
    # print(ifExist)

    if os.path.exists(initial_directory):
        # os.rename(initial_directory, final_directory)
        shutil.move(initial_directory, final_directory)

    df = pd.read_csv(final_directory)

    # if

    print(df)

    return 0


def visa_csv_to_dataframe():
    # read original bank transaction csv file and create dataframe with headers added - original csv file does not have headers, just data
    read_file = pd.read_csv('data/visa.csv', header=None)
    visa_df = pd.DataFrame(read_file)
    visa_df.columns = ['date_of_transaction', 'transaction_information', 'amount_transacted_out',
                       'amount_transacted_in',
                       'card_number']

    # visa_df = visa_df.apply(visa_dataframe_column_updates, axis=1)

    # changes date_of_transaction column to correct date time for inserting into mySQL table
    visa_df['date_of_transaction'] = pd.to_datetime(visa_df.date_of_transaction).dt.normalize()

    # applies 'transaction_amounts' function to dataframe
    visa_df["amount_transacted"] = visa_df.apply(transaction_amounts, axis=1)
    # applies 'transaction_amounts' function to dataframe
    visa_df["type_of_transaction"] = visa_df.apply(transaction_types, axis=1)

    # deletes 'amount transacted in/out' columns as the values have been merged into one column while another column
    # was created to determine the in or out status of each transaction
    del visa_df['amount_transacted_out'], visa_df['amount_transacted_in'], visa_df['card_number']

    # visa_df = visa_df.drop(visa_df[visa_df['transaction_information'] == 'PAYMENT THANK YOU/PAIEMEN T MERCI'].index)

    visa_df["transaction_category"] = visa_df.apply(visa_transaction_category, axis=1)

    return visa_df


def savings_csv_to_dataframe():
    savings_read_file = pd.read_csv('data/savings.csv', header=None)
    savings_df = pd.DataFrame(savings_read_file)
    savings_df.columns = ['date_of_transaction', 'transaction_information', 'amount_transacted_out',
                          'amount_transacted_in']

    savings_df['date_of_transaction'] = pd.to_datetime(savings_df.date_of_transaction).dt.normalize()

    savings_df["amount_transacted"] = savings_df.apply(transaction_amounts, axis=1)
    savings_df["type_of_transaction"] = savings_df.apply(transaction_types, axis=1)

    del savings_df['amount_transacted_out']
    del savings_df['amount_transacted_in']

    savings_df["transaction_category"] = savings_df.apply(savings_transaction_category, axis=1)

    return savings_df


def print_to_files(visa_df, savings_df):
    visa_df.to_csv('data/updated_visa.csv', encoding='utf-8', index=False)
    savings_df.to_csv('data/updated_savings.csv', encoding='utf-8', index=False)

    visa_df.to_json('data/updated_visa.json', orient="records", lines=True)
    savings_df.to_json('data/updated_savings.json', orient="records", lines=True)

    visa_df.to_parquet('data/updated_visa.parquet', compression='gzip')
    savings_df.to_parquet('data/updated_savings.parquet', compression='gzip')

    visa_df.to_excel('data/updated_visa.xlsx', index=False)
    savings_df.to_excel('data/updated_savings.xlsx', index=False)


def savings_balance(visa_df, savings_df):
    balance = savings_df.groupby('type_of_transaction', as_index=False)['amount_transacted'].sum()
    balance = balance.values[0][1] - balance.values[1][1]

    balance = round(balance, 2)

    # b/c transaction tracking for CIBC was not done until after 28/AUG/2017
    # balance = balance + 2286.04

    print(balance)


# function that uses google's "Knowledge Graph Search" API to determine the category that each transaction falls under
# using the 'transaction information' column from the bank transaction csv file
def spending_category(visa_df):
    api_key = open('knowledge_graph_search_api_key.txt').read()
    search_query = "SMASH KITCHEN & BAR"

    service_url = 'https://kgsearch.googleapis.com/v1/entities:search'
    params = {
        'query': search_query,
        'key': api_key,
        'limit': 1,
        'indent': True
    }

    url = service_url + '?' + urllib.parse.urlencode(params)
    response = json.loads(urllib.request.urlopen(url).read())
    # print(response)

    # api_key = open('custom_search_api_key.txt').read()
    # search_engine_id = open('custom_search_search_engine_id.txt')
    #
    # search_query = "McDonald's"
    # url = 'https://www.googleapis.com/customsearch/v1'
    # params = {
    #     'q': search_query,
    #     'key': api_key,
    #     'cx': search_engine_id,
    #     'lr': 'lang_en',
    #     'gl': 'CA'
    # }
    # response = requests.get(url, params=params)
    # results = response.json()['items']
    #
    # for item in results:
    #     print(item)

    # for element in response['itemListElement']:
    #     print(element['result']['description'])
    # print(visa_df['transaction_information'][0])

    #     print(element['description'])
    #     print(element['result']['name'] + element['result']['description'])

    # for element in response['itemListElement']:
    #     print(element['result']['name'] + ' (' + str(element['resultScore']) + ')')


def bank_transactions_to_database_transformation(visa_df, savings_df):
    # connection to MySQL database
    db_conn = MySQLdb.connect(
        host='localhost',
        user='root',
        password=open('sql_password.txt').read(),
        database='bank_transactions',
        cursorclass=MySQLdb.cursors.DictCursor
    )
    cursor = db_conn.cursor()

    # reads the sql commands file to create desired MySQL table in the database
    with open('bank_transactions.sql', 'r') as sql_file:
        sql_script = sql_file.read().split(';')
    sql_file.close()
    for table in sql_script:
        table = re.sub('[\n\r]', '', table)
        if len(table) > 0:
            cursor.execute(table)

    # insert values from dataframe into MySQL table
    engine = create_engine(
        "mysql+mysqlconnector://root:" + (open('sql_password.txt').read()) + "@localhost/bank_transactions")
    visa_df.to_sql(name='visa_transactions', con=engine, if_exists='append', index=False)
    savings_df.to_sql(name='savings_transactions', con=engine, if_exists='append', index=False)

    # query the sql table to get desired values
    query = "SELECT date_of_transaction AS transaction_date, SUM(amount_transacted) AS amount_spent_in_day FROM visa_transactions WHERE type_of_transaction = 'out' AND date_of_transaction > '2024-01-01' GROUP BY date_of_transaction"
    cursor.execute(query)
    result = cursor.fetchall()

    return result


# function to visualize the visa_transactions in matplotlib by placing the selected MySQL table values into a new
# dataframe
def transaction_to_visualization_tool_load_from_sql(result):
    transaction_amount_each_day = pd.DataFrame(result, columns=['transaction_date', 'amount_spent_in_day'])

    plt.bar(transaction_amount_each_day['transaction_date'], transaction_amount_each_day['amount_spent_in_day'],
            edgecolor='black', linewidth=0.7)
    plt.xlabel("Transaction date")
    plt.ylabel("Amount transacted")
    plt.title("Visa Transactions")
    plt.show()


def transaction_to_visualization_tool_load_from_df(visa_df: pd.DataFrame, savings_df):
    visa_df = visa_df.apply(visa_dataframe_time_grouping, axis=1)

    visa_df = visa_dataframe_summation(visa_df)

    # pd.options.display.max_columns = None
    # pd.options.display.max_rows = None
    # print(visa_df)

    filtered_visa_df = filtered_visa_dataframe(visa_df)

    sns.set_theme(style="whitegrid")

    sns.catplot(data=filtered_visa_df,
                kind='bar',
                x='transaction_category',
                y='monthly_sum',
                hue='month_of_transaction')

    plt.xticks(rotation=45)
    # plt.tight_layout()

    plt.show()