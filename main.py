import streamlit as st
import hashlib
from cryptography.fernet import Fernet, InvalidToken
import time

# Page Configuration
st.set_page_config(
    page_title="Encrypted Data Manager🔐",
    page_icon="🛡️",
    layout="centered",
    initial_sidebar_state="expanded"
)

# Session State Initialization 
if "users" not in st.session_state:
    st.session_state.users = {}

if "current_user" not in st.session_state:
    st.session_state.current_user = None

if "FERNET_KEY" not in st.session_state:
    st.session_state.FERNET_KEY = Fernet.generate_key()

cipher = Fernet(st.session_state.FERNET_KEY)

# Utility Functions
def hash_string(s):
    return hashlib.sha256(s.encode()).hexdigest()

def encrypt_text(text):
    return cipher.encrypt(text.encode()).decode()

def decrypt_text(encrypted):
    try:
        return cipher.decrypt(encrypted.encode()).decode()
    except InvalidToken:
        return None
    except Exception as e:
        return f"Decryption Error: {str(e)}"

# ---------- Pages 
def register_page():
    st.title("📝 Register New Account")
    username = st.text_input("Username:")
    password = st.text_input("Password:", type="password")

    if st.button("Register"):
        if not username or not password:
            st.warning("⚠️ All fields are required.")
        elif username in st.session_state.users:
            st.error("🚫 Username already exists.")
        else:
            st.session_state.users[username] = {
                "password": hash_string(password),
                "data": {},
                "failed_attempts": 0
            }
            st.success("✅ Account created! Please log in.")
            time.sleep(1)
            st.session_state.page = "Login"
            st.rerun()

def login_page():
    st.title("🔐 User Login")
    username = st.text_input("Username:")
    password = st.text_input("Password:", type="password")

    if st.button("Login"):
        if username not in st.session_state.users:
            st.error("❌ User not found.")
        elif st.session_state.users[username]["password"] != hash_string(password):
            st.error("❌ Incorrect password.")
        else:
            st.session_state.current_user = username
            st.session_state.users[username]["failed_attempts"] = 0
            st.success(f"✅ Welcome, {username}!")
            time.sleep(1)
            st.session_state.page = "Home"
            st.rerun()

def home_page():
    st.title("🏠 Home Page")
    user = st.session_state.current_user
    st.markdown(f"👋 **Welcome, {user}!**")
    st.write("This app allows you to securely encrypt and decrypt your private text using a secret passkey.")

    st.subheader("🔐 Store Encrypted Data")
    st.write("""
    - Navigate to the **Store Data** section from the sidebar.
    - Enter any text you wish to encrypt.
    - Provide a **secret passkey** of your choice.
    - The text will be securely encrypted and saved.
    - Make sure to remember your passkey — it is needed for decryption!
    """)

    st.subheader("🔓 Retrieve Encrypted Data")
    st.write("""
    - Navigate to the **Retrieve Data** section from the sidebar.
    - Paste the previously encrypted text.
    - Enter the **same passkey** you used to encrypt the data.
    - If the passkey is correct, your original text will be shown.
    - ⚠️ After 3 incorrect attempts, you’ll be locked out and redirected to login.
    """)

    st.info("🛡️ Your data is encrypted using Fernet (AES encryption) for privacy and security.")

def store_data():
    st.header("📥 Store Encrypted Data")
    user = st.session_state.current_user
    text = st.text_area("Enter text to encrypt:")
    passkey = st.text_input("Enter a secret passkey:", type="password")

    if st.button("🔐 Encrypt and Save"):
        if not text or not passkey:
            st.warning("⚠️ All fields required.")
        else:
            encrypted = encrypt_text(text)
            hashed_passkey = hash_string(passkey)
            st.session_state.users[user]["data"][encrypted] = {
                "encrypted_text": encrypted,
                "passkey": hashed_passkey
            }
            st.success("✅ Text encrypted and stored.")
            st.code(encrypted)

def retrieve_data():
    st.header("🔓 Retrieve Encrypted Data")
    user = st.session_state.current_user

    if st.session_state.users[user]["failed_attempts"] >= 3:
        st.error("🚫 Too many failed attempts. Please log in again.")
        st.session_state.current_user = None
        st.session_state.page = "Login"
        time.sleep(1)
        st.rerun()

    encrypted_input = st.text_area("Enter encrypted text:")
    passkey_input = st.text_input("Enter your passkey:", type="password")

    if st.button("🔍 Decrypt"):
        if not encrypted_input or not passkey_input:
            st.warning("⚠️ All fields required.")
        else:
            entry = st.session_state.users[user]["data"].get(encrypted_input)
            hashed_passkey = hash_string(passkey_input)

            if entry and entry["passkey"] == hashed_passkey:
                result = decrypt_text(encrypted_input)
                if result is not None:
                    st.session_state.users[user]["failed_attempts"] = 0
                    st.success("✅ Decryption successful!")
                    st.code(result)
                else:
                    st.error("❌ Invalid encrypted data.")
            else:
                st.session_state.users[user]["failed_attempts"] += 1
                remaining = 3 - st.session_state.users[user]["failed_attempts"]
                st.error(f"❌ Incorrect passkey! Attempts left: {remaining}")
                if remaining == 0:
                    st.warning("🔒 Locked out. Redirecting to login...")
                    st.session_state.current_user = None
                    st.session_state.page = "Login"
                    time.sleep(1)
                    st.rerun()

# Navigation
if "page" not in st.session_state:
    st.session_state.page = "Login"

if st.session_state.current_user:
    st.sidebar.title("🔧 Navigation")
    nav = st.sidebar.radio("Go to:", ["Home", "Store Data", "Retrieve Data", "Logout"])

    if nav == "Home":
        home_page()
    elif nav == "Store Data":
        store_data()
    elif nav == "Retrieve Data":
        retrieve_data()
    elif nav == "Logout":
        st.session_state.current_user = None
        st.session_state.page = "Login"
        st.rerun()
else:
    nav = st.sidebar.radio("🔑 Auth Menu", ["Login", "Register"])
    st.session_state.page = nav

    if nav == "Login":
        login_page()
    elif nav == "Register":
        register_page()

#  Sidebar Footer 
st.sidebar.markdown("""---""")
st.sidebar.markdown("🔗 **Connect with me:**")
st.sidebar.markdown("[![LinkedIn](https://img.shields.io/badge/LinkedIn-RidaFatima-blue?logo=linkedin)](https://www.linkedin.com/in/rida-fatima-597aa32b6?utm_source=share&utm_campaign=share_via&utm_content=profile&utm_medium=android_app)")

st.sidebar.markdown("🧑‍💻 **About Me:**")
st.sidebar.info("I'm Rida Fatima and I made this app as part of a Python assignment given by Sir Zia. It demonstrates a simple encrypted data manager built with Streamlit.")

# Main Footer
st.markdown("""---  
<center style='color:gray'><b>🛡️ Secure Data App | By Rida Fatima</b></center>  
""", unsafe_allow_html=True)
