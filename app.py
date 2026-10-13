import streamlit as st

# 1. PAGE CONFIGURATION
st.set_page_config(page_title="Rural Data", page_icon="📊", layout="centered")

# 2. SESSION STATE (Replaces Flutter Navigator/State)
if 'logged_in' not in st.session_state:
    st.session_state['logged_in'] = False

# 3. LOGIN SCREEN
def login_screen():
    st.title("📊 Rural Data")
    st.write("Please sign in to access the dashboard.")
    
    email = st.text_input("Email")
    password = st.text_input("Password", type="password")
    
    if st.button("Login", type="primary", use_container_width=True):
        if email and password: 
            st.session_state['logged_in'] = True
            st.rerun()

# 4. DASHBOARD SCREEN
def dashboard_screen():
    st.title("Rural Data Overview")
    st.subheader("Company Units")
    
    # Creates a 2x2 grid similar to Flutter's GridView
    col1, col2 = st.columns(2)
    
    with col1:
        st.success("📈 **Kutipan**\n\nView collection metrics.")
        st.warning("💰 **Pembiayaan**\n\nManage financing data.")
        
    with col2:
        st.info("🛡️ **Takaful**\n\nMonitor insurance policies.")
        st.error("💻 **Digital Business**\n\nDigital initiative tracking.")

# 5. PROFILE SCREEN
def profile_screen():
    st.title("My Profile")
    st.write("👤 **Name:** Nur Huda Batrisyia")
    st.write("📧 **Email:** huda.batrisyia@ruraldata.com")
    st.write("🏢 **Unit:** Digital Business")
    
    st.divider()
    
    if st.button("Logout", type="primary"):
        st.session_state['logged_in'] = False
        st.rerun()

# 6. MAIN APP ROUTING
if not st.session_state['logged_in']:
    login_screen()
else:
    # Sidebar replaces Flutter's BottomNavigationBar
    st.sidebar.title("Navigation")
    page = st.sidebar.radio("Go to:", ["Dashboard", "Profile"])
    
    if page == "Dashboard":
        dashboard_screen()
    elif page == "Profile":
        profile_screen()