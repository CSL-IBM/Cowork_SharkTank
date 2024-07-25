import streamlit as st
import sqlite3
import pandas as pd
import matplotlib.pyplot as plt

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
        st.success("테이블이 생성되고 데이터가 성공적으로 가져왔습니다.")
    except Exception as e:
        st.error(f"테이블 생성 또는 데이터 가져오기 중 오류 발생: {str(e)}")

# Function to fetch transactions based on the inquiry
def fetch_transactions(inquiry):
    conn = sqlite3.connect('history.db', check_same_thread=False)
    query = f"SELECT * FROM transactions_Payment WHERE {inquiry} ORDER BY InvoiceDate DESC"
    transactions = pd.read_sql_query(query, conn)
    conn.close()
    return transactions

# Function to plot bar chart of PaymentTime hours
def plot_hourly_distribution(transactions):
    # Extract hours from PaymentTime
    transactions['Hour'] = pd.to_datetime(transactions['PaymentTime']).dt.hour
    
    # Count occurrences of each hour
    hour_counts = transactions['Hour'].value_counts().sort_index()

    # Create bar chart
    plt.figure(figsize=(10, 6))
    plt.bar(hour_counts.index, hour_counts.values, width=0.8)
    plt.xlabel('Hour of Day')
    plt.ylabel('Number of Payments')
    plt.title('Number of Payments by Hour of Day')
    plt.xticks(range(0, 24))
    st.pyplot(plt)

# Initialize Streamlit app
def main():
    st.title('Text-To-Watsonx : Engage AR')

    st.markdown("""
        Text-To-Watsonx : Engage AR에 오신 것을 환영합니다.
        여기서 Engage AR 트랜잭션에 대해 다양한 사항을 문의할 수 있습니다.
        예제 질의를 사용하여 질문 형식을 참고하세요.
        **중요: AI 응답은 다양할 수 있으며, 더 나은 결과를 위해 프롬프트 템플릿이나 LLM을 미세 조정해야 할 수도 있습니다.**
    """)

    # 테이블을 생성하고 데이터를 가져오는 함수 호출
    create_table_from_csv()

    # 예제 질의 섹션
    example_inquiries = [
        "CustomerNumber = '843937'",
    ]
    
    st.markdown("**예제 질의:**")
    selected_inquiry = st.selectbox("예제 질의를 선택하세요:", example_inquiries)

    # 질의 제출 양식
    inquiry = st.text_input('질의를 제출하세요:', selected_inquiry)

    # 질의에 따른 트랜잭션 테이블 표시
    if st.button('제출'):
        try:
            transactions = fetch_transactions(inquiry)
            if not transactions.empty:
                st.markdown("**필터링된 트랜잭션:**")
                st.dataframe(transactions)

                # 시간대별 결제 수를 시각화
                plot_hourly_distribution(transactions)
            else:
                st.markdown("**주어진 질의에 대한 트랜잭션이 없습니다.**")
        except Exception as e:
            st.markdown(f"**오류 발생:** {str(e)}")

if __name__ == '__main__':
    main()
