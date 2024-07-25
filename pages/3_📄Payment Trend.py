import streamlit as st
import sqlite3
import pandas as pd
import csv

st.set_page_config(layout="wide")

# CSV 파일 헤더 정의
header = [
    "No", "CustomerNumber", "CustomerName", "InvoiceNumber", 
    "InvoiceAmount", "InvoiceDate", "DueDate", "PaymentTime", "RepNo."
]

# SQLite 테이블 생성 및 CSV 데이터 삽입 함수
def create_table_from_csv():
    conn = sqlite3.connect('history.db')
    c = conn.cursor()

    # 헤더를 기반으로 SQL 테이블 생성
    columns = ', '.join([f"{col} TEXT" for col in header])
    create_table_sql = f'CREATE TABLE IF NOT EXISTS transactions_Payment ({columns})'
    c.execute(create_table_sql)

    # CSV 파일에서 데이터 읽어 테이블에 삽입
    with open('transactions_Payment.csv', 'r', newline='', encoding='utf-8') as csvfile:
        csvreader = csv.reader(csvfile)
        csv_header = next(csvreader)  # CSV 헤더 읽기

        # 디버깅: CSV 헤더와 정의된 헤더 출력
        st.write("CSV Header:", csv_header)
        st.write("Expected Header:", header)

        # 헤더의 공백 제거
        csv_header = [col.strip() for col in csv_header]
        header = [col.strip() for col in header]

        if csv_header != header:
            raise ValueError("CSV header does not match the defined header.")

        # CSV 데이터를 테이블에 삽입
        for row in csvreader:
            if len(row) == len(header):
                placeholders = ', '.join(['?' for _ in row])
                insert_sql = f'INSERT INTO transactions_Payment VALUES ({placeholders})'
                c.execute(insert_sql, row)
            else:
                st.warning(f"Row with {len(row)} columns found, expected {len(header)} columns. Skipping row: {row}")
    
    conn.commit()
    conn.close()

# 함수 호출하여 테이블 생성 및 데이터 삽입
create_table_from_csv()

# 사용자 문의에 따라 거래내역 조회 함수
def fetch_transactions(inquiry):
    conn = sqlite3.connect('history.db', check_same_thread=False)
    query = f"SELECT * FROM transactions_Payment WHERE {inquiry} ORDER BY InvoiceDate DESC"
    transactions = pd.read_sql_query(query, conn)
    conn.close()
    return transactions

# Streamlit 앱 초기화
def main():
    st.title('Text-To-Watsonx : Engage AR')

    st.markdown("""
        Welcome to the Text-To-Watsonx : Engage AR.
        Here, you can inquire about various aspects of Engage AR transactions.
        Use the example queries as a guide to format your questions.
        **Important: AI responses can vary, you might need to fine-tune your prompt template or LLM for improved results.**
    """)

    # 예시 문의 목록
    example_inquiries = [
        "DueDate > DATE('now')",
        "RepNo. = 'Lisa' AND Category = 'Yellow'",
        "RepNo. = 'David' AND ForecastCode = 'AUTO'",
        "RepNo. = 'John' AND ForecastDate > '2024-08-01'",
        "ForecastCode = 'AUTO' GROUP BY RepNo.",
        "DueDate > '2024-08-10'",
        "Category = 'Green' GROUP BY RepNo."
    ]
    
    st.markdown("**Example Inquiries:**")
    selected_inquiry = st.selectbox("Select an inquiry example:", example_inquiries)

    # 문의 제출 폼
    inquiry = st.text_input('Submit an Inquiry:', selected_inquiry)

    # 제출된 문의에 따라 거래내역 테이블 표시
    if st.button('Submit'):
        try:
            transactions = fetch_transactions(inquiry)
            st.markdown("**Filtered Transactions:**")
            st.dataframe(transactions)
        except Exception as e:
            st.markdown(f"**Error occurred:** {str(e)}")

if __name__ == '__main__':
    main()
