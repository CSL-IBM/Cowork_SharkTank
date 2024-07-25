import streamlit as st
import pandas as pd

st.set_page_config(layout="wide")

# Function to fetch transactions based on the inquiry
def fetch_transactions(df, inquiry):
    try:
        # Use the query method to filter the DataFrame
        transactions = df.query(inquiry)
        return transactions
    except Exception as e:
        st.error(f"Error processing the inquiry: {str(e)}")
        return pd.DataFrame()

# Initialize Streamlit app
def main():
    st.title('Text-To-Watsonx : Engage AR')

    st.markdown("""
        Welcome to the Text-To-Watsonx : Engage AR.
        Here, you can inquire about various aspects of Engage AR transactions.
        Use the example queries as a guide to format your questions.
        **Important: AI responses can vary, you might need to fine-tune your prompt template or LLM for improved results.**
    """)

    # Load data from the uploaded CSV file
    try:
        df = pd.read_csv('transactions_Payment.csv')
    except FileNotFoundError:
        st.error("CSV file not found. Please ensure the 'transactions_Payment.csv' file is uploaded.")
        return

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
        transactions = fetch_transactions(df, inquiry)
        if not transactions.empty:
            st.markdown("**Filtered Transactions:**")
            st.dataframe(transactions)
        else:
            st.markdown("**No transactions found for the given inquiry.**")

if __name__ == '__main__':
    main()
