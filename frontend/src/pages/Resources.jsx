import React, { useState } from 'react';
import Navbar from '../components/Navbar';
import Sidebar from '../components/Sidebar';
import { useAuth } from '../context/AuthContext';
import { useLanguage } from '../context/LanguageContext';

// ==============================================================================
// 1. 24/7 CRISIS HELPLINES (VERIFIED FOR TAMIL NADU & INDIA - ENGLISH ONLY)
// ==============================================================================
const HELPLINES = [
  {
    id: 'emergency-112',
    badge: 'National Emergency',
    badgeColor: '#ef4444',
    title: '🚨 Emergency Services – India',
    numbers: ['112'],
    primaryTel: '112',
    hours: '24/7 (Toll-Free, Always Active)',
    languages: 'Tamil, English, Hindi & Regional Languages',
    desc: 'Unified national emergency helpline across India for immediate police, ambulance, medical rescue, fire, and disaster assistance.',
    actionLabel: 'Call 112',
    actionTel: 'tel:112',
    operator: 'Ministry of Home Affairs & Government of Tamil Nadu',
  },
  {
    id: 'tele-manas-tn',
    badge: 'Tamil Nadu Mental Health',
    badgeColor: '#6366f1',
    title: '🧠 Tele-MANAS – Tamil Nadu Cell',
    numbers: ['14416', '1800-891-4416'],
    primaryTel: '14416',
    hours: '24/7 (Free & Toll-Free)',
    languages: 'Tamil & English',
    desc: 'Government of India’s flagship mental health service with a dedicated Tamil Nadu state center. Provides free, confidential crisis tele-counselling, psychological first aid, and psychiatric referral.',
    actionLabel: 'Call 14416',
    actionTel: 'tel:14416',
    secondaryLabel: 'Call 1800-891-4416',
    secondaryTel: 'tel:18008914416',
    operator: 'National Health Mission Tamil Nadu & NIMHANS',
  },
  {
    id: 'sneha-chennai',
    badge: 'Suicide Prevention',
    badgeColor: '#f59e0b',
    title: '💛 Sneha Suicide Prevention – Chennai',
    numbers: ['044-24640050', '044-24640060'],
    primaryTel: '04424640050',
    hours: '24/7 (Confidential & Compassionate)',
    languages: 'Tamil & English',
    desc: 'Pioneering volunteer-driven crisis helpline in Chennai providing unconditional, non-judgmental emotional support to anyone experiencing distress, depression, or suicidal thoughts.',
    actionLabel: 'Call 044-24640050',
    actionTel: 'tel:04424640050',
    secondaryLabel: 'Call 044-24640060',
    secondaryTel: 'tel:04424640060',
    operator: 'Sneha Suicide Prevention Centre, Chennai, Tamil Nadu',
  },
  {
    id: 'tn-health-104',
    badge: 'State Health Helpline',
    badgeColor: '#10b981',
    title: '📞 Tamil Nadu Health & Student Helpline',
    numbers: ['104'],
    primaryTel: '104',
    hours: '24/7 (Toll-Free across Tamil Nadu)',
    languages: 'Tamil & English',
    desc: 'Government of Tamil Nadu 24/7 official helpline for healthcare guidance, tele-counselling, student exam stress management, and emotional distress support.',
    actionLabel: 'Call 104',
    actionTel: 'tel:104',
    operator: 'Health & Family Welfare Department, Government of Tamil Nadu',
  },
  {
    id: 'nimhans-helpline',
    badge: 'Apex Psychiatry Centre',
    badgeColor: '#8b5cf6',
    title: '🏥 NIMHANS Mental Health Support',
    numbers: ['080-46110007'],
    primaryTel: '08046110007',
    hours: '24/7 (Toll-Free Psychosocial Support)',
    languages: 'Tamil, English, Hindi, Kannada, Telugu',
    desc: 'National Institute of Mental Health and Neuro Sciences premier helpline offering professional psychiatric consultations, psychotherapy advice, and crisis management.',
    actionLabel: 'Call 080-46110007',
    actionTel: 'tel:08046110007',
    operator: 'NIMHANS, Institute of National Importance, Government of India',
  },
  {
    id: 'kiran-helpline',
    badge: 'National Helpline',
    badgeColor: '#0ea5e9',
    title: '🌟 KIRAN Mental Health Helpline',
    numbers: ['1800-599-0019'],
    primaryTel: '18005990019',
    hours: '24/7 (Toll-Free)',
    languages: 'Tamil, English, Hindi & 10+ Languages',
    desc: 'National mental health helpline by the Ministry of Social Justice & Empowerment providing early screening, psychological first aid, and crisis de-escalation.',
    actionLabel: 'Call 1800-599-0019',
    actionTel: 'tel:18005990019',
    operator: 'Ministry of Social Justice and Empowerment, Government of India',
  },
  {
    id: 'vandrevala-foundation',
    badge: 'Free Psychological Counselling',
    badgeColor: '#059669',
    title: '🤝 Vandrevala Foundation',
    numbers: ['+91 9999 666 555'],
    primaryTel: '+919999666555',
    hours: '24/7 (Counselling & WhatsApp Support)',
    languages: 'Tamil, English, Hindi & Regional Languages',
    desc: 'Free, professional 24/7 mental health counseling staffed by experienced clinical psychologists and counselors for anxiety, depression, and personal crisis.',
    actionLabel: 'Call +91 9999 666 555',
    actionTel: 'tel:+919999666555',
    operator: 'Vandrevala Foundation for Mental Health',
  },
];

