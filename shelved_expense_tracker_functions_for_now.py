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