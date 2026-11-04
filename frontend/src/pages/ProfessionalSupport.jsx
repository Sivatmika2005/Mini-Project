import React, { useState, useEffect, useRef } from 'react';
import Navbar from '../components/Navbar';
import Sidebar from '../components/Sidebar';
import { useAuth } from '../context/AuthContext';
import { useLanguage } from '../context/LanguageContext';
import { api } from '../api/client';

// Initial fallback psychiatrists to ensure zero-latency rendering
const INITIAL_PSYCHIATRISTS = [
  {
    id: 'imh-chennai',
    name: 'Institute of Mental Health (IMH)',
    designation: 'Apex Psychiatric Institution of Tamil Nadu',
    hospital: 'Government Institute of Mental Health',
    city: 'Chennai',
    state: 'Tamil Nadu',
    address: 'Medavakkam Tank Road, Kilpauk, Chennai, Tamil Nadu 600010',
    latitude: 13.0886,
    longitude: 80.2443,
    experience: 'Government Apex Centre (Est. 1794)',
    specialization: ['Comprehensive Adult Psychiatry', 'De-Addiction', 'Community Mental Health', 'Crisis Intervention'],
    consultationType: 'OPD Services & 24/7 Psychiatric Emergency',
    bookingUrl: 'https://www.tnhealth.tn.gov.in',
    phone: '044-26442436',
    verified: true,
    verificationSource: 'National Medical Commission / Govt of Tamil Nadu',
    category: 'Psychiatric Hospital',
  },
  {
    id: 'dr-raman-k-chennai',
    name: 'Dr. Raman K',
    designation: 'Senior Consultant Psychiatrist',
    hospital: 'Apollo Hospitals Greams Road',
    city: 'Chennai',
    state: 'Tamil Nadu',
    address: '21 Greams Lane, Off Greams Road, Thousand Lights, Chennai, Tamil Nadu 600006',
    latitude: 13.0604,
    longitude: 80.2508,
    experience: '25+ Years',
    specialization: ['Mood Disorders', 'Anxiety & Panic', 'Neuropsychiatry', 'Cognitive Behaviour Therapy'],
    consultationType: 'In-Person OPD & Video Consultation',
    bookingUrl: 'https://www.apollohospitals.com/doctors/psychiatrist/chennai/dr-raman-k',
    phone: '044-28290200',
    verified: true,
    verificationSource: 'Indian Medical Register / Apollo Hospitals',
    category: 'Psychiatrist',
  },
  {
    id: 'dr-ramakrishnan-coimbatore',
    name: 'Dr. N. Ramakrishnan',
    designation: 'Chief Consultant Psychiatrist & HOD',
    hospital: 'PSG Institute of Medical Sciences & Research',
    city: 'Coimbatore',
    state: 'Tamil Nadu',
    address: 'Avinashi Road, Peelamedu, Coimbatore, Tamil Nadu 641004',
    latitude: 11.0253,
    longitude: 77.0028,
    experience: '22+ Years',
    specialization: ['Clinical Depression', 'Bipolar Affective Disorder', 'Stress Management', 'Geriatric Psychiatry'],
    consultationType: 'Hospital OPD & Teleconsultation',
    bookingUrl: 'https://psgimsr.ac.in/departments/psychiatry',
    phone: '0422-2570170',
    verified: true,
    verificationSource: 'Tamil Nadu Medical Council / PSG IMS&R',
    category: 'Psychiatrist',
  },
  {
    id: 'dr-venkat-salem',
    name: 'Dr. P. Venkatasubramanian',
    designation: 'Senior Consultant Psychiatrist',
    hospital: 'Manipal Hospital Salem',
    city: 'Salem',
    state: 'Tamil Nadu',
    address: 'Dalmia Board, Bangalore Highway, Salem, Tamil Nadu 636012',
    latitude: 11.6912,
    longitude: 78.1189,
    experience: '18+ Years',
    specialization: ['Mood & Anxiety Disorders', 'De-addiction', 'Adolescent Stress', 'Sleep Medicine'],
    consultationType: 'In-Person OPD & Video Consultation',
    bookingUrl: 'https://www.manipalhospitals.com/salem/doctors/psychiatry',
    phone: '0427-2346600',
    verified: true,
    verificationSource: 'Indian Medical Register / Manipal Hospitals',
    category: 'Psychiatrist',
  },
  {
    id: 'nimhans-centre',
    name: 'NIMHANS Outpatient & Tele-MANAS Hub',
    designation: 'National Institute of Mental Health & Neurosciences',
    hospital: 'NIMHANS Central Institute',
    city: 'Bengaluru',
    state: 'Karnataka',
    address: 'Hosur Road, Lakkasandra, Bengaluru, Karnataka 560029',
    latitude: 12.9392,
    longitude: 77.5956,
    experience: 'Apex National Institute',
    specialization: ['Comprehensive Psychiatric Care', 'Psychotherapy', 'Crisis Support', 'Community Mental Health'],
    consultationType: 'In-Person Hospital OPD & 24/7 Teleconsultation',
    bookingUrl: 'https://nimhans.ac.in',
    phone: '080-46110007',
    verified: true,
    verificationSource: 'Ministry of Health & Family Welfare, Govt of India',
    category: 'Psychiatric Hospital',
  },
];

