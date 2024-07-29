import streamlit as st
import sqlite3
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

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
    except Exception as e:
        st.error(f"테이블 생성 또는 데이터 가져오기 중 오류 발생: {str(e)}")

# Function to fetch transactions based on the inquiry
def fetch_transactions(inquiry):
    conn = sqlite3.connect('history.db', check_same_thread=False)
    if inquiry == "CustomerNumber = 'ALL'" or inquiry == "CustomerNumber = '*'":
        query = "SELECT * FROM transactions_Payment ORDER BY InvoiceDate DESC"
    else:
        query = f"SELECT * FROM transactions_Payment WHERE {inquiry} ORDER BY InvoiceDate DESC"
    transactions = pd.read_sql_query(query, conn)
    conn.close()
    
    # Convert CustomerNumber to string and remove commas
    transactions['CustomerNumber'] = transactions['CustomerNumber'].astype(str).str.replace(',', '')
        
    transactions.index = transactions.index + 1  # Change index to start from 1
    return transactions

# Function to plot bar chart of PaymentTime hours
def plot_hourly_distribution(transactions):
    # Extract hours from PaymentTime
    transactions['Hour'] = pd.to_datetime(transactions['PaymentTime']).dt.hour
    
    # Count occurrences of each hour
    hour_counts = transactions['Hour'].value_counts().sort_index()

    # Create bar chart
    fig, ax = plt.subplots(figsize=(6, 6))  # 크기를 동일하게 설정
    ax.bar(hour_counts.index, hour_counts.values, width=0.8)
    ax.set_xlabel('Hour')
    ax.set_ylabel('Number of Payments')
    ax.set_title('Payment Trend')
    ax.set_xticks(range(0, 24))
    st.pyplot(fig)

    # Return the hour with the maximum count
    max_hour = hour_counts.idxmax()
    max_count = hour_counts.max()
    return max_hour, max_count

# Function to plot KDE plot of Payment Date Differences
def plot_kde_differences(transactions):
    # Compute the difference between DueDate and PaymentDate
    transactions['PaymentDate'] = pd.to_datetime(transactions['PaymentTime']).dt.date
    transactions['DueDate'] = pd.to_datetime(transactions['DueDate'])
    transactions['PaymentDate'] = pd.to_datetime(transactions['PaymentDate'])
    transactions['Difference'] = (transactions['PaymentDate'] - transactions['DueDate']).dt.days

    # Filter differences between -30 and 0
    filtered_df = transactions[(transactions['Difference'] >= -30) & (transactions['Difference'] <= 0)]

    # KDE plot (with histogram)
    fig, ax = plt.subplots(figsize=(6, 6))  # 크기를 동일하게 설정
    sns.histplot(filtered_df['Difference'], kde=True, color='purple', ax=ax)
    ax.set_title('KDE Plot of Payment Date Differences (-30 to 0)')
    ax.set_xlabel('Difference (days)')
    st.pyplot(fig)

    # Find the mode of the difference (most frequent value range)
    mode_difference = filtered_df['Difference'].mode().values[0]

    return mode_difference

# Initialize Streamlit app
def main():
    st.title('Text-To-SQL : Payment Trend')

    st.markdown("""
        Welcome to Text-To-SQL.  
        Here, you can inquire about various aspects of Payment Trend.  
        Use Example Inquiries to refer to the question format.  
        
        **Important** : Modify the parts marked with **''** to get the answers you want.  
        The system operates by converting your text inquiries into SQL statements and matching them with linked data in the repository to respond.  

        **Note: This prompt uses fictional data, and the customer and invoice information used are fictitious creations.**
    """)

    # 테이블을 생성하고 데이터를 가져오는 함수 호출
    create_table_from_csv()

    # 예제 질의 섹션
    example_inquiries = [
        "CustomerNumber = '843937'",
        "CustomerNumber = 'ALL'",
    ]
    
    st.markdown("**Example Inquiries:**")
    selected_inquiry = st.selectbox("Select an inquiry example:", example_inquiries)

    st.markdown("""
        CustomerNumber : 843937, 553924, 496375, 609764, 603966, 404658, 955732, 926432, 850024, 949725
    """)

    # 질의 제출 양식
    inquiry = st.text_input('Submit an Inquiry:', selected_inquiry)

    # 질의에 따른 트랜잭션 테이블 표시
    if st.button('Submit'):
        try:
            transactions = fetch_transactions(inquiry)
            if not transactions.empty:
                # 왼쪽과 오른쪽에 나란히 차트를 표시
                col1, col2 = st.columns(2)

                with col1:
                    max_hour, max_count = plot_hourly_distribution(transactions)

                    # 텍스트 결과 출력 (회색 배경의 텍스트 박스)
                    result_message_bar = f"""
                    <div style="background-color: #F0F2F6; padding: 10px; border-radius: 5px; margin-top: 10px;">
                    The hour with the highest count is {max_hour} o'clock, with a total of {max_count} transactions.<br>
                    Therefore, it is recommended to contact the customer if payment is not confirmed by {max_hour} o'clock.
                    </div>
                    """
                    st.markdown(result_message_bar, unsafe_allow_html=True)

                with col2:
                    mode_difference = plot_kde_differences(transactions)

                    # 텍스트 결과 출력 (회색 배경의 텍스트 박스)
                    result_message_kde = f"""
                    <div style="background-color: #F0F2F6; padding: 10px; border-radius: 5px; margin-top: 10px;">
                    The most frequent range of differences is {mode_difference} days.<br>
                    Generally, the difference between the due date and payment date is less than 0.<br>
                    Therefore, it can be observed that this customer tends to pay before the due date.
                    </div>
                    """
                    st.markdown(result_message_kde, unsafe_allow_html=True)

                st.markdown("**Filtered Transactions:**")
                st.dataframe(transactions.drop(columns=['PaymentDate']))
            else:
                st.markdown("**There are no transactions for the given inquiry.**")
        except Exception as e:
            st.markdown(f"**오류 발생:** {str(e)}")

if __name__ == '__main__':
    main()

st.caption(f"© Made by Korea AR Team for SharkTank 2024. All rights reserved.")
