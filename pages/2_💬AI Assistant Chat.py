import streamlit as st
import sqlite3
import pandas as pd
import csv

st.set_page_config(layout="wide")

# Function to create SQLite table and import data from CSV
def create_table_from_csv():
    conn = sqlite3.connect('history.db')
    c = conn.cursor()
    
    # Create the transactions table if it doesn't exist
    c.execute('''CREATE TABLE IF NOT EXISTS transactions (
                 Category TEXT,
                 CustomerName TEXT,
                 CustomerNumber INTEGER,
                 InvoiceNumber TEXT,
                 InvoiceAmount TEXT,
                 InvoiceDate TEXT,
                 DueDate TEXT,
                 ForecastCode TEXT,
                 ForecastDate TEXT,
                 Collector TEXT
                 )''')

    # Read data from CSV and insert into SQLite table
    with open('transactions.csv', 'r', newline='', encoding='utf-8') as csvfile:
        csvreader = csv.reader(csvfile)
        next(csvreader)  # Skip header
        for row in csvreader:
            c.execute('INSERT INTO transactions VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)', row)
    
    conn.commit()
    conn.close()

# Call the function to create the table and import data
create_table_from_csv()

# Connect to SQLite database
def get_db_connection():
    conn = sqlite3.connect('history.db', check_same_thread=False)
    return conn

# Function to fetch transactions from database
def fetch_transactions():
    conn = get_db_connection()
    cursor = conn.execute('SELECT DISTINCT * FROM transactions ORDER BY InvoiceDate DESC')
    transactions = cursor.fetchall()
    conn.close()

    # Convert fetched data into DataFrame
    df = pd.DataFrame(transactions, columns=['Category', 'CustomerName', 'CustomerNumber', 'InvoiceNumber', 'InvoiceAmount',
                                             'InvoiceDate', 'DueDate', 'ForecastCode', 'ForecastDate', 'Collector'])
    # Add 1 to index to make it 1-based
    df.index = df.index + 1

    return df

# Initialize Streamlit app
def main():
    st.title('Text-To-Watsonx : Engage AR')

    # Introduction section
    st.markdown("""
        Welcome to the Text-To-Watsonx : Engage AR.
        Here, you can inquire about various aspects of Engage AR transactions.
        Use the example queries as a guide to format your questions.
        **Important: AI responses can vary, you might need to fine-tune your prompt template or LLM for improved results.**
    """)

    # Example inquiries section
    example_inquiries = [
        "What are the items with a due date after today?",
        "Show me the list where the collector is Lisa and the category is Yellow!",
        "Show me the list where the collector is David and the forecast code is AUTO!",
        "Show me the list where the collector is John and the forecast date is after August!",
        "How many AUTO in Forecastcode per collector?",
        "How many invoice numbers with due date greater than August 10th 2024?",
        "How many green per collector in category?"
    ]
    
    st.markdown("**Example Inquiries:**")
    selected_inquiry = st.selectbox("Select an inquiry example:", example_inquiries)

    # Form for inquiry submission
    inquiry = st.text_input('Submit an Inquiry:', selected_inquiry)

    if st.button('Submit'):
        conn = get_db_connection()
        try:
            # Construct SQL query based on the inquiry text
            query = f"SELECT * FROM transactions WHERE {inquiry} ORDER BY InvoiceDate DESC"
            cursor = conn.execute(query)
            response = cursor.fetchall()
            st.markdown(f"**Response:**")
            st.write(response)
        except Exception as e:
            st.markdown(f"**Error occurred:** {str(e)}")
        finally:
            conn.close()

    # Display transactions table using Pandas DataFrame
    st.markdown("**Transactions:**")
    transactions = fetch_transactions()
    st.dataframe(transactions)

    # Custom CSS for table styling
    st.markdown(
        """
        <style>
        table.dataframe {
            border: 2px solid #5e5e5e; /* Darker gray than default */
            text-align: center; /* Center align text in cells */
        }
        th {
            border: 2px solid #5e5e5e; /* Darker gray than default */
            text-align: center; /* Center align text in header cells */
        }
        td {
            border: 2px solid #5e5e5e; /* Darker gray than default */
            text-align: center; /* Center align text in data cells */
        }
        </style>
        """,
        unsafe_allow_html=True
    )

if __name__ == '__main__':
    main()