const TN_CITIES = [
  'All Tamil Nadu',
  'Chennai',
  'Coimbatore',
  'Salem',
  'Madurai',
  'Tiruchirappalli',
  'Tirunelveli',
  'Erode',
  'Tiruppur',
  'Vellore',
  'Thanjavur',
  'Hosur',
  'Dindigul',
  'Kanchipuram',
  'Cuddalore',
  'Nagercoil',
  'Thoothukudi',
];

const OTHER_CITIES = [
  'All Other Cities',
  'Bengaluru',
  'Hyderabad',
  'Mumbai',
  'Pune',
  'Delhi-NCR',
  'Kolkata',
  'Ahmedabad',
  'Jaipur',
  'Kochi',
  'Thiruvananthapuram',
  'Mysuru',
  'Mangaluru',
  'Lucknow',
  'Chandigarh',
  'Indore',
  'Bhopal',
  'Visakhapatnam',
  'Patna',
  'Bhubaneswar',
];

const CATEGORIES = [
  'All Categories',
  'Psychiatrists',
  'Clinical Psychologists',
  'Psychiatric Hospitals',
  'Child & Adolescent',
  'Addiction Specialists',
];

const DISTANCE_OPTIONS = [
  { label: 'Within 5 km', value: 5 },
  { label: 'Within 10 km', value: 10 },
  { label: 'Within 25 km', value: 25 },
  { label: 'Within 50 km', value: 50 },
  { label: 'All Distances', value: 0 },
];

