import streamlit as st
import pandas as pd
from datetime import datetime
import os
import base64

# ---------------- SET BACKGROUND IMAGE ----------------
def set_bg(image_file):
    with open(image_file, "rb") as f:
        encoded = base64.b64encode(f.read()).decode()
    st.markdown(
        f"""
        <style>
        .stApp {{
            background-image: url("data:image/jpg;base64,{encoded}");
            background-size: cover;
            background-position: center;
            background-repeat: no-repeat;
            background-attachment: fixed;
        }}
        </style>
        """,
        unsafe_allow_html=True
    )

set_bg("cite.jpg")  # <-- replace with your image file

# ---------------- TRANSPARENT FORM & INPUT CSS ----------------
st.markdown("""
<style>
/* Transparent form container */
.css-1d391kg, .stForm {
    background-color: transparent !important;
    box-shadow: none !important;
}

/* Transparent text input */
.stTextInput>div>div>input {
    background-color: rgba(255,255,255,0.3) !important;
    border: 1px solid rgba(0,0,0,0.2) !important;
    border-radius: 8px;
    padding: 8px;
    color: #000;
}

/* Transparent selectbox */
.stSelectbox>div>div>div>select {
    background-color: rgba(255,255,255,0.3) !important;
    border: 1px solid rgba(0,0,0,0.2) !important;
    border-radius: 8px;
    padding: 6px;
    color: #000;
}

/* Centered form container */
.centered-form {
    background-color: rgba(255, 255, 255, 0.15);
    padding: 30px;
    border-radius: 15px;
    width: 450px;
    margin: auto;
    margin-top: 20px;
}
</style>
""", unsafe_allow_html=True)

# ---------------- FILE & FACULTY SETTINGS ----------------
FILE_NAME = "lab_login_data.csv"
FACULTY_CREDENTIALS = {
    "FACULTY001": "pass001",
    "FACULTY002": "pass002",
    "FACULTY003": "pass003"
}

if "faculty_logged_in" not in st.session_state:
    st.session_state.faculty_logged_in = False

if not os.path.exists(FILE_NAME):
    df = pd.DataFrame(columns=[
        "Register Number", "Programme", "Year",
        "Purpose", "Login Time", "Logout Time"
    ])
    df.to_csv(FILE_NAME, index=False)

# ---------------- PAGE TITLE ----------------
st.markdown("<h1 style='text-align: center; color: black ;'>LAB LOGIN</h1>", unsafe_allow_html=True)

# ---------------- ROLE SELECTION ----------------
role = st.sidebar.radio("Select Role", ["Student Login", "Student Logout", "Faculty View"])

# ---------------- HELPER FUNCTIONS ----------------
def start_form():
    st.markdown('<div class="centered-form">', unsafe_allow_html=True)

def end_form():
    st.markdown('</div>', unsafe_allow_html=True)

# ---------------- STUDENT LOGIN ----------------
if role == "Student Login":
    st.subheader("STUDENT LOGIN")
    start_form()

    reg_no = st.text_input("Register Number")
    programme = st.selectbox("Programme", [
        "M.Sc Data Analytics",
        "M,Sc Information Technology",
        "M.Sc Cyber Security",
        "B.Sc AI & ML"
    ])
    year = st.selectbox("Year", ["I", "II", "III"])
    purpose = st.selectbox("Purpose of Visit", ["Lab Practical", "Project Work"])

    if st.button("Login"):
        if reg_no:
            login_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            df = pd.read_csv(FILE_NAME)
            new_data = {
                "Register Number": reg_no,
                "Programme": programme,
                "Year": year,
                "Purpose": purpose,
                "Login Time": login_time,
                "Logout Time": ""
            }
            df = df._append(new_data, ignore_index=True)
            df.to_csv(FILE_NAME, index=False)
            st.success("✅ Login recorded successfully")
        else:
            st.error("❌ Please fill all fields")
    end_form()

# ---------------- STUDENT LOGOUT ----------------
elif role == "Student Logout":
    st.subheader("STUDENT LOGOUT")
    start_form()

    reg_no = st.text_input("Enter Register Number")
    if st.button("Logout"):
        df = pd.read_csv(FILE_NAME)
        active_rows = df[(df["Register Number"] == reg_no) & (df["Logout Time"].isna() | (df["Logout Time"] == ""))]
        if not active_rows.empty:
            last_index = active_rows.index[-1]
            df.loc[last_index, "Logout Time"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            df.to_csv(FILE_NAME, index=False)
            st.success("✅ Logout recorded successfully")
        else:
            st.warning("⚠ No active login found. Please login first.")
    end_form()

# ---------------- FACULTY VIEW ----------------
# ---------------- FACULTY VIEW ----------------
elif role == "Faculty View":
    st.subheader("FACULTY LOGIN")
    start_form()

    if not st.session_state.faculty_logged_in:
        faculty_id = st.text_input("Faculty ID")
        password = st.text_input("Password", type="password")
        if st.button("Login"):
            if faculty_id in FACULTY_CREDENTIALS and FACULTY_CREDENTIALS[faculty_id] == password:
                st.session_state.faculty_logged_in = True
                st.success("✅ Faculty Login Successful")
                # Trigger rerender using st.query_params
                st.query_params = {"faculty_logged_in": "true"}
            else:
                st.error("❌ Invalid Faculty ID or Password")
    else:
        st.subheader("Student Coding Records")
        df = pd.read_csv(FILE_NAME)

        # Filters
        programme_filter = st.selectbox("Select Programme", ["All", "M.Sc Data Analytics", "Information Technology", "M.Sc Cyber Security", "B.Sc AI & ML"])
        year_filter = st.selectbox("Select Year", ["All", "I", "II", "III"])
        purpose_filter = st.selectbox("Select Purpose", ["All", "Lab Practical", "Project Work"])

        filtered_df = df.copy()
        if programme_filter != "All":
            filtered_df = filtered_df[filtered_df["Programme"] == programme_filter]
        if year_filter != "All":
            filtered_df = filtered_df[filtered_df["Year"] == year_filter]
        if purpose_filter != "All":
            filtered_df = filtered_df[filtered_df["Purpose"] == purpose_filter]

        st.dataframe(filtered_df)
        st.markdown("### 📈 Coding Analysis")
        st.write("Total Lab Visits:", len(filtered_df))
        st.write("Unique Students:", filtered_df["Register Number"].nunique())

        if st.button("Logout Faculty"):
            st.session_state.faculty_logged_in = False
            st.success("👋 Faculty logged out")
            # Trigger rerender after logout
            st.query_params = {"faculty_logged_in": "false"}

    end_form()
