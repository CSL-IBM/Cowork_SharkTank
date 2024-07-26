import streamlit as st
import sqlite3
import pandas as pd
import csv

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
        Important: Modify the parts marked with '' to get the answers you want.
        The system operates by converting your text inquiries into SQL statements and matching them with linked data in the repository to respond.
        **Note: This prompt uses fictional data, and the customer and invoice information used are fictitious creations.**
    """)

    # Example inquiries section
    example_inquiries = [
        "DueDate > DATE('now')",
        "Collector = 'Lisa' AND Category = 'Yellow'",
        "Collector = 'David' AND ForecastCode = 'AUTO'",
        "Collector = 'John' AND ForecastDate > '2024-08-01'",
        "ForecastCode = 'AUTO' GROUP BY Collector",
        "DueDate > '2024-08-10'",
        "Category = 'Green' GROUP BY Collector"
    ]
    
    st.markdown("**Example Inquiries:**")
    selected_inquiry = st.selectbox("Select an inquiry example:", example_inquiries)

    # Form for inquiry submission
    inquiry = st.text_input('Submit an Inquiry:', selected_inquiry)

    # Display transactions table based on the inquiry
    if st.button('Submit'):
        try:
            transactions = fetch_transactions(inquiry)
            transactions.index = transactions.index + 1  # Change index to start from 1
            st.markdown("**Filtered Transactions:**")
            st.dataframe(transactions)
        except Exception as e:
            st.markdown(f"**Error occurred:** {str(e)}")

if __name__ == '__main__':
    main()

st.caption(f"© Made by Korea AR Team for SharkTank 2024. All rights reserved.")
