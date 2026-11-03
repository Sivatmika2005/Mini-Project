"""Login / Signup page with modern, professional SaaS design aesthetics."""
import streamlit as st
from components.navbar import render_navbar
from utils import auth
from utils.translations import t


def render():
    if st.session_state.get("user"):
        st.session_state.page = "dashboard"
        st.rerun()
        return

    render_navbar(logged_in=False)

    st.markdown(
        """
        <style>
        .aw-login-card {
            background: rgba(255, 255, 255, 0.95);
            border-radius: 20px;
            padding: 24px 28px 18px 28px;
            box-shadow: 0 10px 30px rgba(124, 124, 235, 0.12);
            border: 1px solid rgba(124, 124, 235, 0.15);
            margin-bottom: 20px;
            text-align: center;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )

    if st.button("← Back to Home", key="login_back", type="secondary"):
        st.session_state.page = "landing"
        st.rerun()

    # Centered single professional layout column
    col_l, col_center, col_r = st.columns([1, 1.8, 1])

    with col_center:
        # Professional Header Card
        st.markdown(
            f"""
            <div class='aw-login-card'>
                <div style='font-size:2.2rem;margin-bottom:4px;'>🌿</div>
                <h2 style='margin:0 0 4px 0;font-size:1.55rem;font-weight:800;'>
                    {t('app_title')}
                </h2>
                <p class='aw-muted' style='margin:0;font-size:0.88rem;'>
                    Welcome back! Please sign in to your account.
                </p>
            </div>
            """,
            unsafe_allow_html=True,
        )

        tab_login, tab_signup = st.tabs(["🔒 Log In", "🌱 Create Account"])

        with tab_login:
            # 1. Check if user landed here with a Firebase password reset action code (oobCode)
            oob_code = st.query_params.get("oobCode")
            mode = st.query_params.get("mode")

            if oob_code or mode == "resetPassword":
                # Case A: oobCode present — user clicked link from Firebase email
                #         and lands directly in this app (continueUrl with oobCode).
                # Case B: mode=resetPassword but no oobCode — Firebase's hosted page
                #         completed the reset and redirected here via continueUrl.
                #         Password is already updated; just show a success message.
                if mode == "resetPassword" and not oob_code:
                    st.success("✅ Your password has been updated successfully! Please log in with your new password below.")
                    st.query_params.clear()
                    st.rerun()
                st.markdown("<div style='margin-top:14px;'></div>", unsafe_allow_html=True)
                st.markdown("<h4 style='margin-bottom:4px;'>Set New Password 🔑</h4>", unsafe_allow_html=True)
                st.markdown("<p class='aw-muted' style='font-size:0.85rem;margin-bottom:16px;'>Please enter your new password below. It will be securely updated in Firebase Authentication.</p>", unsafe_allow_html=True)

                new_pass = st.text_input("New Password (6+ chars)", type="password", key="reset_new_password")
                confirm_pass = st.text_input("Confirm New Password", type="password", key="reset_confirm_password")

                st.markdown("<div style='margin-top:12px;'></div>", unsafe_allow_html=True)
                if st.button("Update Password →", key="confirm_reset_btn", type="primary", use_container_width=True):
                    if not new_pass or len(new_pass) < 6:
                        st.error("Password must be at least 6 characters.")
                    elif new_pass != confirm_pass:
                        st.error("Passwords do not match. Please try again.")
                    else:
                        with st.spinner("Updating password in Firebase Authentication..."):
                            success, msg = auth.confirm_password_reset_with_code(oob_code or "", new_pass)
                            if success:
                                st.success(msg)
                                st.query_params.clear()
                            else:
                                st.error(msg)

                st.markdown("<div style='margin-top:14px;'></div>", unsafe_allow_html=True)
                if st.button("← Return to Log In", key="return_login_from_reset", type="secondary", use_container_width=True):
                    st.query_params.clear()
                    st.session_state.show_forgot_pass_view = False
                    st.rerun()

            elif st.session_state.get("show_forgot_pass_view"):
                st.markdown("<div style='margin-top:14px;'></div>", unsafe_allow_html=True)
                st.markdown("<h4 style='margin-bottom:4px;'>Reset Your Password 🔑</h4>", unsafe_allow_html=True)
                st.markdown("<p class='aw-muted' style='font-size:0.85rem;margin-bottom:16px;'>Enter your registered email address below to receive a secure password reset link.</p>", unsafe_allow_html=True)

                reset_email = st.text_input("Registered Email Address", placeholder="name@example.com", key="reset_email_input")

                st.markdown("<div style='margin-top:8px;'></div>", unsafe_allow_html=True)
                if st.button("Send Reset Link →", key="verify_reset_email_btn", type="primary", use_container_width=True):
                    if not reset_email:
                        st.error("Please enter your registered email address.")
                    else:
                        with st.spinner("Processing password reset request..."):
                            success, msg = auth.send_password_reset_request(reset_email)
                            if success:
                                st.success(msg)
                            else:
                                st.error(msg)

                st.markdown("<div style='margin-top:14px;'></div>", unsafe_allow_html=True)
                if st.button("← Back to Log In", key="back_to_login_btn", type="secondary", use_container_width=True):
                    st.session_state.show_forgot_pass_view = False
                    st.rerun()

            else:
                st.markdown("<div style='margin-top:14px;'></div>", unsafe_allow_html=True)
                username = st.text_input("Username or Email", placeholder="e.g. sivat or name@gmail.com", key="login_username")
                password = st.text_input("Password", type="password", placeholder="Enter password", key="login_password")

                col_forgot1, col_forgot2 = st.columns([1.3, 1])
                with col_forgot2:
                    if st.button("Forgot Password?", key="goto_forgot_pass"):
                        st.session_state.show_forgot_pass_view = True
                        st.rerun()

                st.markdown("<div style='margin-top:8px;'></div>", unsafe_allow_html=True)
                if st.button("Log In to Account →", key="login_submit", type="primary", use_container_width=True):
                    with st.spinner("Authenticating..."):
                        user = auth.authenticate_user(username, password)
                        if user and user != "NETWORK_ERROR":
                            auth.login_user(user)
                            st.session_state.page = "dashboard"
                            st.success("Welcome back! Redirecting to Dashboard...")
                            st.rerun()
                        elif user == "NETWORK_ERROR":
                            st.error("Could not reach the authentication server. Please check your internet connection and try again.")
                        else:
                            st.error("Invalid username/email or password. Please try again.")

        with tab_signup:
            st.markdown("<div style='margin-top:14px;'></div>", unsafe_allow_html=True)
            new_username = st.text_input("Choose a username", placeholder="e.g. Sivat", key="signup_username")
            new_email = st.text_input("Email address", placeholder="name@example.com", key="signup_email")
            new_password = st.text_input("Create password (6+ chars)", type="password", key="signup_password")
            confirm_password = st.text_input("Confirm password", type="password", key="signup_confirm")

            st.markdown("<div style='margin-top:10px;'></div>", unsafe_allow_html=True)
            agree = st.checkbox("I acknowledge this app is a wellness support tool, not clinical care.", key="signup_agree")
            st.markdown("<div style='margin-top:14px;'></div>", unsafe_allow_html=True)

            if st.button("Create My Account →", key="signup_submit", type="primary", use_container_width=True):
                if new_password != confirm_password:
                    st.error("Passwords do not match. Please verify.")
                elif not agree:
                    st.error("Please check the acknowledgment box to continue.")
                else:
                    success, message = auth.register_user(new_username, new_email, new_password)
                    if success:
                        st.success(f"{message} Logging you in...")
                        user = auth.authenticate_user(new_username, new_password)
                        if user and user != "NETWORK_ERROR":
                            auth.login_user(user)
                            st.session_state.page = "dashboard"
                            st.rerun()
                    else:
                        st.error(message)
