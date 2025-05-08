import streamlit as st
import pymysql
from uuid import uuid4
from dotenv import load_dotenv
import os
import time
from datetime import datetime

# Load environment variables from .env file
load_dotenv()

# Initialize MySQL database connection using environment variables
conn = pymysql.connect(
    host=os.getenv('DB_HOST'),
    user=os.getenv('DB_USER'),
    password=os.getenv('DB_PASSWORD'),
    db=os.getenv('DB_NAME'),
    port=int(os.getenv('DB_PORT')),
    charset=os.getenv('DB_CHARSET'),
    connect_timeout=int(os.getenv('DB_CONNECT_TIMEOUT')),
    read_timeout=int(os.getenv('DB_READ_TIMEOUT')),
    write_timeout=int(os.getenv('DB_WRITE_TIMEOUT')),
    cursorclass=pymysql.cursors.DictCursor
)

# Create table if it doesn't exist
with conn.cursor() as c:
    c.execute('''
        CREATE TABLE IF NOT EXISTS interview (
            id INT PRIMARY KEY AUTO_INCREMENT,
            name VARCHAR(255) NOT NULL,
            emailid VARCHAR(255) NOT NULL,
            interview_mode VARCHAR(50) NOT NULL,
            last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
        )
    ''')
    conn.commit()

# Migrate table schema to add missing columns
with conn.cursor() as c:
    try:
        c.execute('ALTER TABLE interview ADD COLUMN interview_status VARCHAR(50) DEFAULT \'Pending\'')
        conn.commit()
    except pymysql.err.OperationalError as e:
        if "Duplicate column name" not in str(e):
            raise e
    try:
        c.execute('ALTER TABLE interview ADD COLUMN good_points TEXT')
        conn.commit()
    except pymysql.err.OperationalError as e:
        if "Duplicate column name" not in str(e):
            raise e
    try:
        c.execute('ALTER TABLE interview ADD COLUMN bad_points TEXT')
        conn.commit()
    except pymysql.err.OperationalError as e:
        if "Duplicate column name" not in str(e):
            raise e
    try:
        c.execute('ALTER TABLE interview ADD COLUMN overall TEXT')
        conn.commit()
    except pymysql.err.OperationalError as e:
        if "Duplicate column name" not in str(e):
            raise e
    try:
        c.execute('ALTER TABLE interview ADD COLUMN last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP')
        conn.commit()
    except pymysql.err.OperationalError as e:
        if "Duplicate column name" not in str(e):
            raise e

# Dictionary of names and emails
dict_of_names = {
    "Mahim Gupta": "mahimgupta@jklu.edu.in",
    "Aman Gupta": "amangupta2024@jklu.edu.in",
    "Yash Bansal": "yashbansal@jklu.edu.in",
    "Devam Gupta": "devamgupta@jklu.edu.in",
    "Ayush Sharma": "ayushsharma2024@jklu.edu.in",
    "Atharv Mehrotra": "atharvmehrotra@jklu.edu.in",
    "Somay Agarwal": "somayagarwal@jklu.edu.in",
    "Aditya Nayak": "adityanayak@jklu.edu.in",
    "Priyanshu Jain": "priyanshujain@jklu.edu.in",
    "Aman Pratap Singh": "amanpratapsingh@jklu.edu.in",
    "Divyanshi Gupta": "Divyanshigupta@jklu.edu.in  ",
    "Yash Mishra": "yashmishra2024@jklu.edu.in",
    "Prateek Saxena": "pksaxena6453@gmail.com"
}

# Hardcoded admin password (not secure for production)
ADMIN_PASSWORD = os.getenv('ADMIN_PASSWORD')  # Replace with your actual admin password

def get_email_from_name(name):
    return dict_of_names.get(name.title())

def get_candidate_names():
    with conn.cursor() as c:
        c.execute('SELECT name FROM interview')
        return [row['name'] for row in c.fetchall()]

def get_recent_updates():
    with conn.cursor() as c:
        c.execute('SELECT name, interview_mode, last_updated FROM interview ORDER BY last_updated DESC')
        return c.fetchall()

