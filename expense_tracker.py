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


def csv_to_dataframe_wip():
    initial_directory = os.path.expanduser('~/downloads/cibc.csv')

    # cibc file for the sake of testing
    intermediate_directory = 'data/cibc.csv'

    if os.path.exists(initial_directory):
        shutil.move(initial_directory, intermediate_directory)

    # TODO: determine the amount of columns in the csv file to then rename the file itself
    # with open('data/foo.csv', newline='') as foofile:
    #     reader = csv.reader(foofile)
    #     for row in reader:
    #         print(row)
    #         if row.count == 5:
    #             print('yes')

    if os.path.exists(intermediate_directory):
        with open(intermediate_directory, newline='') as foofile:
        # reader = (csv.reader(foofile))
        # for row in reader:
        #     print(row)
        # print(list(reader))

            reader = list(csv.reader(foofile))

    # if len(reader[0])

            # print(len(reader[0]))
            # print(reader[4])

        if len(reader[0]) == 5:
            shutil.move(intermediate_directory, 'data/visa.csv')

        elif len(reader[0]) == 4:
            shutil.move(intermediate_directory, 'data/savings.csv')

    # print("rows:", len(reader))
    # print("columns:", len(reader[0]))

    df = pd.read_csv('data/visa.csv')

    print(df)

    return 0


def visa_csv_to_dataframe():
    # read original bank transaction csv file and create dataframe with headers added - original csv file does not have headers, just data
    if os.path.exists('data/visa.csv'):
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
    if os.path.exists('data/savings.csv'):
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



# def csv_to_dataframe(visa_df=None, savings_df=None):
#     if os.path.exists('data/visa.csv'):
#         read_file = pd.read_csv('data/visa.csv', header=None)
#         visa_df = pd.DataFrame(read_file)
#         visa_df.columns = ['date_of_transaction', 'transaction_information', 'amount_transacted_out',
#                            'amount_transacted_in',
#                            'card_number']
#
#         # visa_df = visa_df.apply(visa_dataframe_column_updates, axis=1)
#
#         # changes date_of_transaction column to correct date time for inserting into mySQL table
#         visa_df['date_of_transaction'] = pd.to_datetime(visa_df.date_of_transaction).dt.normalize()
#
#         # applies 'transaction_amounts' function to dataframe
#         visa_df["amount_transacted"] = visa_df.apply(transaction_amounts, axis=1)
#         # applies 'transaction_amounts' function to dataframe
#         visa_df["type_of_transaction"] = visa_df.apply(transaction_types, axis=1)
#
#         # deletes 'amount transacted in/out' columns as the values have been merged into one column while another column
#         # was created to determine the in or out status of each transaction
#         del visa_df['amount_transacted_out'], visa_df['amount_transacted_in'], visa_df['card_number']
#
#         # visa_df = visa_df.drop(visa_df[visa_df['transaction_information'] == 'PAYMENT THANK YOU/PAIEMEN T MERCI'].index)
#
#         visa_df["transaction_category"] = visa_df.apply(visa_transaction_category, axis=1)
#
#     elif os.path.exists('data/savings.csv'):
#         savings_read_file = pd.read_csv('data/savings.csv', header=None)
#         savings_df = pd.DataFrame(savings_read_file)
#         savings_df.columns = ['date_of_transaction', 'transaction_information', 'amount_transacted_out',
#                               'amount_transacted_in']
#
#         savings_df['date_of_transaction'] = pd.to_datetime(savings_df.date_of_transaction).dt.normalize()
#
#         savings_df["amount_transacted"] = savings_df.apply(transaction_amounts, axis=1)
#         savings_df["type_of_transaction"] = savings_df.apply(transaction_types, axis=1)
#
#         del savings_df['amount_transacted_out']
#         del savings_df['amount_transacted_in']
#
#         savings_df["transaction_category"] = savings_df.apply(savings_transaction_category, axis=1)
#
#         return visa_df, savings_df


# def print_to_files(visa_df, savings_df):
#     visa_df.to_csv('data/updated_visa.csv', encoding='utf-8', index=False)
#     savings_df.to_csv('data/updated_savings.csv', encoding='utf-8', index=False)
#
#     visa_df.to_json('data/updated_visa.json', orient="records", lines=True)
#     savings_df.to_json('data/updated_savings.json', orient="records", lines=True)
#
#     visa_df.to_parquet('data/updated_visa.parquet', compression='gzip')
#     savings_df.to_parquet('data/updated_savings.parquet', compression='gzip')
#
#     visa_df.to_excel('data/updated_visa.xlsx', index=False)
#     savings_df.to_excel('data/updated_savings.xlsx', index=False)


def visa_print_to_files(visa_df):
    if os.path.exists('data/visa.csv'):
        visa_df.to_csv('data/updated_visa.csv', encoding='utf-8', index=False)
        visa_df.to_json('data/updated_visa.json', orient="records", lines=True)
        visa_df.to_parquet('data/updated_visa.parquet', compression='gzip')
        visa_df.to_excel('data/updated_visa.xlsx', index=False)


def savings_print_to_files(savings_df):
    if os.path.exists('data/savings.csv'):
        savings_df.to_csv('data/updated_savings.csv', encoding='utf-8', index=False)
        savings_df.to_json('data/updated_savings.json', orient="records", lines=True)
        savings_df.to_parquet('data/updated_savings.parquet', compression='gzip')
        savings_df.to_excel('data/updated_savings.xlsx', index=False)


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