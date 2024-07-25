import streamlit as st
import sqlite3
import pandas as pd

st.set_page_config(layout="wide")

# Function to create table and import data from CSV
def create_table_from_csv():
    try:
        # Load data from the uploaded CSV file
        df = pd.read_csv('transactions_Payment.csv')

         # Only select necessary columns to avoid unnamed columns
        df = df[['CustomerNumber', 'CustomerName', 'InvoiceNumber', 'InvoiceAmount', 'InvoiceDate', 'DueDate', 'PaymentTime', 'RepNo']]

        
        # Connect to SQLite database
        conn = sqlite3.connect('history.db', check_same_thread=False)
        cursor = conn.cursor()

        # Create table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS transactions_Payment (
                CustomerNumber TEXT,
                CustomerName TEXT,
                InvoiceNumber TEXT,
                InvoiceAmount REAL,
                InvoiceDate TEXT,
                DueDate TEXT,
                PaymentTime TEXT,
                RepNo TEXT
            )
        ''')

        # Import data into the table
        df.to_sql('transactions_Payment', conn, if_exists='replace', index=False)

        # Close the connection
        conn.close()
        st.success("Table created and data imported successfully.")
    except Exception as e:
        st.error(f"Error creating table or importing data: {str(e)}")

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

    # Call the function to create the table and import data
    create_table_from_csv()

    # Example inquiries section
    example_inquiries = [
        "CustomerNumber = '843937'",
    ]
    
    st.markdown("**Example Inquiries:**")
    selected_inquiry = st.selectbox("Select an inquiry example:", example_inquiries)

    # Form for inquiry submission
    inquiry = st.text_input('Submit an Inquiry:', selected_inquiry)

    # Display transactions table based on the inquiry
    if st.button('Submit'):
        try:
            transactions = fetch_transactions(inquiry)
            if not transactions.empty:
                st.markdown("**Filtered Transactions:**")
                st.dataframe(transactions)
            else:
                st.markdown("**No transactions found for the given inquiry.**")
        except Exception as e:
            st.markdown(f"**Error occurred:** {str(e)}")

if __name__ == '__main__':
    main()
