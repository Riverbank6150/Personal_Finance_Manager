from expense_tracker import *


def expense_tracker():
    # bank_statements_extraction()

    csv_to_dataframe()

    visa_df = visa_csv_to_dataframe()
    savings_df = savings_csv_to_dataframe()

    print_to_files(visa_df, savings_df)
    # savings_balance(visa_df, savings_df)

    # transaction_category(df)
    # spending_category(df)

    # result = bank_transactions_to_database_transformation(visa_df, savings_df)
    # transaction_to_visualization_tool_load_from_sql(result)

    # transaction_to_visualization_tool_load_from_df(visa_df, savings_df)


if __name__ == '__main__':
    expense_tracker()