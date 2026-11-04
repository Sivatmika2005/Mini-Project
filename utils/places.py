"""Location-based mental healthcare discovery utility.

Integrates:
- Google Places & Geocoding API (when GOOGLE_MAPS_API_KEY is configured)
- Haversine distance formula for precise geographic proximity
- Curated & verified registry of 78+ licensed psychiatrists, clinical psychologists,
  and psychiatric hospitals covering 16 Tamil Nadu cities and 22 major Indian cities.
- Distinction between verified doctors/hospitals and unverified Google Places listings.
"""
import os
import math
import json
import logging
import urllib.request
import urllib.parse
from typing import List, Dict, Optional, Tuple
from dotenv import load_dotenv

from utils.professionals_data import VERIFIED_ESTABLISHMENTS, SUPPORTED_CITIES_COORDINATES, CATEGORIES

load_dotenv()
logger = logging.getLogger(__name__)


def calculate_haversine_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Calculates the great-circle distance between two points on Earth in kilometers.
    
    Formula:
      a = sin²(Δφ/2) + cos φ1 ⋅ cos φ2 ⋅ sin²(Δλ/2)
      c = 2 ⋅ atan2( √a, √(1−a) )
      d = R ⋅ c (where R = 6371 km)
    """
    R = 6371.0  # Earth's radius in kilometers
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = (
        math.sin(dlat / 2.0) ** 2
        + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlon / 2.0) ** 2
    )
    c = 2.0 * math.atan2(math.sqrt(a), math.sqrt(1.0 - a))
    return round(R * c, 2)


def get_closest_known_city(lat: float, lng: float) -> Optional[Dict]:
    """Finds the closest known indexed city based on coordinates."""
    closest_city = None
    min_dist = float("inf")
    for city_name, city_info in SUPPORTED_CITIES_COORDINATES.items():
        dist = calculate_haversine_distance(lat, lng, city_info["lat"], city_info["lng"])
        if dist < min_dist:
            min_dist = dist
            closest_city = {"city": city_name, "state": city_info["state"], "distance_km": dist}
    return closest_city


def reverse_geocode(lat: float, lng: float) -> Dict[str, str]:
    """Resolves latitude and longitude into readable City and State.
    
    Uses Google Geocoding API if GOOGLE_MAPS_API_KEY is configured;
    falls back gracefully to closest indexed Indian city.
    """
    api_key = os.getenv("GOOGLE_MAPS_API_KEY")
    if api_key:
        try:
            url = f"https://maps.googleapis.com/maps/api/geocode/json?latlng={lat},{lng}&key={api_key}"
            req = urllib.request.Request(url, headers={"User-Agent": "AI-Wellness-Companion/1.0"})
            with urllib.request.urlopen(req, timeout=5) as resp:
                data = json.loads(resp.read().decode("utf-8"))
                if data.get("status") == "OK" and data.get("results"):
                    city = ""
                    state = ""
                    district = ""
                    for comp in data["results"][0].get("address_components", []):
                        types = comp.get("types", [])
                        if "locality" in types:
                            city = comp.get("long_name", "")
                        elif "administrative_area_level_2" in types and not city:
                            district = comp.get("long_name", "")
                        elif "administrative_area_level_1" in types:
                            state = comp.get("long_name", "")
                    return {
                        "city": city or district or "Nearby",
                        "state": state or "India",
                        "formatted_address": data["results"][0].get("formatted_address", ""),
                    }
        except Exception as e:
            logger.warning(f"Google Geocoding API lookup failed: {e}")

    # Fallback via closest indexed city
    closest = get_closest_known_city(lat, lng)
    if closest:
        return {
            "city": closest["city"],
            "state": closest["state"],
            "formatted_address": f"{closest['city']}, {closest['state']}, India",
        }
    return {"city": "Your Location", "state": "India", "formatted_address": "India"}


def search_google_places(lat: float, lng: float, radius_meters: int = 25000) -> List[Dict]:
    """Queries Google Places API (Nearby Search) for psychiatric & mental wellness establishments.
    
    All listings returned from Google Places are marked as 'Verification Not Confirmed'
    until verified against the Indian Medical Register / medical college directory.
    """
    api_key = os.getenv("GOOGLE_MAPS_API_KEY")
    if not api_key:
        return []

    try:
        query_kw = urllib.parse.quote("psychiatrist mental health clinic hospital psychologist")
        url = (
            f"https://maps.googleapis.com/maps/api/place/nearbysearch/json"
            f"?location={lat},{lng}&radius={radius_meters}&keyword={query_kw}&key={api_key}"
        )
        req = urllib.request.Request(url, headers={"User-Agent": "AI-Wellness-Companion/1.0"})
        with urllib.request.urlopen(req, timeout=6) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            if data.get("status") in ("OK", "ZERO_RESULTS"):
                results = []
                for item in data.get("results", []):
                    item_lat = item.get("geometry", {}).get("location", {}).get("lat", 0.0)
                    item_lng = item.get("geometry", {}).get("location", {}).get("lng", 0.0)
                    dist = calculate_haversine_distance(lat, lng, item_lat, item_lng)
                    place_id = item.get("place_id", "")
                    name = item.get("name", "Mental Health Clinic")
                    vicinity = item.get("vicinity", "Nearby Location")
                    rating = item.get("rating", 4.5)
                    user_ratings_total = item.get("user_ratings_total", 0)

                    # Build directions and maps links
                    directions_url = f"https://www.google.com/maps/dir/?api=1&destination={urllib.parse.quote(name + ' ' + vicinity)}"
                    maps_url = f"https://www.google.com/maps/search/?api=1&query={urllib.parse.quote(name)}&query_place_id={place_id}"

                    results.append({
                        "id": f"places_{place_id}",
                        "name": name,
                        "title": "Mental Healthcare Establishment",
                        "qualification": "Google Maps Listed Facility",
                        "category": "Psychiatric Clinic / Hospital",
                        "city": vicinity.split(",")[-1].strip() if "," in vicinity else "Nearby",
                        "state": "India",
                        "address": vicinity,
                        "lat": item_lat,
                        "lng": item_lng,
                        "phone": "Available via Google Maps",
                        "experience": "N/A",
                        "rating": float(rating),
                        "reviews_count": user_ratings_total,
                        "fee": "Consultation fee on enquiry",
                        "availability": "Contact facility for timings",
                        "languages": ["English", "Local Language"],
                        "specialties": ["Mental Health Support", "Consultation"],
                        "about": f"{name} is a mental healthcare establishment listed on Google Maps.",
                        "is_verified": False,
                        "verification_badge": "Verification Not Confirmed",
                        "verification_source": "Google Places Listing",
                        "distance_km": dist,
                        "directions_url": directions_url,
                        "maps_url": maps_url,
                        "booking_url": directions_url,
                        "is_hospital": True,
                    })
                return results
    except Exception as e:
        logger.warning(f"Google Places API lookup failed: {e}")
    return []


def get_nearby_professionals(
    lat: float,
    lng: float,
    radius_km: float = 25.0,
    category: Optional[str] = None,
    sort_by: str = "distance",
) -> Dict:
    """Finds professionals near the given coordinates.
    
    1. Computes exact distance to all 78 verified establishments.
    2. Queries Google Places API if configured and merges results.
    3. Guarantees at least 2 verified establishments are always returned,
       even if the user is outside the initial radius (expanding smoothly).
    """
    detected_loc = reverse_geocode(lat, lng)

    # 1. Calculate distance for all verified establishments
    scored_verified = []
    for est in VERIFIED_ESTABLISHMENTS:
        item = dict(est)
        est_lat = item.get("latitude") or item.get("lat", 0.0)
        est_lng = item.get("longitude") or item.get("lng", 0.0)
        dist = calculate_haversine_distance(lat, lng, est_lat, est_lng)
        item["distance_km"] = dist
        item["latitude"] = est_lat
        item["longitude"] = est_lng
        item["lat"] = est_lat
        item["lng"] = est_lng
        # Generate Google Maps directions URL
        destination_str = f"{item['name']}, {item.get('hospital', '')}, {item.get('address', '')}"
        item["directions_url"] = f"https://www.google.com/maps/dir/?api=1&destination={urllib.parse.quote(destination_str)}"
        scored_verified.append(item)

    # Filter by category if specified
    if category and category.lower() != "all":
        cat_lower = category.lower()
        scored_verified = [
            e for e in scored_verified
            if cat_lower in e.get("category", "").lower()
            or cat_lower in e.get("title", "").lower()
            or any(cat_lower in s.lower() for s in e.get("specialties", []))
        ]

    # Filter within radius
    within_radius = [e for e in scored_verified if e["distance_km"] <= radius_km]

    # Query Google Places if enabled
    places_results = []
    if os.getenv("GOOGLE_MAPS_API_KEY"):
        places_results = search_google_places(lat, lng, radius_meters=int(radius_km * 1000))
        if category and category.lower() != "all":
            cat_lower = category.lower()
            places_results = [
                p for p in places_results
                if cat_lower in p.get("category", "").lower() or cat_lower in p.get("name", "").lower()
            ]

    # Combine: Verified establishments first, then Places results
    combined = within_radius + places_results

    # Guarantee: If fewer than 2 establishments are in range, include the closest verified ones
    if len(combined) < 2:
        sorted_all = sorted(scored_verified, key=lambda x: x["distance_km"])
        for item in sorted_all:
            if item not in combined:
                combined.append(item)
            if len(combined) >= 2:
                break

    # Sort results
    if sort_by == "distance":
        combined.sort(key=lambda x: x.get("distance_km", float("inf")))
    elif sort_by == "rating":
        combined.sort(key=lambda x: x.get("rating", 0.0), reverse=True)
    elif sort_by == "name":
        combined.sort(key=lambda x: x.get("name", "").lower())

    return {
        "status": "success",
        "detected_location": detected_loc,
        "user_coordinates": {"lat": lat, "lng": lng},
        "search_radius_km": radius_km,
        "total_count": len(combined),
        "professionals": combined,
    }


def search_professionals(
    city: Optional[str] = None,
    state: Optional[str] = None,
    district: Optional[str] = None,
    pincode: Optional[str] = None,
    query: Optional[str] = None,
    category: Optional[str] = None,
    sort_by: str = "distance",
    max_distance: Optional[float] = None,
    user_lat: Optional[float] = None,
    user_lng: Optional[float] = None,
) -> Dict:
    """Flexible multi-criteria search across verified mental health directory."""
    results = []

    for est in VERIFIED_ESTABLISHMENTS:
        item = dict(est)
        est_lat = item.get("latitude") or item.get("lat", 0.0)
        est_lng = item.get("longitude") or item.get("lng", 0.0)
        item["latitude"] = est_lat
        item["longitude"] = est_lng
        item["lat"] = est_lat
        item["lng"] = est_lng
        # Compute distance if user coordinates provided
        if user_lat is not None and user_lng is not None:
            item["distance_km"] = calculate_haversine_distance(user_lat, user_lng, est_lat, est_lng)
        else:
            item["distance_km"] = None

        dest_str = f"{item['name']}, {item.get('hospital', '')}, {item.get('address', '')}"
        item["directions_url"] = f"https://www.google.com/maps/dir/?api=1&destination={urllib.parse.quote(dest_str)}"
        results.append(item)

    # Filter by City
    if city and city.lower() != "all":
        city_lower = city.strip().lower()
        results = [e for e in results if city_lower in e.get("city", "").lower()]

    # Filter by State
    if state and state.lower() != "all":
        state_lower = state.strip().lower()
        results = [e for e in results if state_lower in e.get("state", "").lower()]

    # Filter by Category
    if category and category.lower() != "all":
        cat_lower = category.strip().lower()
        results = [
            e for e in results
            if cat_lower in e.get("category", "").lower()
            or cat_lower in e.get("title", "").lower()
            or any(cat_lower in s.lower() for s in e.get("specialties", []))
        ]

    # Filter by Search Query (name, hospital, qualification, address, pincode)
    if query:
        q_lower = query.strip().lower()
        results = [
            e for e in results
            if q_lower in e.get("name", "").lower()
            or q_lower in e.get("qualification", "").lower()
            or q_lower in e.get("address", "").lower()
            or q_lower in e.get("city", "").lower()
            or any(q_lower in s.lower() for s in e.get("specialties", []))
        ]

    # Filter by max distance if distance is available
    if max_distance is not None and user_lat is not None and user_lng is not None:
        results = [e for e in results if e.get("distance_km") is not None and e["distance_km"] <= max_distance]

    # Sorting
    if sort_by == "distance" and user_lat is not None and user_lng is not None:
        results.sort(key=lambda x: x.get("distance_km") if x.get("distance_km") is not None else float("inf"))
    elif sort_by == "rating":
        results.sort(key=lambda x: x.get("rating", 0.0), reverse=True)
    elif sort_by == "name":
        results.sort(key=lambda x: x.get("name", "").lower())
    elif sort_by == "fee_low":
        results.sort(key=lambda x: int("".join(c for c in x.get("fee", "0") if c.isdigit()) or "0"))

    # Fallback safety: ensure if city is selected but returned 0 results, return all for that city
    if city and city.lower() != "all" and len(results) == 0:
        city_lower = city.strip().lower()
        results = [e for e in VERIFIED_ESTABLISHMENTS if city_lower in e.get("city", "").lower()]

    return {
        "status": "success",
        "city_filter": city or "All",
        "state_filter": state or "All",
        "total_count": len(results),
        "professionals": results,
    }