// ==============================================================================
// 2. ARTICLES & GUIDES (GENUINE INDIAN & TAMIL NADU SOURCES - ENGLISH ONLY)
// ==============================================================================
const ARTICLES = [
  {
    title: 'Understanding Stress Among College Students in India & Tamil Nadu',
    source: 'NIMHANS Centre for Well-Being & WHO India',
    url: 'https://nimhans.ac.in/',
    body: 'College students across engineering, arts, and medical colleges in Tamil Nadu often encounter unique psychological pressures: demanding semester curricula, hostel adjustments away from family, intense placement competition, and high expectations. Research by NIMHANS indicates that prolonged unmanaged academic stress elevates anxiety and disrupts sleep architecture. Recognizing stress early through active emotional check-ins, balanced study routines, and campus counseling prevents burnout.',
  },
  {
    title: 'Managing Academic Pressure & Exam Anxiety',
    source: 'National Health Mission Tamil Nadu (104 Helpline)',
    url: 'https://nhm.tn.gov.in/',
    body: 'Exam anxiety is a normal physiological reaction before University semester exams, NEET, GATE, or TNPSC. However, acute panic impairs working memory retrieval in the prefrontal cortex. To manage exam stress: practice the Pomodoro technique (25 minutes focus followed by a 5-minute break), avoid last-minute sleep deprivation, stay hydrated, and use box breathing before entering the exam hall. Students in Tamil Nadu can also call 104 for dedicated exam stress counselling.',
  },
  {
    title: 'Depression Awareness & Early Warning Signs',
    source: 'Ministry of Health and Family Welfare (MoHFW), India',
    url: 'https://main.mohfw.gov.in/',
    body: 'Clinical depression is vastly different from temporary sadness. Key clinical warning signs include: persistent low mood exceeding two consecutive weeks, loss of interest in hobbies (anhedonia), insomnia or excessive sleeping, chronic fatigue, unexplained somatic pains, feelings of worthlessness, and social withdrawal. Acknowledging depression as a treatable health condition is the first crucial step toward recovery.',
  },
  {
    title: 'Mental Health Awareness & Overcoming Social Stigma in Tamil Nadu',
    source: 'District Mental Health Programme (DMHP), Tamil Nadu',
    url: 'https://nhm.tn.gov.in/en/district-mental-health-programme',
    body: 'In many communities, societal hesitation and stigma prevent young adults from consulting psychologists or psychiatrists. Mental health is a normal component of overall human healthcare, just like cardiac or dental health. Tamil Nadu is pioneering district-level de-stigmatization through the District Mental Health Programme (DMHP). Seeking counseling is an act of courage, wisdom, and self-care.',
  },
  {
    title: 'How to Access Government Mental Health Services in Tamil Nadu',
    source: 'Institute of Mental Health (IMH), Kilpauk, Chennai & NHM',
    url: 'https://nhm.tn.gov.in/',
    body: 'Tamil Nadu offers comprehensive mental healthcare across all 38 districts through the District Mental Health Programme (DMHP). Patients can walk into psychiatry Outpatient Departments (OPD) at Government Medical College Hospitals (e.g., Madras Medical College, Kilpauk, Stanley, Madurai, Coimbatore, Tiruchirappalli) or District Headquarter Hospitals. The premier state institute is the historic Institute of Mental Health (IMH) in Kilpauk, Chennai. Consultations, psychotherapy, and essential medications are provided free of cost.',
  },
  {
    title: 'When and How to Seek Professional Counselling',
    source: 'Tele-MANAS National Centre & NIMHANS',
    url: 'https://telemanas.mohfw.gov.in/',
    body: 'Consult a professional mental health counselor or clinical psychologist when: feelings of dread or sadness persist for more than 14 days, personal hygiene or college attendance slips, feelings of despair arise, or you rely on harmful coping mechanisms. You can initiate confidential support anytime by calling Tele-MANAS at 14416 from any phone.',
  },
  {
    title: 'Daily Mental Wellness & Balanced Living',
    source: 'WHO India & National Health Mission Tamil Nadu',
    url: 'https://www.who.int/india/health-topics/mental-health',
    body: 'Daily habits to sustain peaceful mental wellness: prioritizing 7 to 8 hours of restorative sleep, getting morning sunlight, maintaining balanced hydration and nutrition, taking structured study breaks, and limiting social media doomscrolling. Opening up and speaking with trusted friends or family members significantly eases emotional pressure. For free professional guidance anytime, call Tele-MANAS at 14416.',
  },
];

