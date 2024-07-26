import streamlit as st
import sqlite3
import pandas as pd
import matplotlib.pyplot as plt

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
        #st.success("테이블이 생성되고 데이터가 성공적으로 가져왔습니다.")
    #except Exception as e:
        #st.error(f"테이블 생성 또는 데이터 가져오기 중 오류 발생: {str(e)}")

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
    fig, ax = plt.subplots(figsize=(6, 3))  # 크기를 조정함
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
    
    st.markdown("**예제 질의:**")
    selected_inquiry = st.selectbox("예제 질의를 선택하세요:", example_inquiries)

    st.markdown("""
        CustomerNumber : 843937, 553924, 496375, 609764, 603966, 404658, 955732, 926432, 850024, 949725
    """)

    # 질의 제출 양식
    inquiry = st.text_input('질의를 제출하세요:', selected_inquiry)

    # 질의에 따른 트랜잭션 테이블 표시
    if st.button('제출'):
        try:
            transactions = fetch_transactions(inquiry)
            if not transactions.empty:
                max_hour, max_count = plot_hourly_distribution(transactions)

                # 텍스트 결과 출력 (회색 배경의 텍스트 박스)
                result_message = f"가장 많은 count를 가진 Hour는 {max_hour}시이며, 총 건수는 {max_count}건 입니다. 따라서, {max_hour}시까지 대금 지급이 확인되지 않는 경우에는 고객에게 contact 하시는 것을 추천드립니다."
                st.markdown(f'<div style="background-color: #F0F2F6; padding: 10px; border-radius: 5px;">{result_message}</div>', unsafe_allow_html=True)
                
                st.markdown("**필터링된 트랜잭션:**")
                st.dataframe(transactions)
            else:
                st.markdown("**주어진 질의에 대한 트랜잭션이 없습니다.**")
        except Exception as e:
            st.markdown(f"**오류 발생:** {str(e)}")

if __name__ == '__main__':
    main()

st.caption(f"© Made by Korea AR Team for SharkTank 2024. All rights reserved.")
