"""Professional Support page with verified Indian Psychiatrists directory & 24/7 crisis guidance."""
import streamlit as st
from components.sidebar import render_sidebar
from utils import db

VERIFIED_PSYCHIATRISTS = [
    {
        "id": "dr-achal-bhagat",
        "name": "Dr. Achal Bhagat",
        "designation": "Senior Consultant Psychiatrist & Psychotherapist",
        "hospital": "Indraprastha Apollo Hospitals",
        "city": "Delhi-NCR",
        "address": "Sarita Vihar, Delhi Mathura Road, New Delhi",
        "experience": "30+ Years",
        "specialization": ["Depression", "Anxiety Disorders", "Mood Disorders", "Psychotherapy", "Stress Management"],
        "consultationType": "In-Person OPD & Video Consultation",
        "bookingUrl": "https://www.apollohospitals.com/doctors/psychiatrist/delhi/dr-achal-bhagat",
        "phone": "1860-500-1066",
    },
    {
        "id": "dr-soumiya-mudgal",
        "name": "Dr. Soumiya Mudgal",
        "designation": "Senior Consultant – Mental Health & Behavioural Sciences (Psychiatry)",
        "hospital": "Max Super Speciality Hospital",
        "city": "Delhi-NCR",
        "address": "1, 2, Press Enclave Marg, Saket, New Delhi",
        "experience": "16+ Years",
        "specialization": ["Adult Psychiatry", "Depression", "Anxiety", "OCD", "Bipolar Disorder", "Work Stress"],
        "consultationType": "In-Person OPD & Video Consultation",
        "bookingUrl": "https://www.maxhealthcare.in/doctor/dr-soumiya-mudgal",
        "phone": "011-26515050",
    },
    {
        "id": "dr-raman-k",
        "name": "Dr. Raman K",
        "designation": "Senior Consultant Psychiatrist",
        "hospital": "Apollo Hospitals",
        "city": "Chennai",
        "address": "21 Greams Lane, Off Greams Road, Chennai, Tamil Nadu",
        "experience": "25+ Years",
        "specialization": ["Mood Disorders", "Anxiety & Panic", "Neuropsychiatry", "Cognitive Behaviour Therapy"],
        "consultationType": "In-Person OPD & Video Consultation",
        "bookingUrl": "https://www.apollohospitals.com/doctors/psychiatrist/chennai/dr-raman-k",
        "phone": "044-28290200",
    },
    {
        "id": "dr-vishal-chhabra",
        "name": "Dr. Vishal Chhabra",
        "designation": "Senior Consultant Psychiatrist",
        "hospital": "Fortis Hospital",
        "city": "Delhi-NCR",
        "address": "AA Block, Poorbi Shalimar Bag, Shalimar Bagh, New Delhi",
        "experience": "18+ Years",
        "specialization": ["Clinical Psychiatry", "Stress & Anxiety", "Depressive Disorders", "Sleep Health"],
        "consultationType": "In-Person OPD & Video Consultation",
        "bookingUrl": "https://www.fortishealthcare.com/doctors/dr-vishal-chhabra-314",
        "phone": "011-45302222",
    },
    {
        "id": "dr-sanjay-garg",
        "name": "Dr. Sanjay Garg",
        "designation": "Senior Consultant Psychiatrist",
        "hospital": "Fortis Hospital",
        "city": "Kolkata",
        "address": "730 Anandapur, E.M. Bypass Road, Kolkata, West Bengal",
        "experience": "17+ Years",
        "specialization": ["General Adult Psychiatry", "Stress Disorders", "Depression", "Psychotherapy"],
        "consultationType": "In-Person OPD & Video Consultation",
        "bookingUrl": "https://www.fortishealthcare.com/doctors/dr-sanjay-garg-2068",
        "phone": "033-66284444",
    },
    {
        "id": "dr-shantanu-bharti",
        "name": "Dr. Shantanu Bharti",
        "designation": "Senior Consultant – Mental Health & Psychiatry",
        "hospital": "Medanta – The Medicity",
        "city": "Delhi-NCR",
        "address": "CH Bakhtawar Singh Road, Sector 38, Gurugram, Haryana",
        "experience": "14+ Years",
        "specialization": ["Neuropsychiatry", "Anxiety & Panic Attacks", "Depression", "Sleep Disorders"],
        "consultationType": "In-Person OPD & Video Consultation",
        "bookingUrl": "https://www.medanta.org/doctors/dr-shantanu-bharti",
        "phone": "0124-4141414",
    },
    {
        "id": "nimhans-centre",
        "name": "NIMHANS Outpatient & Tele-MANAS Hub",
        "designation": "National Institute of Mental Health & Neurosciences",
        "hospital": "NIMHANS Central Institute",
        "city": "Bengaluru",
        "address": "Hosur Road, Lakkasandra, Bengaluru, Karnataka",
        "experience": "Apex National Institute",
        "specialization": ["Comprehensive Psychiatric Care", "Psychotherapy", "Crisis Support", "Community Mental Health"],
        "consultationType": "In-Person Hospital OPD & 24/7 Teleconsultation",
        "bookingUrl": "https://nimhans.ac.in",
        "phone": "080-46110007",
    },
]