// ==============================================================================
// 3. MINDFULNESS & BREATHING PRACTICES (ENGLISH ONLY)
// ==============================================================================
const MINDFULNESS_GUIDES = [
  {
    id: 'box-breathing',
    title: '4-4-4-4 Box Breathing Technique',
    category: 'Acute Anxiety & Exam Calmness',
    time: '3–5 Minutes',
    desc: 'Equal-ratio breathing resets the autonomic nervous system, lowers heart rate, and restores cognitive clarity under exam stress.',
    steps: [
      '1. Inhale slowly and deeply through your nose for 4 seconds.',
      '2. Hold your breath gently for 4 seconds without straining.',
      '3. Exhale smoothly and completely through your mouth for 4 seconds.',
      '4. Rest in quiet stillness for 4 seconds before beginning the next cycle.',
    ],
  },
  {
    id: 'grounding-54321',
    title: '5-4-3-2-1 Sensory Grounding Technique',
    category: 'Panic Relief & Present Moment Anchor',
    time: '2–4 Minutes',
    desc: 'Pulls sensory focus away from catastrophic thoughts by anchoring awareness to physical objects in your immediate room.',
    steps: [
      '👁️ 5 Things you can see: Look for subtle details in your room (desk surface, book spine, light reflection).',
      '🖐️ 4 Things you can physically feel: The chair supporting you, fabric of your clothes, solid floor beneath your feet.',
      '👂 3 Things you can hear: The fan hum, breeze outside, or distant traffic sounds.',
      '👃 2 Things you can smell: Hand wash, fresh morning air, notebook paper, or the aroma of tea.',
      '👅 1 Thing you can taste or positive truth: A sip of cool water, or repeating: "I am safe in this present moment."',
    ],
  },
  {
    id: 'exam-stress-relief',
    title: 'Exam Stress Relief & Guided Somatic Relaxation',
    category: 'Student Study & Academic Anxiety',
    time: '3 Minutes',
    desc: 'Release micro-contractions in muscles before entering study halls, laboratory tests, or examination centers.',
    steps: [
      '1. Unclench your jaw and drop your tongue away from the roof of your mouth.',
      '2. Drop your shoulders two inches down and away from your ears.',
      '3. Take two deep physiological sighs: a double inhale through your nose, followed by a long, slow sighing exhale through your mouth.',
      '4. Remind yourself: "I have prepared, and I will take this one question and one step at a time."',
    ],
  },
  {
    id: 'sleep-relaxation-nsdr',
    title: 'Sleep Relaxation & Non-Sleep Deep Rest (NSDR)',
    category: 'Bedtime Insomnia & Restorative Rest',
    time: '5–10 Minutes',
    desc: 'The 4-7-8 relaxing breath stimulates the parasympathetic vagus nerve, calming racing thoughts before sleep.',
    steps: [
      '1. Inhale quietly through your nose for 4 seconds.',
      '2. Hold your breath gently for 7 seconds.',
      '3. Exhale completely through your mouth with a soft whoosh for 8 seconds.',
      '4. Repeat for 4 full cycles before turning off lamps for bedtime rest.',
    ],
  },
  {
    id: 'daily-mindfulness',
    title: 'Daily Mindfulness Practice',
    category: 'Everyday Emotional Balance',
    time: '2–3 Minutes',
    desc: 'Micro-mindfulness exercises during study intervals, coffee pauses, or walking across campus.',
    steps: [
      '1. Pause whatever you are doing for 60 seconds.',
      '2. Notice the warmth of your cup or the firm weight of your footsteps on the path.',
      '3. Acknowledge your current emotions without judging them as good or bad.',
      '4. Proceed with your day with patience, kindness, and clear priorities.',
    ],
  },
];

