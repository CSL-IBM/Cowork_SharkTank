import streamlit as st
import sqlite3
import pandas as pd
import csv

st.set_page_config(layout="wide")

# Function to create SQLite table and import data from CSV
def create_table_from_csv():
    conn = sqlite3.connect('history.db')
    c = conn.cursor()

    # Read data from CSV and dynamically create table
    with open('/mnt/data/transactions_EngageAR&Contract.csv', 'r', newline='', encoding='utf-8') as csvfile:
        csvreader = csv.reader(csvfile)
        header = next(csvreader)  # Read header
        print(f"CSV Header: {header}")  # 출력하여 확인
        columns = ', '.join([f"{col} TEXT" for col in header])
        
        # Create table dynamically based on CSV header
        c.execute(f'''CREATE TABLE IF NOT EXISTS transactions ({columns})''')

        # Insert CSV data into the table
        for row in csvreader:
            placeholders = ', '.join(['?' for _ in row])
            c.execute(f'INSERT INTO transactions VALUES ({placeholders})', row)
    
    conn.commit()
    conn.close()
    return header

# Call the function to create the table and import data
header = create_table_from_csv()

# Function to fetch transactions based on the inquiry
def fetch_transactions(inquiry):
    conn = sqlite3.connect('history.db', check_same_thread=False)
    query = f"SELECT * FROM transactions WHERE {inquiry} ORDER BY InvoiceDate DESC"
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
            st.markdown("**Filtered Transactions:**")
            st.dataframe(transactions)
        except Exception as e:
            st.markdown(f"**Error occurred:** {str(e)}")

if __name__ == '__main__':
    main()
