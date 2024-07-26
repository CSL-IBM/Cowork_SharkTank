import streamlit as st
import sqlite3
import pandas as pd
import csv

st.set_page_config(layout="wide")

# 명시적으로 CSV 파일의 열 이름을 지정합니다.
header = [
    "No", "Category", "CustomerName", "CustomerNumber", "InvoiceNumber", 
    "InvoiceAmount", "InvoiceDate", "DueDate", "ForecastCode", 
    "ForecastDate", "Collector", "ContractNo", "Link"
]

# Function to create SQLite table and import data from CSV
def create_table_from_csv():
    conn = sqlite3.connect('history.db')
    c = conn.cursor()

    # Create table dynamically based on specified header
    columns = ', '.join([f"{col} TEXT" for col in header])
    c.execute(f'''CREATE TABLE IF NOT EXISTS transactions_EngageAR_Contract ({columns})''')

    # Read data from CSV and insert into table
    with open('transactions_EngageAR_Contract.csv', 'r', newline='', encoding='utf-8') as csvfile:
        csvreader = csv.reader(csvfile)
        next(csvreader)  # Skip header in the CSV file
        
        # Insert CSV data into the table
        row_count = 0
        for row in csvreader:
            if len(row) == len(header):
                placeholders = ', '.join(['?' for _ in row])
                c.execute(f'INSERT INTO transactions_EngageAR_Contract VALUES ({placeholders})', row)
                row_count += 1
            else:
                raise ValueError("Number of columns in the row does not match the header length.")
        
        if row_count != 200:
            raise ValueError(f"Expected 200 lines of data, but got {row_count}.")
    
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
        "Category = 'Green' GROUP BY Collector",
        "InvoiceNumber = 'GP9904'"
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
            st.dataframe(transactions, use_container_width=True)
            
            if "InvoiceNumber" in inquiry:
                if not transactions.empty:
                    link = transactions.iloc[0]['Link']
                    st.markdown(f"**InvoiceNumber: {transactions.iloc[0]['InvoiceNumber']}**")
                    st.markdown(f"[Click here to open link]({link})")
                else:
                    st.markdown("No results found for the given InvoiceNumber.")
        except Exception as e:
            st.markdown(f"**Error occurred:** {str(e)}")

if __name__ == '__main__':
    main()