// ==============================================================================
// 4. FREQUENTLY ASKED QUESTIONS (ENGLISH ONLY)
// ==============================================================================
const FAQS = [
  {
    q: 'How can I contact a mental health counsellor in Tamil Nadu?',
    a: 'You can immediately speak with a trained mental health counselor 24/7 by calling 14416 (Tele-MANAS Tamil Nadu, toll-free) or dialing 104 (Tamil Nadu State Health Helpline). Both services provide free, confidential tele-counseling. For in-person consultations, you can visit the psychiatry outpatient department (OPD) of your nearest Government District Headquarters Hospital, Government Medical College Hospital, or the Institute of Mental Health (IMH) in Kilpauk, Chennai.',
  },
  {
    q: 'What is Tele-MANAS and how does it operate in Tamil Nadu?',
    a: 'Tele-MANAS (Tele Mental Health Assistance and Networking Across States) is the Government of India’s 24/7 toll-free national tele-mental health programme, coordinated by NIMHANS. In Tamil Nadu, calls to 14416 or 1800-891-4416 connect directly to qualified clinical psychologists, psychiatrists, and trained counselors stationed in state cells, offering immediate psychological first aid and referral services.',
  },
  {
    q: 'Is mental health counselling available for free in Tamil Nadu?',
    a: 'Yes, 100% free. Tele-MANAS (14416), Tamil Nadu Health Helpline (104), and Sneha Suicide Prevention (044-24640050) do not charge any fees. Furthermore, outpatient consultations, psychological evaluations, and essential psychiatric medications are provided free of cost at all Tamil Nadu Government Medical College Hospitals and District Mental Health Programme (DMHP) clinics under the National Health Mission.',
  },
  {
    q: 'How can college students get mental health support in Tamil Nadu?',
    a: 'College students experiencing exam anxiety, academic pressure, career uncertainty, or emotional distress can reach out to their institutional student guidance cell, dial 104 (which features dedicated student examination counseling protocols), or call Tele-MANAS (14416) anytime. Consultations are strictly confidential and do not impact academic records.',
  },
  {
    q: 'What should I do if someone is experiencing an acute mental health crisis?',
    a: 'Stay calm and never leave the person alone. Listen with empathy and without judgment or lecturing. Ensure their immediate environment is safe. Immediately dial 112 (Emergency Services across India) or 14416 (Tele-MANAS) or 044-24640050 (Sneha Chennai). If there is imminent danger of physical harm, safely escort them to the nearest Government Hospital casualty/emergency department.',
  },
  {
    q: 'Where can I find government mental health services in Tamil Nadu?',
    a: 'Government mental healthcare is active in all 38 districts of Tamil Nadu through the District Mental Health Programme (DMHP) operating in District Headquarter Hospitals and Primary Health Centres. The state’s apex institution is the Institute of Mental Health (IMH) located in Kilpauk, Chennai (established in 1794, one of Asia’s oldest psychiatric institutions). All Government Medical Colleges (e.g., Madras Medical College, Stanley, Kilpauk, Madurai, Coimbatore, Tiruchirappalli) have full-time psychiatry clinics.',
  },
  {
    q: 'When should I seek professional help instead of managing on my own?',
    a: 'You should seek professional support if feelings of deep sadness, anxiety, dread, or emotional numbness persist for more than 2 consecutive weeks, if your academic performance or college attendance drops sharply, if your sleep or appetite is severely disrupted, or if you feel overwhelmed by hopeless thoughts. Getting help early prevents minor distress from escalating into clinical depression.',
  },
];

