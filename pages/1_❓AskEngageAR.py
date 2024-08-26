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

    # Match the query with patterns and convert to SQL condition
    if forecast_date_vs_due_date_pattern.match(natural_language_query):
        matches = forecast_date_vs_due_date_pattern.findall(natural_language_query)
        if matches:
            column1, value1, column2 = matches[0]
            return f"{column1} = '{value1}' AND {column2} > {column2}"
    elif and_condition_pattern.match(natural_language_query):
        conditions_str = and_condition_pattern.findall(natural_language_query)[0]
        conditions = [cond.strip() for cond in conditions_str.split('and')]
        sql_conditions = []
        for condition in conditions:
            if "greater than" in condition:
                column, value = re.findall(r"'(\w+)' is greater than '(\d{4}-\d{2}-\d{2})'", condition, re.IGNORECASE)[0]
                sql_conditions.append(f"{column} > '{value}'")
            elif "is" in condition:
                column, value = re.findall(r"'(\w+)' is '(\w+)'", condition, re.IGNORECASE)[0]
                sql_conditions.append(f"{column} = '{value}'")
            else:
                return natural_language_query  # Fallback to return the original query if it doesn't match
        return " AND ".join(sql_conditions)
    elif equality_pattern.match(natural_language_query):
        column, value = equality_pattern.findall(natural_language_query)[0]
        return f"{column} = '{value}'"
    elif greater_than_pattern.match(natural_language_query):
        column, value = greater_than_pattern.findall(natural_language_query)[0]
        return f"{column} > '{value}'"
    elif date_greater_than_pattern.match(natural_language_query):
        column = date_greater_than_pattern.findall(natural_language_query)[0]
        return f"{column} > DATE('now')"
    elif date_literal_pattern.match(natural_language_query):
        column, date = date_literal_pattern.findall(natural_language_query)[0]
        return f"{column} > '{date}'"
    elif group_by_pattern.match(natural_language_query):
        column, value, group_by = group_by_pattern.findall(natural_language_query)[0]
        return f"{column} = '{value}' GROUP BY {group_by}"
    else:
        return natural_language_query  # Fallback to return the original query if it doesn't match



# Function to fetch transactions based on the inquiry
def fetch_transactions(inquiry):
    conn = sqlite3.connect('history.db', check_same_thread=False)
    query = f"SELECT * FROM transactions_EngageAR_Contract WHERE {inquiry} ORDER BY InvoiceDate DESC"
    transactions = pd.read_sql_query(query, conn)
    conn.close()
    return transactions

# Initialize Streamlit app
def main():
    st.title('Text-To-SQL : Engage AR')

    st.markdown("""
        Welcome to Text-To-SQL.  
        Here, you can inquire about various aspects of Engage AR transactions.  
        Use Example Inquiries to refer to the question format.  
        
        **Important** : Modify the parts marked with **''** to get the answers you want.  
        The system operates by converting your text inquiries into SQL statements and matching them with linked data in the repository to respond.  

        **Note: This prompt uses fictional data, and the customer and invoice information used are fictitious creations.**
    """)

    # Example inquiries section
    example_inquiries = [
        "Show the transactions where the 'Category' is 'Green'",
        "Show the transactions where the 'CustomerNumber' is '988587'",
        "Show the transactions where the 'InvoiceAmount' is greater than '50000000'",
        "Show the transactions where the 'ForecastCode' is 'AUTO'",
        "Show the transactions where the 'ForecastDate' is greater than DATE('now')",
        "Show the transactions where the 'DueDate' is greater than DATE('now')",
        "Show the transactions where the 'DueDate' is greater than '2024-08-10'",
        "Show the transactions where the 'Collector' is 'Lisa' and the 'Category' is 'Yellow'",
        "Show the transactions where the 'Collector' is 'David' and the 'ForecastCode' is 'AUTO'",
        "Show the transactions where the 'Collector' is 'John' and the 'ForecastDate' is greater than '2024-08-01'",
    ]
    
    st.markdown("**Example Inquiries:**")
    selected_inquiry = st.selectbox("Select an inquiry example:", example_inquiries)

    # Form for inquiry submission
    natural_language_inquiry = st.text_input('Submit an Inquiry:', selected_inquiry)

    # Convert the natural language inquiry to SQL condition
    sql_condition = convert_to_sql_condition(natural_language_inquiry)

    # Display transactions table based on the inquiry
    if st.button('Submit'):
        try:
            transactions = fetch_transactions(sql_condition)
            total_lines = len(transactions)  # Get the total number of lines
            transactions.index = transactions.index + 1  # Change index to start from 1
            line_text = "line" if total_lines == 1 else "lines"
            st.markdown(f"**Filtered Transactions: {total_lines} {line_text}**")  # Display the total number of lines
            st.dataframe(transactions)
        except Exception as e:
            st.markdown(f"**Error occurred:** {str(e)}")

if __name__ == '__main__':
    main()

st.caption(f"© Made by Korea AR Team for SharkTank 2024. All rights reserved.")