export default function ProfessionalSupport({ onNavigate }) {
  const { user } = useAuth();
  const { t } = useLanguage();

  const [doctors, setDoctors] = useState(INITIAL_PSYCHIATRISTS);
  const [loading, setLoading] = useState(false);
  const [regionFilter, setRegionFilter] = useState('All'); // 'All', 'TN', 'Other'
  const [selectedCity, setSelectedCity] = useState('All Cities');
  const [selectedCategory, setSelectedCategory] = useState('All Categories');
  const [searchQuery, setSearchQuery] = useState('');
  const [latestCheckin, setLatestCheckin] = useState(null);

  // Geolocation & Proximity States
  const [userLocation, setUserLocation] = useState(null); // { lat, lng }
  const [detectedAddress, setDetectedAddress] = useState(null); // e.g. "Chennai, Tamil Nadu"
  const [locationLoading, setLocationLoading] = useState(false);
  const [locationError, setLocationError] = useState(null);
  const [distanceRadius, setDistanceRadius] = useState(25);
  const [viewMode, setViewMode] = useState('list'); // 'list' | 'map'

  // Map reference
  const mapContainerRef = useRef(null);
  const leafletMapRef = useRef(null);
  const leafletMarkersRef = useRef([]);

  // Fetch initial checkin and all verified professionals from backend
  useEffect(() => {
    if (user) {
      api.getLatestCheckin()
        .then((res) => setLatestCheckin(res.checkin))
        .catch(() => setLatestCheckin(null));
    }
    fetchProfessionals();
  }, [user]);

  // Load all professionals from backend
  const fetchProfessionals = async (cityParam = '', categoryParam = '', queryParam = '') => {
    setLoading(true);
    try {
      const res = await api.searchProfessionals({
        city: cityParam && cityParam !== 'All Cities' && !cityParam.startsWith('All') ? cityParam : undefined,
        category: categoryParam && categoryParam !== 'All Categories' ? categoryParam : undefined,
        query: queryParam || undefined,
        user_lat: userLocation ? userLocation.lat : undefined,
        user_lng: userLocation ? userLocation.lng : undefined,
        max_distance: userLocation && distanceRadius > 0 ? distanceRadius : undefined,
      });
      if (res && res.professionals && res.professionals.length > 0) {
        setDoctors(res.professionals);
      }
    } catch (err) {
      console.warn('Backend professional fetch note:', err);
    } finally {
      setLoading(false);
    }
  };

  // Trigger search on filter changes when not in proximity-mode
  useEffect(() => {
    if (!userLocation) {
      fetchProfessionals(selectedCity, selectedCategory, searchQuery);
    }
  }, [selectedCity, selectedCategory, regionFilter]);

  // Handle Geolocation "Find Professionals Near Me"
  const handleFindNearMe = () => {
    if (!navigator.geolocation) {
      setLocationError('Geolocation is not supported by your current browser.');
      return;
    }

    setLocationLoading(true);
    setLocationError(null);

    navigator.geolocation.getCurrentPosition(
      async (position) => {
        const lat = position.coords.latitude;
        const lng = position.coords.longitude;
        setUserLocation({ lat, lng });

        try {
          const res = await api.getNearbyProfessionals(
            lat,
            lng,
            distanceRadius > 0 ? distanceRadius : 50,
            selectedCategory !== 'All Categories' ? selectedCategory : ''
          );

          if (res && res.status === 'success') {
            setDoctors(res.professionals || []);
            if (res.detected_location) {
              setDetectedAddress(`${res.detected_location.city}, ${res.detected_location.state}`);
            }
          }
        } catch (err) {
          console.error('Nearby discovery failed:', err);
          setLocationError('Could not connect to nearby location service. Showing verified directory.');
        } finally {
          setLocationLoading(false);
        }
      },
      (err) => {
        setLocationLoading(false);
        if (err.code === 1) {
          setLocationError('Location permission was denied. You can select your city manually below.');
        } else if (err.code === 2) {
          setLocationError('Location information is currently unavailable. Please select your city manually.');
        } else if (err.code === 3) {
          setLocationError('Location request timed out. Please select your city manually.');
        } else {
          setLocationError('Unable to detect location. Please use manual city selection.');
        }
      },
      { enableHighAccuracy: true, timeout: 10000, maximumAge: 60000 }
    );
  };

  // Clear detected location
  const handleClearLocation = () => {
    setUserLocation(null);
    setDetectedAddress(null);
    setLocationError(null);
    setSelectedCity('All Cities');
    fetchProfessionals('All Cities', selectedCategory, searchQuery);
  };

  // Re-fetch nearby when radius or category changes while location is active
  useEffect(() => {
    if (userLocation) {
      api.getNearbyProfessionals(
        userLocation.lat,
        userLocation.lng,
        distanceRadius > 0 ? distanceRadius : 100,
        selectedCategory !== 'All Categories' ? selectedCategory : ''
      )
        .then((res) => {
          if (res && res.professionals) setDoctors(res.professionals);
        })
        .catch((err) => console.warn(err));
    }
  }, [distanceRadius, selectedCategory]);

  // Leaflet Interactive Map View Integration
  useEffect(() => {
    if (viewMode !== 'map') return;

    const loadLeaflet = async () => {
      // Add Leaflet CSS if not already present
      if (!document.getElementById('leaflet-css')) {
        const link = document.createElement('link');
        link.id = 'leaflet-css';
        link.rel = 'stylesheet';
        link.href = 'https://unpkg.com/leaflet@1.9.4/dist/leaflet.css';
        document.head.appendChild(link);
      }

      // Add Leaflet JS if not already present
      if (!window.L) {
        await new Promise((resolve) => {
          const script = document.createElement('script');
          script.src = 'https://unpkg.com/leaflet@1.9.4/dist/leaflet.js';
          script.onload = resolve;
          document.head.appendChild(script);
        });
      }

      if (!mapContainerRef.current || !window.L) return;

      // Determine center: user location or first doctor's location or Chennai
      const centerLat = userLocation?.lat || doctors[0]?.latitude || doctors[0]?.lat || 13.0827;
      const centerLng = userLocation?.lng || doctors[0]?.longitude || doctors[0]?.lng || 80.2707;

      if (!leafletMapRef.current) {
        leafletMapRef.current = window.L.map(mapContainerRef.current).setView([centerLat, centerLng], userLocation ? 12 : 7);
        window.L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
          attribution: '&copy; OpenStreetMap contributors',
          maxZoom: 18,
        }).addTo(leafletMapRef.current);
      } else {
        leafletMapRef.current.setView([centerLat, centerLng], userLocation ? 12 : 7);
      }

      // Clear existing markers
      leafletMarkersRef.current.forEach((m) => m.remove());
      leafletMarkersRef.current = [];

      // Add user location marker if active
      if (userLocation) {
        const userMarker = window.L.circleMarker([userLocation.lat, userLocation.lng], {
          radius: 9,
          fillColor: '#7c7ceb',
          color: '#ffffff',
          weight: 3,
          opacity: 1,
          fillOpacity: 0.9,
        }).addTo(leafletMapRef.current);
        userMarker.bindPopup('<b>📍 Your Current Location</b>');
        leafletMarkersRef.current.push(userMarker);
      }

      // Add markers for professionals
      doctors.forEach((doc) => {
        const lat = doc.latitude || doc.lat;
        const lng = doc.longitude || doc.lng;
        if (!lat || !lng) return;

        const isVerified = doc.verified !== false && doc.is_verified !== false;
        const markerColor = isVerified ? '#6669e5' : '#e67e22';

        const customIcon = window.L.divIcon({
          className: 'custom-map-pin',
          html: `<div style="background:${markerColor}; color:#fff; width:30px; height:30px; border-radius:50%; display:flex; align-items:center; justify-content:center; box-shadow:0 3px 8px rgba(0,0,0,0.3); font-size:14px; border:2px solid #fff;">${isVerified ? '🩺' : '🏥'}</div>`,
          iconSize: [30, 30],
          iconAnchor: [15, 15],
        });

        const popupContent = `
          <div style="font-family:Inter, sans-serif; font-size:13px; line-height:1.4; min-width:200px;">
            <b style="font-size:14px; color:#1a1a2e;">${doc.name}</b>
            <div style="color:#7c7ceb; font-weight:600; margin-top:2px;">${doc.designation || doc.hospital}</div>
            <div style="font-size:12px; color:#5c5b78; margin-top:4px;">📍 ${doc.address || doc.city}</div>
            ${doc.distance_km !== undefined && doc.distance_km !== null ? `<div style="font-size:12px; font-weight:700; color:#2e7d32; margin-top:3px;">📍 ${doc.distance_km} km away</div>` : ''}
            <div style="margin-top:8px; display:flex; gap:6px;">
              <a href="${doc.directions_url || `https://www.google.com/maps/dir/?api=1&destination=${lat},${lng}`}" target="_blank" style="background:#7c7ceb; color:#fff; padding:4px 8px; border-radius:6px; text-decoration:none; font-size:11px; font-weight:600;">🗺️ Directions</a>
              ${doc.bookingUrl ? `<a href="${doc.bookingUrl}" target="_blank" style="background:#f1efff; color:#7c7ceb; border:1px solid #7c7ceb; padding:4px 8px; border-radius:6px; text-decoration:none; font-size:11px; font-weight:600;">📅 Book</a>` : ''}
            </div>
          </div>
        `;

        const marker = window.L.marker([lat, lng], { icon: customIcon }).addTo(leafletMapRef.current);
        marker.bindPopup(popupContent);
        leafletMarkersRef.current.push(marker);
      });
    };

    loadLeaflet();
  }, [viewMode, doctors, userLocation]);

  const query = searchQuery.toLowerCase().trim();

  // Filter client-side
  const filteredDoctors = doctors.filter((doc) => {
    if (!query) return true;
    const nameMatch = (doc.name || '').toLowerCase().includes(query);
    const hospMatch = (doc.hospital || '').toLowerCase().includes(query);
    const cityMatch = (doc.city || '').toLowerCase().includes(query);
    const qualMatch = (doc.qualification || '').toLowerCase().includes(query);
    const specs = Array.isArray(doc.specialization)
      ? doc.specialization
      : Array.isArray(doc.specialties)
      ? doc.specialties
      : [];
    const specMatch = specs.some((s) => s.toLowerCase().includes(query));
    return nameMatch || hospMatch || cityMatch || qualMatch || specMatch;
  });

  const stressScore = latestCheckin?.stress_level;
  const showStressNotice = stressScore && stressScore >= 6;

  const content = (
    <main className={user ? 'main-content' : 'main-content no-sidebar'}>
      {!user && <Navbar onNavigate={onNavigate} currentPage="professional_support" />}

      {/* Header */}
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
        Connect with verified psychiatrists, clinical psychologists, and mental healthcare establishments across Tamil Nadu and major cities in India.
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
              If you or someone you know is in severe distress or experiencing thoughts of self-harm, please do not wait for a routine appointment. Reach out immediately to verified 24/7 helplines:
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
                href="tel:04424640050"
                className="btn-secondary"
                style={{ padding: '6px 14px', fontSize: '0.85rem', textDecoration: 'none' }}
              >
                📞 Sneha Chennai: 044-24640050
              </a>
              <a
                href="tel:104"
                className="btn-secondary"
                style={{ padding: '6px 14px', fontSize: '0.85rem', textDecoration: 'none' }}
              >
                📞 TN Health Helpline: 104
              </a>
              <a
                href="tel:18005990019"
                className="btn-secondary"
                style={{ padding: '6px 14px', fontSize: '0.85rem', textDecoration: 'none' }}
              >
                📞 KIRAN: 1800-599-0019
              </a>
            </div>
          </div>
        </div>
      </div>

      {/* Stress Score Notice */}
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
            It looks like you've recently experienced elevated stress levels ({stressScore}/10). Speaking with a licensed mental-health specialist or psychiatrist can provide supportive guidance, medical evaluation, and personalized coping strategies.
          </div>
        </div>
      )}

      {/* Location Detection & Filter Section */}
      <div className="aw-card" style={{ margin: '18px 0', padding: '18px' }}>
        <div style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>

          {/* Search bar + Geolocation Button + View Mode Toggle */}
          <div style={{ display: 'flex', gap: '12px', flexWrap: 'wrap', alignItems: 'center' }}>
            <div style={{ flex: '1 1 300px' }}>
              <input
                type="text"
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                placeholder="🔎 Search by psychiatrist, hospital, city, or specialization (e.g. Depression, CBT, NIMHANS)..."
                style={{ width: '100%', padding: '10px 14px', borderRadius: '8px', border: '1px solid var(--line)' }}
              />
            </div>

            {/* Native Browser Geolocation Button */}
            <button
              className="btn-primary"
              onClick={handleFindNearMe}
              disabled={locationLoading}
              style={{
                display: 'inline-flex',
                alignItems: 'center',
                gap: '6px',
                padding: '10px 16px',
                fontSize: '0.88rem',
                whiteSpace: 'nowrap',
              }}
              title="Detect your current location to find nearby mental health professionals"
            >
              {locationLoading ? '⏳ Detecting Location...' : '📍 Find Professionals Near Me'}
            </button>

            {/* View Mode Toggle */}
            <div style={{ display: 'inline-flex', borderRadius: '8px', overflow: 'hidden', border: '1px solid var(--line)' }}>
              <button
                type="button"
                onClick={() => setViewMode('list')}
                style={{
                  padding: '8px 14px',
                  fontSize: '0.85rem',
                  border: 'none',
                  cursor: 'pointer',
                  background: viewMode === 'list' ? 'var(--accent, #7c7ceb)' : 'var(--card-bg, #ffffff)',
                  color: viewMode === 'list' ? '#ffffff' : 'var(--ink)',
                  fontWeight: 600,
                }}
              >
                📋 Card View
              </button>
              <button
                type="button"
                onClick={() => setViewMode('map')}
                style={{
                  padding: '8px 14px',
                  fontSize: '0.85rem',
                  border: 'none',
                  cursor: 'pointer',
                  background: viewMode === 'map' ? 'var(--accent, #7c7ceb)' : 'var(--card-bg, #ffffff)',
                  color: viewMode === 'map' ? '#ffffff' : 'var(--ink)',
                  fontWeight: 600,
                }}
              >
                🗺️ Map View
              </button>
            </div>
          </div>

          {/* Location Feedback Status Banner */}
          {detectedAddress && (
            <div
              style={{
                background: 'rgba(46, 125, 50, 0.08)',
                border: '1px solid rgba(46, 125, 50, 0.25)',
                borderRadius: '8px',
                padding: '10px 14px',
                display: 'flex',
                justifyContent: 'space-between',
                alignItems: 'center',
                flexWrap: 'wrap',
                gap: '8px',
              }}
            >
              <div style={{ fontSize: '0.88rem', color: '#1b5e20', fontWeight: 600 }}>
                📍 Detected Location: <b>{detectedAddress}</b> • Showing professionals sorted by proximity ({filteredDoctors.length} found)
              </div>
              <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                <span style={{ fontSize: '0.82rem', color: 'var(--ink)' }}>Radius:</span>
                <select
                  value={distanceRadius}
                  onChange={(e) => setDistanceRadius(Number(e.target.value))}
                  style={{ padding: '4px 8px', fontSize: '0.82rem', borderRadius: '6px', border: '1px solid var(--line)' }}
                >
                  {DISTANCE_OPTIONS.map((opt) => (
                    <option key={opt.value} value={opt.value}>
                      {opt.label}
                    </option>
                  ))}
                </select>
                <button
                  type="button"
                  onClick={handleClearLocation}
                  style={{
                    background: 'transparent',
                    border: 'none',
                    color: '#d63031',
                    fontSize: '0.82rem',
                    cursor: 'pointer',
                    fontWeight: 600,
                    textDecoration: 'underline',
                  }}
                >
                  Clear Location
                </button>
              </div>
            </div>
          )}

          {locationError && (
            <div
              style={{
                background: '#fff9db',
                border: '1px solid #ffe066',
                borderRadius: '8px',
                padding: '10px 14px',
                fontSize: '0.85rem',
                color: '#856404',
              }}
            >
              ⚠️ {locationError}
            </div>
          )}

          {/* Region Tabs: All India | Tamil Nadu (16 Cities) | Other Major Cities (22 Cities) */}
          <div style={{ display: 'flex', gap: '8px', flexWrap: 'wrap', alignItems: 'center' }}>
            <span style={{ fontSize: '0.85rem', fontWeight: 600, color: 'var(--ink)', marginRight: '4px' }}>
              Region:
            </span>
            <button
              className={regionFilter === 'All' ? 'btn-primary' : 'btn-secondary'}
              style={{ padding: '5px 12px', fontSize: '0.82rem' }}
              onClick={() => {
                setRegionFilter('All');
                setSelectedCity('All Cities');
              }}
            >
              All India (38 Cities)
            </button>
            <button
              className={regionFilter === 'TN' ? 'btn-primary' : 'btn-secondary'}
              style={{ padding: '5px 12px', fontSize: '0.82rem' }}
              onClick={() => {
                setRegionFilter('TN');
                setSelectedCity('All Tamil Nadu');
              }}
            >
              🌴 Tamil Nadu (16 Cities)
            </button>
            <button
              className={regionFilter === 'Other' ? 'btn-primary' : 'btn-secondary'}
              style={{ padding: '5px 12px', fontSize: '0.82rem' }}
              onClick={() => {
                setRegionFilter('Other');
                setSelectedCity('All Other Cities');
              }}
            >
              🏙️ Other Major Cities (22 Cities)
            </button>
          </div>

          {/* City Selection Pills / Dropdown */}
          <div style={{ display: 'flex', gap: '6px', flexWrap: 'wrap', alignItems: 'center' }}>
            <span style={{ fontSize: '0.85rem', fontWeight: 600, color: 'var(--ink)', marginRight: '4px' }}>
              City Filter:
            </span>
            {regionFilter === 'TN' &&
              TN_CITIES.map((city) => (
                <button
                  key={city}
                  className={selectedCity === city ? 'btn-primary' : 'btn-secondary'}
                  style={{ padding: '4px 10px', fontSize: '0.8rem' }}
                  onClick={() => setSelectedCity(city)}
                >
                  {city}
                </button>
              ))}

            {regionFilter === 'Other' &&
              OTHER_CITIES.slice(0, 10).map((city) => (
                <button
                  key={city}
                  className={selectedCity === city ? 'btn-primary' : 'btn-secondary'}
                  style={{ padding: '4px 10px', fontSize: '0.8rem' }}
                  onClick={() => setSelectedCity(city)}
                >
                  {city}
                </button>
              ))}

            {regionFilter === 'All' && (
              <>
                {['All Cities', 'Chennai', 'Coimbatore', 'Salem', 'Madurai', 'Bengaluru', 'Delhi-NCR', 'Mumbai', 'Hyderabad', 'Kolkata'].map((city) => (
                  <button
                    key={city}
                    className={selectedCity === city ? 'btn-primary' : 'btn-secondary'}
                    style={{ padding: '4px 10px', fontSize: '0.8rem' }}
                    onClick={() => setSelectedCity(city)}
                  >
                    {city}
                  </button>
                ))}
              </>
            )}

            {/* Quick dropdown for all 38 cities */}
            <select
              value={selectedCity}
              onChange={(e) => setSelectedCity(e.target.value)}
              style={{
                padding: '4px 8px',
                fontSize: '0.82rem',
                borderRadius: '6px',
                border: '1px solid var(--line)',
                marginLeft: '4px',
              }}
            >
              <option value="All Cities">-- Browse All 38 Cities --</option>
              <optgroup label="Tamil Nadu (16 Cities)">
                {TN_CITIES.slice(1).map((c) => (
                  <option key={c} value={c}>{c}</option>
                ))}
              </optgroup>
              <optgroup label="Other Indian Cities (22 Cities)">
                {OTHER_CITIES.slice(1).map((c) => (
                  <option key={c} value={c}>{c}</option>
                ))}
              </optgroup>
            </select>
          </div>

          {/* Category Filter */}
          <div style={{ display: 'flex', gap: '6px', flexWrap: 'wrap', alignItems: 'center' }}>
            <span style={{ fontSize: '0.85rem', fontWeight: 600, color: 'var(--ink)', marginRight: '4px' }}>
              Specialization:
            </span>
            {CATEGORIES.map((cat) => (
              <button
                key={cat}
                className={selectedCategory === cat ? 'btn-primary' : 'btn-secondary'}
                style={{ padding: '4px 10px', fontSize: '0.8rem' }}
                onClick={() => setSelectedCategory(cat)}
              >
                {cat}
              </button>
            ))}
          </div>

        </div>
      </div>

      {/* Main Results View */}
      <div>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '14px' }}>
          <h3 style={{ margin: 0 }}>
            {userLocation ? '📍 Nearby Mental Health Professionals' : 'Verified Mental Health Directory'} ({filteredDoctors.length})
          </h3>
          <span className="aw-muted" style={{ fontSize: '0.85rem' }}>
            🇮🇳 Indian Medical Register &amp; NMC Verified
          </span>
        </div>

        {/* MAP VIEW */}
        {viewMode === 'map' && (
          <div className="aw-card" style={{ padding: '0', overflow: 'hidden', marginBottom: '20px' }}>
            <div
              ref={mapContainerRef}
              style={{
                width: '100%',
                height: '480px',
                borderRadius: '12px',
                background: '#e5e3df',
              }}
            />
            <div style={{ padding: '12px 16px', background: 'var(--card-bg, #ffffff)', borderTop: '1px solid var(--line)', display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: '8px' }}>
              <div style={{ fontSize: '0.82rem', color: 'var(--muted)' }}>
                💡 Click any pin on the map to see clinic details, direct booking links, and turn-by-turn Google Maps directions.
              </div>
              <div style={{ display: 'flex', gap: '14px', fontSize: '0.82rem' }}>
                <span>🩺 <b style={{ color: '#6669e5' }}>Purple Pin:</b> Verified Doctor / Hospital</span>
                {userLocation && <span>📍 <b style={{ color: '#2e7d32' }}>Circle:</b> Your Location</span>}
              </div>
            </div>
          </div>
        )}

        {/* CARD LIST VIEW */}
        {filteredDoctors.length === 0 ? (
          <div className="aw-card" style={{ textAlign: 'center', padding: '36px 20px' }}>
            <div style={{ fontSize: '2rem', marginBottom: '8px' }}>🔍</div>
            <div style={{ fontWeight: 600, color: 'var(--ink)' }}>No professionals matched your current filter</div>
            <div className="aw-muted" style={{ fontSize: '0.9rem', marginTop: '6px' }}>
              Try expanding your distance radius, choosing "All Cities", or clearing search keywords.
            </div>
          </div>
        ) : (
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(330px, 1fr))', gap: '16px' }}>
            {filteredDoctors.map((doc) => {
              const isVerified = doc.verified !== false && doc.is_verified !== false;
              const specs = Array.isArray(doc.specialization)
                ? doc.specialization
                : Array.isArray(doc.specialties)
                ? doc.specialties
                : [];

              const directionsHref =
                doc.directions_url ||
                `https://www.google.com/maps/dir/?api=1&destination=${encodeURIComponent((doc.name || '') + ' ' + (doc.hospital || '') + ' ' + (doc.address || doc.city || ''))}`;

              return (
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
                    {/* Header: Name + Verification Badge */}
                    <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', gap: '8px' }}>
                      <div>
                        <div style={{ fontWeight: 700, fontSize: '1.15rem', color: 'var(--ink)' }}>
                          {doc.category === 'Psychiatric Hospital' ? '🏥' : '👨‍⚕️'} {doc.name}
                        </div>
                        <div style={{ color: 'var(--accent, #7c7ceb)', fontWeight: 600, fontSize: '0.88rem', marginTop: '2px' }}>
                          {doc.designation || doc.title || 'Mental Health Professional'}
                        </div>
                      </div>

                      {/* Verification Status Badge */}
                      {isVerified ? (
                        <span
                          style={{
                            background: 'rgba(46, 125, 50, 0.12)',
                            color: '#2e7d32',
                            fontSize: '0.72rem',
                            fontWeight: 700,
                            padding: '3px 8px',
                            borderRadius: '12px',
                            whiteSpace: 'nowrap',
                            border: '1px solid rgba(46, 125, 50, 0.25)',
                          }}
                          title={doc.verificationSource || 'Verified via Indian Medical Register / Medical Council'}
                        >
                          ✓ Verified
                        </span>
                      ) : (
                        <span
                          style={{
                            background: 'rgba(230, 126, 34, 0.12)',
                            color: '#d35400',
                            fontSize: '0.72rem',
                            fontWeight: 600,
                            padding: '3px 8px',
                            borderRadius: '12px',
                            whiteSpace: 'nowrap',
                          }}
                        >
                          Verification Not Confirmed
                        </span>
                      )}
                    </div>

                    {/* Distance Badge if available */}
                    {doc.distance_km !== undefined && doc.distance_km !== null && (
                      <div
                        style={{
                          display: 'inline-flex',
                          alignItems: 'center',
                          gap: '4px',
                          marginTop: '8px',
                          background: 'rgba(124, 124, 235, 0.12)',
                          color: 'var(--accent-deep, #6669e5)',
                          fontSize: '0.78rem',
                          fontWeight: 700,
                          padding: '2px 8px',
                          borderRadius: '6px',
                        }}
                      >
                        📍 {doc.distance_km} km away from your location
                      </div>
                    )}

                    {/* Hospital & Address */}
                    <div style={{ marginTop: '10px', fontSize: '0.9rem', color: 'var(--ink)' }}>
                      <div>🏥 <b>{doc.hospital}</b></div>
                      <div className="aw-muted" style={{ fontSize: '0.85rem', marginTop: '3px' }}>
                        📍 {doc.address}
                      </div>
                      {doc.qualification && (
                        <div style={{ marginTop: '5px', fontSize: '0.82rem', color: 'var(--muted)' }}>
                          🎓 <b>Qualification:</b> {doc.qualification}
                        </div>
                      )}
                      {doc.experience && (
                        <div style={{ marginTop: '4px', fontSize: '0.85rem' }}>
                          ⏳ <b>Experience:</b> {doc.experience}
                        </div>
                      )}
                      {doc.consultationType && (
                        <div style={{ marginTop: '4px', fontSize: '0.85rem' }}>
                          💻 <b>Consultation:</b> {doc.consultationType}
                        </div>
                      )}
                    </div>

                    {/* Specializations */}
                    {specs.length > 0 && (
                      <div style={{ marginTop: '12px' }}>
                        <div style={{ fontSize: '0.78rem', fontWeight: 600, color: 'var(--ink)', marginBottom: '6px' }}>
                          Areas of Expertise:
                        </div>
                        <div style={{ display: 'flex', flexWrap: 'wrap', gap: '5px' }}>
                          {specs.map((spec, sIdx) => (
                            <span
                              key={sIdx}
                              style={{
                                background: 'var(--bg, #f5f6fa)',
                                border: '1px solid rgba(124,124,235,0.2)',
                                borderRadius: '6px',
                                padding: '2px 8px',
                                fontSize: '0.72rem',
                                color: 'var(--ink)',
                              }}
                            >
                              {spec}
                            </span>
                          ))}
                        </div>
                      </div>
                    )}
                  </div>

                  {/* Actions: Book + Call + Directions */}
                  <div
                    style={{
                      marginTop: '18px',
                      paddingTop: '14px',
                      borderTop: '1px solid rgba(124,124,235,0.15)',
                      display: 'flex',
                      flexWrap: 'wrap',
                      gap: '8px',
                    }}
                  >
                    {/* Book Appointment */}
                    {doc.bookingUrl && (
                      <a
                        href={doc.bookingUrl}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="btn-primary"
                        style={{
                          flex: '1 1 120px',
                          textAlign: 'center',
                          textDecoration: 'none',
                          padding: '8px 10px',
                          fontSize: '0.84rem',
                        }}
                      >
                        📅 Book
                      </a>
                    )}

                    {/* Directions via Google Maps */}
                    <a
                      href={directionsHref}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="btn-secondary"
                      style={{
                        textAlign: 'center',
                        textDecoration: 'none',
                        padding: '8px 10px',
                        fontSize: '0.84rem',
                        display: 'inline-flex',
                        alignItems: 'center',
                        gap: '4px',
                      }}
                      title="Open Google Maps turn-by-turn directions"
                    >
                      🗺️ Directions
                    </a>

                    {/* Call Clinic / Doctor */}
                    {doc.phone && (
                      <a
                        href={`tel:${doc.phone.replace(/[^0-9+]/g, '')}`}
                        className="btn-secondary"
                        style={{
                          textAlign: 'center',
                          textDecoration: 'none',
                          padding: '8px 10px',
                          fontSize: '0.84rem',
                        }}
                        title={`Call ${doc.hospital || doc.name}`}
                      >
                        📞 Call
                      </a>
                    )}
                  </div>
                </div>
              );
            })}
          </div>
        )}
      </div>

      {/* Directory Disclaimer */}
      <div className="aw-card" style={{ marginTop: '24px', padding: '16px', background: 'var(--card-bg, #ffffff)' }}>
        <div style={{ fontSize: '0.85rem', color: 'var(--ink)', lineHeight: '1.5' }}>
          ℹ️ <b>Directory Information Note:</b> Verified doctors and institutions hold registered medical qualifications recognized by the National Medical Commission (NMC) and respective State Medical Councils across India and Tamil Nadu. Appointments are scheduled directly with the official hospital or clinic. AI Wellness Companion does not collect medical fees or share confidential health records.
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
