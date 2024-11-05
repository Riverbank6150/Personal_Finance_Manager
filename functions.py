from expense_tracker import *
import pandas as pd
import csv
from typing import List


def __init_visa_dict():
    categories_dict = {}
    with open('visa_transaction_mapping.csv', mode='r') as file:
        reader = csv.DictReader(file)
        for row in reader:
            categories_dict[row['transaction_info']] = row['transaction_category']

    return categories_dict


visa_categories_dict = __init_visa_dict()


def __init_savings_dict():
    categories_dict = {}
    with open('savings_transaction_mapping.csv', mode='r') as file:
        reader = csv.DictReader(file)
        for row in reader:
            categories_dict[row['transaction_info']] = row['transaction_category']

    return categories_dict


savings_categories_dict = __init_savings_dict()


# function to have the original bank transaction csv file 'amount transacted in/out' columns put together in one
# single 'transaction amount' dataframe column
def transaction_amounts(row):
    if pd.isnull(row['amount_transacted_out']):
        return row['amount_transacted_in']
    elif pd.notnull(row['amount_transacted_out']):
        return row['amount_transacted_out']


# function to create new dataframe column to determine what kind of transaction (in or out) to be used alongside new
# singular 'transaction amount' dataframe column
def transaction_types(row):
    if pd.isnull(row['amount_transacted_out']):
        return 'in'
    elif pd.notnull(row['amount_transacted_out']):
        return 'out'


# function to categorize each transaction
def visa_transaction_category(transaction_info):
    for key, value in visa_categories_dict.items():
        if key in transaction_info['transaction_information'].upper():
            return value
    return 'UNCATEGORIZED'


def savings_transaction_category(transaction_info):
    for key, value in savings_categories_dict.items():
        if key in transaction_info['transaction_information'].upper():
            return value
    return 'UNCATEGORIZED'


def visa_dataframe_time_grouping(visa_df):
    visa_df['week_of_transaction'] = visa_df['date_of_transaction'].strftime('%Y-W%V')
    visa_df['month_of_transaction'] = visa_df['date_of_transaction'].strftime('%Y-%m')
    visa_df['quarter_of_transaction'] = visa_df['date_of_transaction'].to_period('Q').strftime('%Y-Q%q')
    visa_df['year_of_transaction'] = visa_df['date_of_transaction'].strftime('%Y')

    return visa_df


def savings_dataframe_time_grouping(savings_df):
    savings_df['week_of_transaction'] = savings_df['date_of_transaction'].strftime('%Y-W%V')
    savings_df['month_of_transaction'] = savings_df['date_of_transaction'].strftime('%Y-%m')
    savings_df['quarter_of_transaction'] = savings_df['date_of_transaction'].to_period('Q').strftime('%Y-Q%q')
    savings_df['year_of_transaction'] = savings_df['date_of_transaction'].strftime('%Y')

    return savings_df


def visa_dataframe_summation(visa_df):
    visa_df['daily_sum'] = visa_df.groupby(['date_of_transaction', 'type_of_transaction', 'transaction_category'])[
        'amount_transacted'].transform('sum')

    visa_df['monthly_sum'] = visa_df.groupby(['month_of_transaction', 'type_of_transaction', 'transaction_category'])[
        'amount_transacted'].transform('sum')

    return visa_df


def savings_dataframe_summation(savings_df):
    return 0


def filtered_visa_dataframe(visa_df):
    # gives only the values from 2024
    filtered_visa_df = visa_df.loc[(visa_df['date_of_transaction'] >= '2024-1-1',)]

    # drops rows that have "credit card payment" as the transaction category value to avoid redundancy in plots
    filtered_visa_df = filtered_visa_df.drop(
        filtered_visa_df[filtered_visa_df['transaction_category'] == 'CREDIT CARD PAYMENT'].index)

    return filtered_visa_df


def filtered_savings_dataframe(Savings_df):
    return 0