CITIES = ["All Cities", "Bengaluru", "Chennai", "Delhi-NCR", "Kolkata"]


def render():
    render_sidebar()
    user = st.session_state.get("user")

    # Header Controls
    top_col, btn_col = st.columns([3, 1], vertical_alignment="center")
    with top_col:
        st.markdown("<h2 style='margin-bottom:0;'>Professional Support 🩺</h2>", unsafe_allow_html=True)
    with btn_col:
        if st.button("← Dashboard", key="prof_back", use_container_width=True, type="secondary"):
            st.session_state.page = "dashboard"
            st.rerun()

    st.markdown(
        "<div class='aw-muted' style='margin-top:4px;margin-bottom:16px;'>"
        "Connect with verified, qualified Indian psychiatrists and mental healthcare institutions for clinical guidance."
        "</div>",
        unsafe_allow_html=True,
    )

    # 🚨 Immediate Emergency Helpline Notice (India)
    st.markdown(
        """
        <div class='aw-card' style='border-left: 5px solid #ff6b8b; background: #fff5f6; margin-bottom: 16px; padding: 16px;'>
            <b style='color: #d63031; font-size: 1.05rem;'>🚨 Immediate Crisis &amp; Emergency Notice:</b>
            <div style='margin-top: 6px; font-size: 0.92rem; line-height: 1.6; color: var(--ink);'>
                If you or someone you know is in severe distress or experiencing thoughts of self-harm, please do not wait for a routine appointment. Reach out immediately to verified 24/7 national helplines:
            </div>
            <div style='margin-top: 10px; display: flex; flex-wrap: wrap; gap: 10px;'>
                <a href='tel:14416' style='background: #d63031; color: white; padding: 6px 14px; border-radius: 8px; text-decoration: none; font-size: 0.85rem; font-weight: 600;'>📞 Tele-MANAS: 14416 (24/7 Toll-Free)</a>
                <a href='tel:18005990019' style='background: var(--card-bg, #fff); color: var(--ink); border: 1px solid rgba(124,124,235,0.3); padding: 6px 14px; border-radius: 8px; text-decoration: none; font-size: 0.85rem; font-weight: 600;'>📞 KIRAN: 1800-599-0019</a>
                <a href='tel:+919999666555' style='background: var(--card-bg, #fff); color: var(--ink); border: 1px solid rgba(124,124,235,0.3); padding: 6px 14px; border-radius: 8px; text-decoration: none; font-size: 0.85rem; font-weight: 600;'>📞 Vandrevala Foundation: +91 9999 666 555</a>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # Supportive recommendation based on existing check-in data
    if user:
        latest = db.get_latest_checkin(user["id"])
        if latest and latest.get("stress_level", 0) >= 6:
            stress_val = latest["stress_level"]
            st.markdown(
                f"""
                <div class='aw-card' style='border-left: 5px solid var(--accent, #7c7ceb); background: rgba(124, 124, 235, 0.08); margin-bottom: 16px; padding: 14px 18px;'>
                    <div style='font-weight: 600; color: var(--ink);'>🌱 Personalized Wellness Reflection:</div>
                    <div class='aw-muted' style='font-size: 0.92rem; margin-top: 4px; line-height: 1.5;'>
                        It looks like you've recently experienced elevated stress levels ({stress_val}/10). If you are finding things difficult to manage, speaking with a licensed psychiatrist or mental-health professional can offer supportive medical guidance and personalized strategies.
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )

    # Search & City Filter
    search_col, filter_col = st.columns([2.5, 1.5])
    with search_col:
        search_query = st.text_input("Search:", placeholder="🔎 Search by doctor name, hospital, or specialty...", label_visibility="collapsed")
    with filter_col:
        selected_city = st.selectbox("Filter City:", CITIES, label_visibility="collapsed")

    query = (search_query or "").lower().strip()
    filtered_doctors = [
        d for d in VERIFIED_PSYCHIATRISTS
        if (selected_city == "All Cities" or d["city"] == selected_city)
        and (
            not query
            or query in d["name"].lower()
            or query in d["hospital"].lower()
            or query in d["city"].lower()
            or any(query in s.lower() for s in d["specialization"])
        )
    ]

    st.markdown(f"<div style='font-weight: 700; margin: 16px 0 10px 0; color: var(--ink);'>Verified Indian Psychiatrists ({len(filtered_doctors)})</div>", unsafe_allow_html=True)

    if not filtered_doctors:
        st.info("No psychiatrists matched your search. Try changing the city filter or search query.")
        return

    # Render Cards in 2 columns
    for i in range(0, len(filtered_doctors), 2):
        cols = st.columns(2)
        for j in range(2):
            if i + j < len(filtered_doctors):
                doc = filtered_doctors[i + j]
                with cols[j]:
                    specs_html = "".join(
                        f"<span style='background: var(--bg, #f5f6fa); border: 1px solid rgba(124,124,235,0.2); border-radius: 6px; padding: 2px 8px; font-size: 0.75rem; color: var(--ink); margin-right: 4px; display: inline-block; margin-bottom: 4px;'>{s}</span>"
                        for s in doc["specialization"]
                    )
                    call_btn_html = f"<a href='tel:{doc['phone'].replace('-', '')}' style='background: var(--card-bg, #fff); color: var(--ink); border: 1px solid rgba(124,124,235,0.3); padding: 8px 12px; border-radius: 8px; text-decoration: none; font-size: 0.85rem; font-weight: 600;'>📞 Call</a>" if doc.get("phone") else ""
                    
                    st.markdown(
                        f"""
                        <div class='aw-card' style='height: 100%; display: flex; flex-direction: column; justify-content: space-between; margin-bottom: 14px;'>
                            <div>
                                <div style='display: flex; justify-content: space-between; align-items: flex-start;'>
                                    <div>
                                        <div style='font-weight: 700; font-size: 1.1rem; color: var(--ink);'>👨‍⚕️ {doc['name']}</div>
                                        <div style='color: var(--accent, #7c7ceb); font-weight: 600; font-size: 0.85rem; margin-top: 2px;'>{doc['designation']}</div>
                                    </div>
                                    <span style='background: rgba(124, 124, 235, 0.15); color: var(--accent, #7c7ceb); font-size: 0.72rem; font-weight: 700; padding: 2px 8px; border-radius: 12px;'>Verified</span>
                                </div>
                                <div style='margin-top: 10px; font-size: 0.88rem; color: var(--ink);'>
                                    <div>🏥 <b>{doc['hospital']}</b></div>
                                    <div class='aw-muted' style='font-size: 0.82rem; margin-top: 2px;'>📍 {doc['address']}</div>
                                    <div style='margin-top: 4px; font-size: 0.82rem;'>⏳ <b>Experience:</b> {doc['experience']}</div>
                                    <div style='margin-top: 2px; font-size: 0.82rem;'>💻 <b>Consultation:</b> {doc['consultationType']}</div>
                                </div>
                                <div style='margin-top: 10px;'>
                                    <div style='font-size: 0.78rem; font-weight: 600; color: var(--ink); margin-bottom: 4px;'>Areas of Expertise:</div>
                                    <div>{specs_html}</div>
                                </div>
                            </div>
                            <div style='margin-top: 16px; padding-top: 12px; border-top: 1px solid rgba(124,124,235,0.15); display: flex; gap: 8px;'>
                                <a href='{doc['bookingUrl']}' target='_blank' rel='noopener noreferrer' style='flex: 1; text-align: center; background: var(--accent, #7c7ceb); color: white; padding: 8px 12px; border-radius: 8px; text-decoration: none; font-size: 0.85rem; font-weight: 600;'>📅 Book Appointment</a>
                                {call_btn_html}
                            </div>
                        </div>
                        """,
                        unsafe_allow_html=True,
                    )

    st.markdown(
        """
        <div class='aw-card' style='margin-top: 16px; padding: 14px; background: var(--card-bg, #ffffff);'>
            <div style='font-size: 0.82rem; color: var(--ink); line-height: 1.5;'>
                ℹ️ <b>Directory Information Note:</b> All listed doctors and institutions are qualified medical professionals practicing in India. Appointments are scheduled directly through official hospital portals. AI Wellness Companion does not collect booking fees or transmit personal health records.
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )
