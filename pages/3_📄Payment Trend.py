import streamlit as st
import sqlite3
import pandas as pd
import csv

st.set_page_config(layout="wide")

# 명시적으로 CSV 파일의 열 이름을 지정합니다.
header = [
    "No", "CustomerNumber", "CustomerName", "InvoiceNumber", 
    "InvoiceAmount", "InvoiceDate", "DueDate", "PaymentTime", "RepNo."
]

# Function to create SQLite table and import data from CSV
def create_table_from_csv():
    conn = sqlite3.connect('history.db')
    c = conn.cursor()

    # Create table dynamically based on specified header
    columns = ', '.join([f"{col} TEXT" for col in header])
    c.execute(f'''CREATE TABLE IF NOT EXISTS transactions_EngageAR_Contract ({columns})''')

    # Read data from CSV and insert into table
    with open('transactions_Payment.csv', 'r', newline='', encoding='utf-8') as csvfile:
        csvreader = csv.reader(csvfile)
        next(csvreader)  # Skip header in the CSV file
        
        # Insert CSV data into the table
        for row in csvreader:
            if len(row) == len(header):
                placeholders = ', '.join(['?' for _ in row])
                c.execute(f'INSERT INTO transactions_Payment VALUES ({placeholders})', row)
            else:
                raise ValueError("Number of columns in the row does not match the header length.")
    
    conn.commit()
    conn.close()

# Call the function to create the table and import data
create_table_from_csv()

# Function to fetch transactions based on the inquiry
def fetch_transactions(inquiry):
    conn = sqlite3.connect('history.db', check_same_thread=False)
    query = f"SELECT * FROM transactions_Payment WHERE {inquiry} ORDER BY InvoiceDate DESC"
    transactions = pd.read_sql_query(query, conn)
    conn.close()
    return transactions

# Initialize Streamlit app
def main():
    st.title('Text-To-Watsonx : Engage AR')

    st.markdown("""
        Welcome to the Text-To-Watsonx : Engage AR.
        Here, you can inquire about various aspects of Engage AR transactions.
        Use the example queries as a guide to format your questions.
        **Important: AI responses can vary, you might need to fine-tune your prompt template or LLM for improved results.**
    """)

    # Example inquiries section
    example_inquiries = [
        '"DueDate" > DATE("now")',
        '"CustomerName" = \'Lisa\' AND "CustomerNumber" = \'12345\'',
        '"CustomerName" = \'David\' AND "InvoiceAmount" > 500',
        '"CustomerName" = \'John\' AND "InvoiceDate" > \'2024-08-01\'',
        '"InvoiceAmount" > 1000 GROUP BY "CustomerName"',
        '"DueDate" > \'2024-08-10\'',
        '"CustomerNumber" = \'67890\' GROUP BY "CustomerName"'
    ]
    
    st.markdown("**Example Inquiries:**")
    selected_inquiry = st.selectbox("Select an inquiry example:", example_inquiries)

    # Form for inquiry submission
    inquiry = st.text_input('Submit an Inquiry:', selected_inquiry)

    # Display transactions table based on the inquiry
    if st.button('Submit'):
        try:
            transactions = fetch_transactions(inquiry)
            st.markdown("**Filtered Transactions:**")
            st.dataframe(transactions)
        except Exception as e:
            st.markdown(f"**Error occurred:** {str(e)}")

if __name__ == '__main__':
    main()
