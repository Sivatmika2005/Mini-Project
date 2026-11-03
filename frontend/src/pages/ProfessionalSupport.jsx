import React, { useState, useEffect } from 'react';
import Navbar from '../components/Navbar';
import Sidebar from '../components/Sidebar';
import { useAuth } from '../context/AuthContext';
import { useLanguage } from '../context/LanguageContext';
import { api } from '../api/client';

// Verified Indian Psychiatrists from official hospital & healthcare institutions
const VERIFIED_PSYCHIATRISTS = [
  {
    id: 'dr-achal-bhagat',
    name: 'Dr. Achal Bhagat',
    designation: 'Senior Consultant Psychiatrist & Psychotherapist',
    hospital: 'Indraprastha Apollo Hospitals',
    city: 'Delhi-NCR',
    address: 'Sarita Vihar, Delhi Mathura Road, New Delhi',
    experience: '30+ Years',
    specialization: ['Depression', 'Anxiety Disorders', 'Mood Disorders', 'Psychotherapy', 'Stress Management'],
    consultationType: 'In-Person OPD & Video Consultation',
    bookingUrl: 'https://www.apollohospitals.com/doctors/psychiatrist/delhi/dr-achal-bhagat',
    phone: '1860-500-1066',
  },
  {
    id: 'dr-soumiya-mudgal',
    name: 'Dr. Soumiya Mudgal',
    designation: 'Senior Consultant – Mental Health & Behavioural Sciences (Psychiatry)',
    hospital: 'Max Super Speciality Hospital',
    city: 'Delhi-NCR',
    address: '1, 2, Press Enclave Marg, Saket, New Delhi',
    experience: '16+ Years',
    specialization: ['Adult Psychiatry', 'Depression', 'Anxiety', 'OCD', 'Bipolar Disorder', 'Work Stress'],
    consultationType: 'In-Person OPD & Video Consultation',
    bookingUrl: 'https://www.maxhealthcare.in/doctor/dr-soumiya-mudgal',
    phone: '011-26515050',
  },
  {
    id: 'dr-raman-k',
    name: 'Dr. Raman K',
    designation: 'Senior Consultant Psychiatrist',
    hospital: 'Apollo Hospitals',
    city: 'Chennai',
    address: '21 Greams Lane, Off Greams Road, Chennai, Tamil Nadu',
    experience: '25+ Years',
    specialization: ['Mood Disorders', 'Anxiety & Panic', 'Neuropsychiatry', 'Cognitive Behaviour Therapy'],
    consultationType: 'In-Person OPD & Video Consultation',
    bookingUrl: 'https://www.apollohospitals.com/doctors/psychiatrist/chennai/dr-raman-k',
    phone: '044-28290200',
  },
  {
    id: 'dr-vishal-chhabra',
    name: 'Dr. Vishal Chhabra',
    designation: 'Senior Consultant Psychiatrist',
    hospital: 'Fortis Hospital',
    city: 'Delhi-NCR',
    address: 'AA Block, Poorbi Shalimar Bag, Shalimar Bagh, New Delhi',
    experience: '18+ Years',
    specialization: ['Clinical Psychiatry', 'Stress & Anxiety', 'Depressive Disorders', 'Sleep Health'],
    consultationType: 'In-Person OPD & Video Consultation',
    bookingUrl: 'https://www.fortishealthcare.com/doctors/dr-vishal-chhabra-314',
    phone: '011-45302222',
  },
  {
    id: 'dr-sanjay-garg',
    name: 'Dr. Sanjay Garg',
    designation: 'Senior Consultant Psychiatrist',
    hospital: 'Fortis Hospital',
    city: 'Kolkata',
    address: '730 Anandapur, E.M. Bypass Road, Kolkata, West Bengal',
    experience: '17+ Years',
    specialization: ['General Adult Psychiatry', 'Stress Disorders', 'Depression', 'Psychotherapy'],
    consultationType: 'In-Person OPD & Video Consultation',
    bookingUrl: 'https://www.fortishealthcare.com/doctors/dr-sanjay-garg-2068',
    phone: '033-66284444',
  },
  {
    id: 'dr-shantanu-bharti',
    name: 'Dr. Shantanu Bharti',
    designation: 'Senior Consultant – Mental Health & Psychiatry',
    hospital: 'Medanta – The Medicity',
    city: 'Delhi-NCR',
    address: 'CH Bakhtawar Singh Road, Sector 38, Gurugram, Haryana',
    experience: '14+ Years',
    specialization: ['Neuropsychiatry', 'Anxiety & Panic Attacks', 'Depression', 'Sleep Disorders'],
    consultationType: 'In-Person OPD & Video Consultation',
    bookingUrl: 'https://www.medanta.org/doctors/dr-shantanu-bharti',
    phone: '0124-4141414',
  },
  {
    id: 'nimhans-centre',
    name: 'NIMHANS Outpatient & Tele-MANAS Hub',
    designation: 'National Institute of Mental Health & Neurosciences',
    hospital: 'NIMHANS Central Institute',
    city: 'Bengaluru',
    address: 'Hosur Road, Lakkasandra, Bengaluru, Karnataka',
    experience: 'Apex National Institute',
    specialization: ['Comprehensive Psychiatric Care', 'Psychotherapy', 'Crisis Support', 'Community Mental Health'],
    consultationType: 'In-Person Hospital OPD & 24/7 Teleconsultation',
    bookingUrl: 'https://nimhans.ac.in',
    phone: '080-46110007',
  },
];

