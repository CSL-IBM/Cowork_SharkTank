import streamlit as st
import sqlite3
import pandas as pd
import csv
import re

st.set_page_config(layout="wide")

# 명시적으로 CSV 파일의 열 이름을 지정합니다.
header = [
    "Category", "CustomerName", "CustomerNumber", "InvoiceNumber", 
    "InvoiceAmount", "InvoiceDate", "DueDate", "ForecastCode", 
    "ForecastDate", "Collector", "ContractNo", "Link"
]

# Function to create SQLite table and import data from CSV
def create_table_from_csv():
    conn = sqlite3.connect('history.db')
    c = conn.cursor()

    # Drop the table if it exists to avoid schema mismatch
    c.execute('DROP TABLE IF EXISTS transactions_EngageAR_Contract')

    # Create table dynamically based on specified header
    columns = ', '.join([f"{col} TEXT" for col in header])
    c.execute(f'''CREATE TABLE IF NOT EXISTS transactions_EngageAR_Contract ({columns})''')

    # Read data from CSV and insert into table
    with open('transactions_EngageAR_Contract.csv', 'r', newline='', encoding='utf-8') as csvfile:
        csvreader = csv.reader(csvfile)
        next(csvreader)  # Skip header in the CSV file
        
        # Insert CSV data into the table
        for row in csvreader:
            if len(row) == len(header):
                placeholders = ', '.join(['?' for _ in row])
                try:
                    c.execute(f'INSERT INTO transactions_EngageAR_Contract VALUES ({placeholders})', row)
                except sqlite3.OperationalError as e:
                    st.write(f"Error inserting row: {row}")
                    st.write(e)
            else:
                st.write(f"Row length mismatch: {row}")
                raise ValueError("Number of columns in the row does not match the header length.")
    
    conn.commit()
    conn.close()

# Call the function to create the table and import data
create_table_from_csv()

# Function to convert natural language inquiry into SQL condition
def convert_to_sql_condition(natural_language_query):
    # Define regex patterns for different types of queries
    equality_pattern = re.compile(r"show the transactions where the '(\w+)' is '(\w+)'", re.IGNORECASE)
    greater_than_pattern = re.compile(r"show the transactions where the '(\w+)' is greater than '(\w+)'", re.IGNORECASE)
    date_greater_than_pattern = re.compile(r"show the transactions where the '(\w+)' is greater than DATE\('now'\)", re.IGNORECASE)
    date_literal_pattern = re.compile(r"show the transactions where the '(\w+)' is greater than '(\d{4}-\d{2}-\d{2})'", re.IGNORECASE)
    group_by_pattern = re.compile(r"show the transactions where the '(\w+)' is '(\w+)' GROUP BY (\w+)", re.IGNORECASE)
    and_condition_pattern = re.compile(r"show the transactions where (.+)", re.IGNORECASE)
    forecast_date_vs_due_date_pattern = re.compile(r"show the transactions where the '(\w+)' is '(\w+)' and the '(\w+)' is greater than '(\w+)'", re.IGNORECASE)
    forecast_date_vs_due_date_column_pattern = re.compile(r"show the transactions where the '(\w+)' is greater than '(\w+)'", re.IGNORECASE)
    show_all_pattern = re.compile(r"show all transactions|show the transactions", re.IGNORECASE)

    print(f"Processing query: {natural_language_query}")

    # Match the query with patterns and convert to SQL condition
    if show_all_pattern.match(natural_language_query):
        print("Generating SQL condition for showing all transactions")
        return ""  # No WHERE clause needed for showing all transactions
    elif forecast_date_vs_due_date_pattern.match(natural_language_query):
        matches = forecast_date_vs_due_date_pattern.findall(natural_language_query)
        print(f"Forecast vs Due Date Matches: {matches}")
        if matches:
            try:
                column1, value1, column2, value2 = matches[0]
                sql_condition = f"{column1} = '{value1}' AND {column2} > {value2}"
                print(f"Generated SQL Condition: {sql_condition}")
                return sql_condition
            except ValueError as e:
                print(f"Error parsing query: {e}")
                return f"Error parsing query: {e}"
    elif forecast_date_vs_due_date_column_pattern.match(natural_language_query):
        matches = forecast_date_vs_due_date_column_pattern.findall(natural_language_query)
        print(f"Forecast Date vs Due Date Column Matches: {matches}")
        if matches:
            try:
                column1, column2 = matches[0]
                sql_condition = f"{column1} > {column2}"
                print(f"Generated SQL Condition: {sql_condition}")
                return sql_condition
            except ValueError as e:
                print(f"Error parsing query: {e}")
                return f"Error parsing query: {e}"
    elif and_condition_pattern.match(natural_language_query):
        conditions_str = and_condition_pattern.findall(natural_language_query)[0]
        print(f"Conditions String: {conditions_str}")
        conditions = [cond.strip() for cond in conditions_str.split('and')]
        sql_conditions = []
        for condition in conditions:
            if "greater than" in condition:
                match = re.search(r"'(\w+)' is greater than '(\d{4}-\d{2}-\d{2})'", condition, re.IGNORECASE)
                if match:
                    column, value = match.groups()
                    sql_conditions.append(f"{column} > '{value}'")
                else:
                    print(f"Error matching greater than condition: {condition}")
            elif "is" in condition:
                match = re.search(r"'(\w+)' is '(\w+)'", condition, re.IGNORECASE)
                if match:
                    column, value = match.groups()
                    sql_conditions.append(f"{column} = '{value}'")
                else:
                    print(f"Error matching equality condition: {condition}")
            else:
                return f"Unrecognized condition format: {condition}"
        sql_condition = " AND ".join(sql_conditions)
        print(f"Generated SQL Condition: {sql_condition}")
        return sql_condition
    elif equality_pattern.match(natural_language_query):
        column, value = equality_pattern.findall(natural_language_query)[0]
        sql_condition = f"{column} = '{value}'"
        print(f"Generated SQL Condition: {sql_condition}")
        return sql_condition
    elif greater_than_pattern.match(natural_language_query):
        column, value = greater_than_pattern.findall(natural_language_query)[0]
        sql_condition = f"{column} > '{value}'"
        print(f"Generated SQL Condition: {sql_condition}")
        return sql_condition
    elif date_greater_than_pattern.match(natural_language_query):
        column = date_greater_than_pattern.findall(natural_language_query)[0]
        sql_condition = f"{column} > DATE('now')"
        print(f"Generated SQL Condition: {sql_condition}")
        return sql_condition
    elif date_literal_pattern.match(natural_language_query):
        column, date = date_literal_pattern.findall(natural_language_query)[0]
        sql_condition = f"{column} > '{date}'"
        print(f"Generated SQL Condition: {sql_condition}")
        return sql_condition
    elif group_by_pattern.match(natural_language_query):
        column, value, group_by = group_by_pattern.findall(natural_language_query)[0]
        sql_condition = f"{column} = '{value}' GROUP BY {group_by}"
        print(f"Generated SQL Condition: {sql_condition}")
        return sql_condition
    else:
        print(f"Unrecognized query format: {natural_language_query}")
        return f"Unrecognized query format: {natural_language_query}"  # Fallback to return the original query if it doesn't match

# Function to fetch transactions based on the inquiry
def fetch_transactions(inquiry):
    conn = sqlite3.connect('history.db', check_same_thread=False)
    
    if inquiry:  # If there is an inquiry condition
        query = f"SELECT * FROM transactions_EngageAR_Contract WHERE {inquiry} ORDER BY InvoiceDate DESC"
    else:  # If no inquiry condition
        query = "SELECT * FROM transactions_EngageAR_Contract ORDER BY InvoiceDate DESC"
    
    transactions = pd.read_sql_query(query, conn)
    conn.close()
    return transactions

# Main function to handle Streamlit UI
def main():
    st.title("Transaction Inquiry System")

    # Input for natural language query
    natural_language_inquiry = st.text_input("Enter your inquiry:", "")

    # Convert natural language to SQL condition
    sql_condition = convert_to_sql_condition(natural_language_inquiry)
    
    # Fetch transactions based on the SQL condition
    transactions = fetch_transactions(sql_condition)
    
    # Display transactions
    st.write(transactions)

if __name__ == "__main__":
    main()