// ==============================================================================
// COMPONENT
// ==============================================================================
export default function Resources({ onNavigate }) {
  const { user } = useAuth();
  const { t } = useLanguage();

  const [activeTab, setActiveTab] = useState('helplines');
  const [searchQuery, setSearchQuery] = useState('');
  const [expandedArticles, setExpandedArticles] = useState({});
  const [expandedFaqs, setExpandedFaqs] = useState({});

  const toggleArticle = (i) => {
    setExpandedArticles((prev) => ({ ...prev, [i]: !prev[i] }));
  };

  const toggleFaq = (i) => {
    setExpandedFaqs((prev) => ({ ...prev, [i]: !prev[i] }));
  };

  const query = searchQuery.toLowerCase().trim();

  const filteredHelplines = HELPLINES.filter(
    (h) =>
      !query ||
      h.title.toLowerCase().includes(query) ||
      h.desc.toLowerCase().includes(query) ||
      h.numbers.some((n) => n.includes(query)) ||
      h.languages.toLowerCase().includes(query) ||
      h.operator.toLowerCase().includes(query)
  );

  const filteredArticles = ARTICLES.filter(
    (a) =>
      !query ||
      a.title.toLowerCase().includes(query) ||
      a.body.toLowerCase().includes(query) ||
      a.source.toLowerCase().includes(query)
  );

  const filteredMindfulness = MINDFULNESS_GUIDES.filter(
    (m) =>
      !query ||
      m.title.toLowerCase().includes(query) ||
      m.category.toLowerCase().includes(query) ||
      m.desc.toLowerCase().includes(query)
  );

  const filteredFaqs = FAQS.filter(
    (f) =>
      !query ||
      f.q.toLowerCase().includes(query) ||
      f.a.toLowerCase().includes(query)
  );

  const content = (
    <main className={user ? 'main-content' : 'main-content no-sidebar'}>
      {!user && <Navbar onNavigate={onNavigate} currentPage="resources" />}

      {/* Header & Breadcrumb */}
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '4px', flexWrap: 'wrap', gap: '10px' }}>
        <div>
          <h2 style={{ margin: 0, fontSize: '1.75rem', fontWeight: 800, color: 'var(--ink)' }}>
            {t('resources_title')}
          </h2>
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginTop: '4px' }}>
            <span
              style={{
                display: 'inline-flex',
                alignItems: 'center',
                gap: '5px',
                padding: '3px 10px',
                borderRadius: '999px',
                fontSize: '0.8rem',
                fontWeight: 700,
                background: 'rgba(124,124,235,0.12)',
                color: 'var(--accent)',
              }}
            >
              📍 Tamil Nadu, India
            </span>
            <span className="aw-muted" style={{ fontSize: '0.9rem' }}>
              • Verified Government &amp; Institutional Support
            </span>
          </div>
        </div>
        <button
          className="btn-secondary"
          onClick={() => onNavigate(user ? 'dashboard' : 'landing')}
        >
          {user ? '← Back to Dashboard' : '← Back to Home'}
        </button>
      </div>

      <p className="aw-muted" style={{ marginTop: '8px', fontSize: '0.94rem' }}>
        {t('resources_subtitle')}
      </p>

      {/* Emergency Crisis Notice */}
      <div
        className="aw-card"
        style={{
          borderLeft: '5px solid #ef4444',
          background: 'linear-gradient(135deg, rgba(254,242,242,0.9), rgba(255,255,255,0.9))',
          margin: '18px 0',
          padding: '16px 20px',
          borderRadius: '16px',
        }}
      >
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: '8px' }}>
          <b style={{ color: '#dc2626', fontSize: '1.05rem' }}>
            ⚠️ 24/7 Immediate Crisis Assistance – Tamil Nadu, India:
          </b>
          <span style={{ fontSize: '0.85rem', fontWeight: 700, color: '#dc2626', background: '#fee2e2', padding: '3px 8px', borderRadius: '6px' }}>
            Toll-Free Numbers
          </span>
        </div>
        <div style={{ fontSize: '0.92rem', color: '#374151', lineHeight: 1.6, marginTop: '6px' }}>
          This AI Wellness companion is a supportive self-care tool, <b>not clinical emergency healthcare or medical diagnosis</b>.
          If you or someone you know is in immediate danger, distress, or having thoughts of self-harm, please connect with 
          <strong> Tele-MANAS (14416 / 1800-891-4416)</strong>, <strong>Sneha Chennai (044-24640050)</strong>, or 
          <strong> National Emergency (112)</strong> immediately.
        </div>
      </div>

      {/* Search Input Bar */}
      <div style={{ margin: '18px 0' }}>
        <input
          type="text"
          value={searchQuery}
          onChange={(e) => setSearchQuery(e.target.value)}
          placeholder="🔎 Search by topic, helpline number, college stress, exam anxiety (e.g., 14416, Sneha, 104, depression)..."
          style={{ width: '100%', padding: '12px 18px', borderRadius: '12px', fontSize: '0.95rem' }}
        />
      </div>

      {/* Category Tabs */}
      <div className="tabs-container">
        {[
          { id: 'helplines', label: '🚨 24/7 Crisis Helplines' },
          { id: 'articles', label: '📚 Articles & Guides' },
          { id: 'mindfulness', label: '🧘 Mindfulness & Breathing' },
          { id: 'faqs', label: '❓ Frequently Asked Questions' },
        ].map((tab) => (
          <button
            key={tab.id}
            className={`tab-btn ${activeTab === tab.id ? 'active' : ''}`}
            onClick={() => setActiveTab(tab.id)}
          >
            {tab.label}
          </button>
        ))}
      </div>

      {/* ==================================================================== */}
      {/* TAB 1: 24/7 CRISIS HELPLINES */}
      {/* ==================================================================== */}
      {activeTab === 'helplines' && (
        <div>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '14px' }}>
            <h3 style={{ margin: 0, color: 'var(--ink)' }}>
              Verified 24/7 Helplines (Tamil Nadu &amp; India)
            </h3>
            <span className="aw-muted" style={{ fontSize: '0.85rem' }}>
              Showing {filteredHelplines.length} verified helplines
            </span>
          </div>

          <div style={{ display: 'flex', flexDirection: 'column', gap: '14px' }}>
            {filteredHelplines.map((h) => (
              <div
                key={h.id}
                className="aw-card"
                style={{
                  display: 'flex',
                  justifyContent: 'space-between',
                  alignItems: 'center',
                  flexWrap: 'wrap',
                  gap: '16px',
                  borderLeft: `4px solid ${h.badgeColor || '#7c7ceb'}`,
                }}
              >
                <div style={{ flex: 1, minWidth: '260px' }}>
                  <div style={{ display: 'flex', alignItems: 'center', gap: '8px', flexWrap: 'wrap' }}>
                    <span style={{ fontWeight: 800, fontSize: '1.1rem', color: 'var(--ink)' }}>
                      {h.title}
                    </span>
                    <span
                      style={{
                        fontSize: '0.75rem',
                        fontWeight: 700,
                        padding: '2px 8px',
                        borderRadius: '6px',
                        background: 'rgba(124,124,235,0.1)',
                        color: h.badgeColor || 'var(--accent)',
                      }}
                    >
                      {h.badge}
                    </span>
                  </div>

                  <div style={{ display: 'flex', gap: '14px', alignItems: 'center', margin: '6px 0 4px', flexWrap: 'wrap' }}>
                    <span style={{ fontWeight: 800, fontSize: '1.15rem', color: '#6366f1' }}>
                      📞 {h.numbers.join(' / ')}
                    </span>
                    <span style={{ fontSize: '0.82rem', color: '#059669', fontWeight: 600 }}>
                      🕒 {h.hours}
                    </span>
                    <span style={{ fontSize: '0.82rem', color: 'var(--muted)' }}>
                      🗣️ {h.languages}
                    </span>
                  </div>

                  <div className="aw-muted" style={{ fontSize: '0.9rem', lineHeight: 1.5, marginTop: '4px' }}>
                    {h.desc}
                  </div>
                  <div style={{ fontSize: '0.78rem', color: 'var(--muted)', marginTop: '4px', fontStyle: 'italic' }}>
                    Organized by: {h.operator}
                  </div>
                </div>

                <div style={{ display: 'flex', flexDirection: 'column', gap: '8px', minWidth: '150px' }}>
                  <a
                    href={h.actionTel}
                    className="btn-primary"
                    style={{
                      textDecoration: 'none',
                      textAlign: 'center',
                      padding: '8px 16px',
                      fontSize: '0.92rem',
                      fontWeight: 700,
                      borderRadius: '10px',
                      display: 'inline-block',
                    }}
                  >
                    📞 {h.actionLabel}
                  </a>
                  {h.secondaryTel && (
                    <a
                      href={h.secondaryTel}
                      className="btn-secondary"
                      style={{
                        textDecoration: 'none',
                        textAlign: 'center',
                        padding: '6px 14px',
                        fontSize: '0.85rem',
                        borderRadius: '10px',
                        display: 'inline-block',
                      }}
                    >
                      📞 {h.secondaryLabel}
                    </a>
                  )}
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* ==================================================================== */}
      {/* TAB 2: ARTICLES & GUIDES */}
      {/* ==================================================================== */}
      {activeTab === 'articles' && (
        <div>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '14px' }}>
            <h3 style={{ margin: 0, color: 'var(--ink)' }}>
              Mental Health Psychoeducation &amp; Guides
            </h3>
            <span className="aw-muted" style={{ fontSize: '0.85rem' }}>
              Showing {filteredArticles.length} guides
            </span>
          </div>

          <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
            {filteredArticles.map((a, i) => (
              <div key={i} className="aw-card">
                <div
                  style={{
                    display: 'flex',
                    justifyContent: 'space-between',
                    alignItems: 'center',
                    cursor: 'pointer',
                    fontWeight: 700,
                  }}
                  onClick={() => toggleArticle(i)}
                >
                  <span style={{ fontSize: '1.02rem', color: 'var(--ink)' }}>📖 {a.title}</span>
                  <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
                    <span style={{ fontSize: '0.78rem', color: 'var(--accent)', fontWeight: 600 }}>
                      {a.source}
                    </span>
                    <span style={{ fontSize: '0.85rem' }}>{expandedArticles[i] ? '▲' : '▼'}</span>
                  </div>
                </div>

                {expandedArticles[i] && (
                  <div style={{ marginTop: '14px', paddingTop: '12px', borderTop: '1px solid rgba(124,124,235,0.15)' }}>
                    <p style={{ margin: 0, lineHeight: 1.7, fontSize: '0.92rem', color: 'var(--ink)' }}>
                      {a.body}
                    </p>
                    <div style={{ marginTop: '12px', display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: '8px' }}>
                      <span style={{ fontSize: '0.8rem', color: 'var(--muted)' }}>
                        Source Institution: <strong>{a.source}</strong>
                      </span>
                      <a
                        href={a.url}
                        target="_blank"
                        rel="noopener noreferrer"
                        style={{
                          fontSize: '0.82rem',
                          color: '#6366f1',
                          fontWeight: 700,
                          textDecoration: 'none',
                        }}
                      >
                        Visit Official Resource Portal ↗
                      </a>
                    </div>
                  </div>
                )}
              </div>
            ))}
          </div>
        </div>
      )}

      {/* ==================================================================== */}
      {/* TAB 3: MINDFULNESS & BREATHING */}
      {/* ==================================================================== */}
      {activeTab === 'mindfulness' && (
        <div style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
          <div>
            <h3 style={{ margin: '0 0 6px', color: 'var(--ink)' }}>
              Interactive Mindfulness &amp; Somatic Calmness Practices
            </h3>
            <p className="aw-muted" style={{ margin: 0, fontSize: '0.9rem' }}>
              Evidence-based respiratory and mindfulness techniques for emotional regulation and academic focus.
            </p>
          </div>

          <div style={{ display: 'flex', flexDirection: 'column', gap: '14px' }}>
            {filteredMindfulness.map((m) => (
              <div key={m.id} className="aw-card">
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', flexWrap: 'wrap', gap: '8px' }}>
                  <div>
                    <h4 style={{ margin: '0 0 4px', fontSize: '1.1rem', color: 'var(--ink)' }}>
                      {m.title}
                    </h4>
                    <span
                      style={{
                        fontSize: '0.78rem',
                        fontWeight: 700,
                        padding: '2px 8px',
                        borderRadius: '6px',
                        background: 'rgba(124,124,235,0.1)',
                        color: 'var(--accent)',
                      }}
                    >
                      {m.category} • ⏱️ {m.time}
                    </span>
                  </div>
                </div>

                <div style={{ margin: '10px 0', fontSize: '0.9rem', lineHeight: 1.6, color: 'var(--ink)' }}>
                  {m.desc}
                </div>

                <div style={{ background: 'rgba(124,124,235,0.04)', borderRadius: '12px', padding: '14px 16px', marginTop: '10px' }}>
                  <div style={{ fontWeight: 700, fontSize: '0.88rem', color: 'var(--ink)', marginBottom: '8px' }}>
                    Step-by-Step Instructions:
                  </div>
                  <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
                    {m.steps.map((step, sIdx) => (
                      <div key={sIdx} style={{ fontSize: '0.88rem', lineHeight: 1.5, color: 'var(--ink)', fontWeight: 500 }}>
                        {step}
                      </div>
                    ))}
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* ==================================================================== */}
      {/* TAB 4: FREQUENTLY ASKED QUESTIONS */}
      {/* ==================================================================== */}
      {activeTab === 'faqs' && (
        <div>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '14px' }}>
            <h3 style={{ margin: 0, color: 'var(--ink)' }}>
              Frequently Asked Questions (Tamil Nadu, India)
            </h3>
            <span className="aw-muted" style={{ fontSize: '0.85rem' }}>
              Showing {filteredFaqs.length} questions
            </span>
          </div>

          <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
            {filteredFaqs.map((f, i) => (
              <div key={i} className="aw-card">
                <div
                  style={{
                    display: 'flex',
                    justifyContent: 'space-between',
                    alignItems: 'center',
                    cursor: 'pointer',
                    fontWeight: 700,
                  }}
                  onClick={() => toggleFaq(i)}
                >
                  <span style={{ fontSize: '1rem', color: 'var(--ink)', lineHeight: 1.5 }}>
                    ❓ {f.q}
                  </span>
                  <span style={{ minWidth: '20px', textAlign: 'right' }}>
                    {expandedFaqs[i] ? '▲' : '▼'}
                  </span>
                </div>
                {expandedFaqs[i] && (
                  <div style={{ marginTop: '12px', paddingTop: '10px', borderTop: '1px solid rgba(124,124,235,0.12)' }}>
                    <p style={{ margin: 0, lineHeight: 1.7, fontSize: '0.92rem', color: 'var(--ink)' }}>
                      {f.a}
                    </p>
                  </div>
                )}
              </div>
            ))}
          </div>
        </div>
      )}
    </main>
  );

  return user ? (
    <div className="app-layout">
      <Sidebar currentPage="resources" onNavigate={onNavigate} />
      {content}
    </div>
  ) : (
    content
  );
}