const CITIES = ['All Cities', 'Bengaluru', 'Chennai', 'Delhi-NCR', 'Kolkata'];

export default function ProfessionalSupport({ onNavigate }) {
  const { user } = useAuth();
  const { t } = useLanguage();

  const [selectedCity, setSelectedCity] = useState('All Cities');
  const [searchQuery, setSearchQuery] = useState('');
  const [latestCheckin, setLatestCheckin] = useState(null);

  useEffect(() => {
    if (user) {
      api.getLatestCheckin()
        .then((res) => setLatestCheckin(res.checkin))
        .catch(() => setLatestCheckin(null));
    }
  }, [user]);

  const query = searchQuery.toLowerCase().trim();

  const filteredDoctors = VERIFIED_PSYCHIATRISTS.filter((doc) => {
    const matchesCity = selectedCity === 'All Cities' || doc.city === selectedCity;
    const matchesQuery =
      !query ||
      doc.name.toLowerCase().includes(query) ||
      doc.hospital.toLowerCase().includes(query) ||
      doc.city.toLowerCase().includes(query) ||
      doc.specialization.some((s) => s.toLowerCase().includes(query));
    return matchesCity && matchesQuery;
  });

  const stressScore = latestCheckin?.stress_level;
  const showStressNotice = stressScore && stressScore >= 6;

  const content = (
    <main className={user ? 'main-content' : 'main-content no-sidebar'}>
      {!user && <Navbar onNavigate={onNavigate} currentPage="professional_support" />}

      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '4px' }}>
        <h2>Professional Support 🩺</h2>
        <button
          className="btn-secondary"
          onClick={() => onNavigate(user ? 'dashboard' : 'landing')}
        >
          {user ? '← Back to Dashboard' : '← Back to Home'}
        </button>
      </div>
      <p className="aw-muted">
        Connect with verified, qualified Indian psychiatrists and mental healthcare institutions for clinical guidance.
      </p>

      {/* 🚨 Immediate Emergency Helpline Notice (India) */}
      <div
        className="aw-card"
        style={{
          borderLeft: '5px solid #ff6b8b',
          background: '#fff5f6',
          margin: '18px 0',
          padding: '16px',
        }}
      >
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', flexWrap: 'wrap', gap: '12px' }}>
          <div>
            <b style={{ color: '#d63031', fontSize: '1.05rem' }}>🚨 Immediate Crisis &amp; Emergency Notice:</b>
            <div style={{ marginTop: '6px', fontSize: '0.92rem', lineHeight: '1.6', color: 'var(--ink)' }}>
              If you or someone you know is in severe distress or experiencing thoughts of self-harm, please do not wait for a routine appointment. Reach out immediately to verified 24/7 national helplines:
            </div>
            <div style={{ marginTop: '8px', display: 'flex', flexWrap: 'wrap', gap: '10px' }}>
              <a
                href="tel:14416"
                className="btn-primary"
                style={{ padding: '6px 14px', fontSize: '0.85rem', background: '#d63031', borderColor: '#d63031', textDecoration: 'none' }}
              >
                📞 Tele-MANAS: 14416 (24/7 Toll-Free)
              </a>
              <a
                href="tel:18005990019"
                className="btn-secondary"
                style={{ padding: '6px 14px', fontSize: '0.85rem', textDecoration: 'none' }}
              >
                📞 KIRAN: 1800-599-0019
              </a>
              <a
                href="tel:+919999666555"
                className="btn-secondary"
                style={{ padding: '6px 14px', fontSize: '0.85rem', textDecoration: 'none' }}
              >
                📞 Vandrevala Foundation: +91 9999 666 555
              </a>
            </div>
          </div>
        </div>
      </div>

      {/* Supportive recommendation based on existing check-in data */}
      {showStressNotice && (
        <div
          className="aw-card"
          style={{
            borderLeft: '5px solid var(--accent, #7c7ceb)',
            background: 'rgba(124, 124, 235, 0.08)',
            margin: '16px 0',
            padding: '14px 18px',
          }}
        >
          <div style={{ fontWeight: 600, color: 'var(--ink)' }}>
            🌱 Personalized Wellness Reflection:
          </div>
          <div className="aw-muted" style={{ fontSize: '0.92rem', marginTop: '4px', lineHeight: '1.5' }}>
            It looks like you've recently experienced elevated stress levels ({stressScore}/10). If you are finding things difficult to manage, speaking with a licensed psychiatrist or mental-health professional can offer supportive medical guidance and personalized strategies.
          </div>
        </div>
      )}

      {/* Search & City Filter */}
      <div className="aw-card" style={{ margin: '18px 0', padding: '16px' }}>
        <div style={{ display: 'flex', flexDirection: 'column', gap: '14px' }}>
          <div>
            <input
              type="text"
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              placeholder="🔎 Search by psychiatrist name, hospital, city, or specialization (e.g. Anxiety, Depression)..."
            />
          </div>

          <div style={{ display: 'flex', gap: '8px', flexWrap: 'wrap', alignItems: 'center' }}>
            <span style={{ fontSize: '0.85rem', fontWeight: 600, color: 'var(--ink)', marginRight: '4px' }}>
              Filter by City:
            </span>
            {CITIES.map((city) => (
              <button
                key={city}
                className={selectedCity === city ? 'btn-primary' : 'btn-secondary'}
                style={{ padding: '5px 12px', fontSize: '0.85rem' }}
                onClick={() => setSelectedCity(city)}
              >
                {city}
              </button>
            ))}
          </div>
        </div>
      </div>

      {/* Psychiatrists List */}
      <div>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '14px' }}>
          <h3 style={{ margin: 0 }}>Verified Indian Psychiatrists ({filteredDoctors.length})</h3>
          <span className="aw-muted" style={{ fontSize: '0.85rem' }}>
            🇮🇳 India Medical Directory
          </span>
        </div>

        {filteredDoctors.length === 0 ? (
          <div className="aw-card" style={{ textAlign: 'center', padding: '36px 20px' }}>
            <div style={{ fontSize: '2rem', marginBottom: '8px' }}>🔍</div>
            <div style={{ fontWeight: 600, color: 'var(--ink)' }}>No psychiatrists matched your search</div>
            <div className="aw-muted" style={{ fontSize: '0.9rem', marginTop: '6px' }}>
              Try selecting "All Cities" or clearing your search keywords.
            </div>
          </div>
        ) : (
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(320px, 1fr))', gap: '16px' }}>
            {filteredDoctors.map((doc) => (
              <div
                key={doc.id}
                className="aw-card"
                style={{
                  display: 'flex',
                  flexDirection: 'column',
                  justifyContent: 'space-between',
                  height: '100%',
                  padding: '20px',
                }}
              >
                <div>
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
                    <div>
                      <div style={{ fontWeight: 700, fontSize: '1.15rem', color: 'var(--ink)' }}>
                        👨‍⚕️ {doc.name}
                      </div>
                      <div style={{ color: 'var(--accent, #7c7ceb)', fontWeight: 600, fontSize: '0.88rem', marginTop: '2px' }}>
                        {doc.designation}
                      </div>
                    </div>
                    <span
                      style={{
                        background: 'rgba(124, 124, 235, 0.15)',
                        color: 'var(--accent, #7c7ceb)',
                        fontSize: '0.75rem',
                        fontWeight: 700,
                        padding: '3px 8px',
                        borderRadius: '12px',
                      }}
                    >
                      Verified
                    </span>
                  </div>

                  <div style={{ marginTop: '12px', fontSize: '0.9rem', color: 'var(--ink)' }}>
                    <div>🏥 <b>{doc.hospital}</b></div>
                    <div className="aw-muted" style={{ fontSize: '0.85rem', marginTop: '3px' }}>
                      📍 {doc.address}
                    </div>
                    <div style={{ marginTop: '6px', fontSize: '0.85rem' }}>
                      ⏳ <b>Experience:</b> {doc.experience}
                    </div>
                    <div style={{ marginTop: '4px', fontSize: '0.85rem' }}>
                      💻 <b>Consultation:</b> {doc.consultationType}
                    </div>
                  </div>

                  <div style={{ marginTop: '14px' }}>
                    <div style={{ fontSize: '0.8rem', fontWeight: 600, color: 'var(--ink)', marginBottom: '6px' }}>
                      Areas of Expertise:
                    </div>
                    <div style={{ display: 'flex', flexWrap: 'wrap', gap: '6px' }}>
                      {doc.specialization.map((spec, sIdx) => (
                        <span
                          key={sIdx}
                          style={{
                            background: 'var(--bg, #f5f6fa)',
                            border: '1px solid rgba(124,124,235,0.2)',
                            borderRadius: '6px',
                            padding: '2px 8px',
                            fontSize: '0.75rem',
                            color: 'var(--ink)',
                          }}
                        >
                          {spec}
                        </span>
                      ))}
                    </div>
                  </div>
                </div>

                <div style={{ marginTop: '20px', paddingTop: '14px', borderTop: '1px solid rgba(124,124,235,0.15)', display: 'flex', gap: '10px' }}>
                  <a
                    href={doc.bookingUrl}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="btn-primary"
                    style={{ flex: 1, textAlign: 'center', textDecoration: 'none', padding: '8px 12px', fontSize: '0.88rem' }}
                  >
                    📅 Book Appointment
                  </a>
                  {doc.phone && (
                    <a
                      href={`tel:${doc.phone.replace(/[^0-9+]/g, '')}`}
                      className="btn-secondary"
                      style={{ textAlign: 'center', textDecoration: 'none', padding: '8px 12px', fontSize: '0.88rem' }}
                      title={`Call ${doc.hospital}`}
                    >
                      📞 Call
                    </a>
                  )}
                </div>
              </div>
            ))}
          </div>
        )}
      </div>

      <div className="aw-card" style={{ marginTop: '24px', padding: '16px', background: 'var(--card-bg, #ffffff)' }}>
        <div style={{ fontSize: '0.85rem', color: 'var(--ink)', lineHeight: '1.5' }}>
          ℹ️ <b>Directory Information Note:</b> All listed doctors and institutions are qualified medical professionals practicing in India. Appointments are scheduled directly through official hospital portals. AI Wellness Companion does not collect booking fees or transmit personal health records.
        </div>
      </div>
    </main>
  );

  return user ? (
    <div className="app-layout">
      <Sidebar currentPage="professional_support" onNavigate={onNavigate} />
      {content}
    </div>
  ) : (
    content
  );
}