def main():
    # Initialize session state
    if 'name' not in st.session_state:
        st.session_state.name = ""
    if 'email' not in st.session_state:
        st.session_state.email = ""
    if 'admin_logged_in' not in st.session_state:
        st.session_state.admin_logged_in = False
    if 'page' not in st.session_state:
        st.session_state.page = "main"

    if st.session_state.page == "main":
        st.title("Tech and Support Coordinator Role for Sabrang 2025")
        # Login as Admin button
        if st.button("Login as Admin"):
            st.session_state.page = "admin_login"
            st.rerun()
        st.write("Select your name from the dropdown below.")

        # Candidate Form
        name_options = [""] + sorted(dict_of_names.keys())
        selected_name = st.selectbox("Select Your Name", name_options, index=name_options.index(st.session_state.name) if st.session_state.name in name_options else 0, key="name_select")

        # Update name and email when a name is selected
        if selected_name and selected_name != st.session_state.name:
            st.session_state.name = selected_name
            email_from_dict = get_email_from_name(selected_name)
            st.session_state.email = email_from_dict if email_from_dict else ""
            st.rerun()

        # Email input (read-only, autofilled based on name)
        email = st.text_input("Email", value=st.session_state.email, disabled=True, key="email_input")

        # Interview mode dropdown
        interview_mode = st.selectbox("Interview Mode", ["Offline", "Online"])
        st.write("If you encounter any issues, please try using mobile data instead of college Wi-Fi or contact Suryaansh.")
               
        # Submit button
        if st.button("Submit"):
            if st.session_state.name and st.session_state.email and interview_mode:
                # Check if candidate already exists
                with conn.cursor() as c:
                    c.execute('SELECT id FROM interview WHERE name = %s', (st.session_state.name.title(),))
                    existing = c.fetchone()
                
                if existing:
                    # Update existing record
                    with conn.cursor() as c:
                        c.execute('''
                            UPDATE interview 
                            SET emailid = %s, interview_mode = %s, interview_status = %s, last_updated = CURRENT_TIMESTAMP
                            WHERE name = %s
                        ''', (st.session_state.email, interview_mode, 'Pending', st.session_state.name.title()))
                        conn.commit()
                else:
                    # Insert new record
                    with conn.cursor() as c:
                        c.execute('''
                            INSERT INTO interview (name, emailid, interview_mode, interview_status, last_updated)
                            VALUES (%s, %s, %s, %s, CURRENT_TIMESTAMP)
                        ''', (st.session_state.name.title(), st.session_state.email, interview_mode, 'Pending'))
                        conn.commit()
                
                # Show success message and snowflakes with a delay
                st.success("🎉 Submission successful! See you at the interview.")
                st.snow()
                time.sleep(7)  # Delay to show snowflakes and message
                
                # Clear form
                st.session_state.name = ""
                st.session_state.email = ""
                st.rerun()
            else:
                st.error("Please select a name and choose an interview mode, or contact Suryaansh.")

    elif st.session_state.page == "admin_login":
        st.title("Admin Login")
        username = st.text_input("Username", key="admin_username")
        password = st.text_input("Password", type="password", key="admin_password")
        col1, col2 = st.columns(2)
        with col1:
            if st.button("Login"):
                if password == ADMIN_PASSWORD:
                    st.session_state.admin_logged_in = True
                    st.session_state.page = "admin_panel"
                    st.success("Logged in successfully!")
                    st.rerun()
                else:
                    st.error("Invalid username or password.")
        with col2:
            if st.button("Back to Main"):
                st.session_state.page = "main"
                st.rerun()

    elif st.session_state.page == "admin_panel":
        st.title("Admin Panel: Candidate Interview Details")
        if st.button("Logout"):
            st.session_state.admin_logged_in = False
            st.session_state.page = "main"
            st.rerun()

        # Display recent updates
        st.subheader("Recent Preference Updates")
        recent_updates = get_recent_updates()
        if not recent_updates:
            st.warning("No candidates found in the database.")
        else:
            # Create a table for recent updates
            st.table([
                {"Name": row['name'], "Interview Mode": row['interview_mode'], "Last Updated": row['last_updated']}
                for row in recent_updates
            ])

        # Existing candidate selection and details
        st.subheader("Candidate Details")
        candidate_names = get_candidate_names()
        if not candidate_names:
            st.warning("No candidates found in the database.")
        else:
            selected_candidate = st.selectbox("Select Candidate", [""] + sorted(candidate_names), key="admin_candidate_select")
            if selected_candidate:
                # Fetch current details
                with conn.cursor() as c:
                    c.execute('SELECT interview_status, good_points, bad_points, overall, interview_mode, last_updated FROM interview WHERE name = %s', (selected_candidate,))
                    result = c.fetchone()
                
                # Display interview mode and last updated timestamp
                st.write(f"**Interview Mode**: {result['interview_mode']}")
                st.write(f"**Last Updated**: {result['last_updated']}")

                # Input fields for interview details
                interview_status = st.selectbox("Interview Status", ["Pending", "Scheduled", "Done"], 
                                             index=["Pending", "Scheduled", "Done"].index(result['interview_status']) if result and result['interview_status'] else 0,
                                             key=f"status_{selected_candidate}")
                good_points = st.text_area("Good Points", value=result['good_points'] if result and result['good_points'] else "", key=f"good_{selected_candidate}")
                bad_points = st.text_area("Bad Points", value=result['bad_points'] if result and result['bad_points'] else "", key=f"bad_{selected_candidate}")
                overall = st.text_area("Overall Assessment", value=result['overall'] if result and result['overall'] else "", key=f"overall_{selected_candidate}")

                # Save button
                if st.button("Save Candidate Details", key=f"save_{selected_candidate}"):
                    with conn.cursor() as c:
                        c.execute('''
                            UPDATE interview 
                            SET interview_status = %s, good_points = %s, bad_points = %s, overall = %s, last_updated = CURRENT_TIMESTAMP
                            WHERE name = %s
                        ''', (interview_status, good_points, bad_points, overall, selected_candidate))
                        conn.commit()
                    st.success(f"Details for {selected_candidate} saved successfully!")

if __name__ == "__main__":
    try:
        main()
    finally:
        # Close database connection when app closes
        conn.close()
