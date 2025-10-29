import os
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path
from dotenv import load_dotenv

ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

load_dotenv(ROOT_DIR / ".env")

from src.db.database import SessionLocal  # noqa: E402
from src.db.models import Listing  # noqa: E402


MOCK_LISTINGS = [
    {
        "external_id": "mock-roma-001",
        "source": "mock",
        "url": "https://mocked-listings.example/roma/001",
        "title": "Accogliente appartamento vicino al Colosseo",
        "description": "Luminoso bilocale recentemente ristrutturato, a due passi dal Colosseo.",
        "price": 1500,
        "price_currency": "EUR",
        "property_type": "apartment",
        "rooms": 2,
        "bedrooms": 1,
        "bathrooms": 1,
        "area": 55,
        "furnished": True,
        "pets_allowed": True,
        "features": ["Furnished", "Pet-friendly", "City view"],
        "address": "Via del Colosseo, 12",
        "city": "Roma",
        "district": "Centro Storico",
        "postal_code": "00184",
        "latitude": 41.8902,
        "longitude": 12.4922,
        "images": [
            "https://via.placeholder.com/1024x768.png?text=Roma+001+A",
            "https://via.placeholder.com/1024x768.png?text=Roma+001+B",
        ],
    },
    {
        "external_id": "mock-roma-002",
        "source": "mock",
        "url": "https://mocked-listings.example/roma/002",
        "title": "Trilocale moderno a Trastevere",
        "description": "Ampio trilocale con balcone panoramico nel cuore di Trastevere.",
        "price": 2100,
        "price_currency": "EUR",
        "property_type": "apartment",
        "rooms": 3,
        "bedrooms": 2,
        "bathrooms": 2,
        "area": 80,
        "furnished": True,
        "pets_allowed": False,
        "features": ["Balcony", "Elevator"],
        "address": "Via della Scala, 27",
        "city": "Roma",
        "district": "Trastevere",
        "postal_code": "00153",
        "latitude": 41.8896,
        "longitude": 12.4709,
        "images": [
            "https://via.placeholder.com/1024x768.png?text=Roma+002+A",
            "https://via.placeholder.com/1024x768.png?text=Roma+002+B",
        ],
    },
    {
        "external_id": "mock-roma-003",
        "source": "mock",
        "url": "https://mocked-listings.example/roma/003",
        "title": "Monolocale luminoso a Prati",
        "description": "Perfetto per studenti o giovani professionisti, vicino alla metropolitana.",
        "price": 950,
        "price_currency": "EUR",
        "property_type": "studio",
        "rooms": 1,
        "bedrooms": 1,
        "bathrooms": 1,
        "area": 35,
        "furnished": True,
        "pets_allowed": False,
        "features": ["Near metro"],
        "address": "Via Cola di Rienzo, 88",
        "city": "Roma",
        "district": "Prati",
        "postal_code": "00192",
        "latitude": 41.9062,
        "longitude": 12.4663,
        "images": [
            "https://via.placeholder.com/1024x768.png?text=Roma+003+A",
            "https://via.placeholder.com/1024x768.png?text=Roma+003+B",
        ],
    },
    {
        "external_id": "mock-milano-001",
        "source": "mock",
        "url": "https://mocked-listings.example/milano/001",
        "title": "Bilocale elegante a Brera",
        "description": "Appartamento completamente arredato nel quartiere Brera, Milano.",
        "price": 2400,
        "price_currency": "EUR",
        "property_type": "apartment",
        "rooms": 2,
        "bedrooms": 1,
        "bathrooms": 1,
        "area": 60,
        "furnished": True,
        "pets_allowed": False,
        "features": ["Furnished", "City center"],
        "address": "Via Brera, 10",
        "city": "Milano",
        "district": "Brera",
        "postal_code": "20121",
        "latitude": 45.4723,
        "longitude": 9.1889,
        "images": [
            "https://via.placeholder.com/1024x768.png?text=Milano+001",
        ],
    },
    {
        "external_id": "mock-roma-004",
        "source": "mock",
        "url": "https://mocked-listings.example/roma/004",
        "title": "Attico con terrazza a Monti",
        "description": "Attico con ampia terrazza e vista su Roma, ideale per famiglie.",
        "price": 2800,
        "price_currency": "EUR",
        "property_type": "penthouse",
        "rooms": 4,
        "bedrooms": 3,
        "bathrooms": 2,
        "area": 110,
        "furnished": False,
        "pets_allowed": True,
        "features": ["Terrace", "City view", "Parking"],
        "address": "Via dei Serpenti, 45",
        "city": "Roma",
        "district": "Monti",
        "postal_code": "00184",
        "latitude": 41.8944,
        "longitude": 12.4931,
        "images": [
            "https://via.placeholder.com/1024x768.png?text=Roma+004+A",
            "https://via.placeholder.com/1024x768.png?text=Roma+004+B",
        ],
    },
]


def create_or_update_listing(session, data: dict) -> tuple[Listing, bool]:
    listing = (
        session.query(Listing)
        .filter(Listing.source == data["source"], Listing.external_id == data["external_id"])
        .first()
    )

    now = datetime.now(timezone.utc)

    if listing:
        for key, value in data.items():
            setattr(listing, key, value)
        listing.updated_at = now
        session.add(listing)
        return listing, False

    listing = Listing(
        **data,
        created_at=now,
        scraped_at=now,
        published_at=now - timedelta(days=7)
    )
    session.add(listing)
    return listing, True


def main():
    session = SessionLocal()
    try:
        created = 0
        updated = 0
        for item in MOCK_LISTINGS:
            _, is_created = create_or_update_listing(session, item)
            if is_created:
                created += 1
            else:
                updated += 1
        session.commit()
        print(f"Mock listings processed. Created: {created}, updated: {updated}")
    except Exception as exc:
        session.rollback()
        print(f"Error creating mock listings: {exc}")
        raise
    finally:
        session.close()


if __name__ == "__main__":
    main()
