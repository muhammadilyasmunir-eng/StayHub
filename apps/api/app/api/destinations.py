from datetime import date
from urllib.parse import quote

from fastapi import APIRouter

router = APIRouter(prefix="/public/destinations", tags=["Public Destinations"])


# Wikimedia Commons images are rotated deterministically by day so each city
# presents one destination image per day without storing image state.
_DESTINATIONS = [
    {
        "city": "Lahore",
        "country": "Pakistan",
        "title": "Badshahi Mosque",
        "description": "Mughal-era heritage and one of Lahore's most iconic landmarks.",
        "images": [
            "Badshahi Mosque (Lahore).jpg",
            "Badshahi Mosque Lahore Punjab.jpg",
            "LAHORE FORT.jpg",
        ],
    },
    {
        "city": "Islamabad",
        "country": "Pakistan",
        "title": "Faisal Mosque",
        "description": "Pakistan's capital with the iconic Faisal Mosque and Margalla Hills.",
        "images": [
            "National Faisal Mosque Islamabad.jpg",
            "Pakistan Monument islamabad.jpg",
            "Daman e koh.jpg",
        ],
    },
    {
        "city": "Karachi",
        "country": "Pakistan",
        "title": "Mazar-e-Quaid",
        "description": "Pakistan's largest coastal city, rich in history, culture and food.",
        "images": [
            "Mazar-E-Quaid.jpg",
            "Mazar e Quaid - Karachi.jpg",
            "MAZAR E QUAID.jpg",
        ],
    },
    {
        "city": "Rawalpindi",
        "country": "Pakistan",
        "title": "Historic Rawalpindi",
        "description": "A historic twin city known for its old bazaars and railway heritage.",
        "images": [
            "Rawalpindi Railway Station.jpg",
            "The Rawalpindi Railway Station.jpg",
            "Rawalpindi railway station.JPG",
        ],
    },
    {
        "city": "Murree",
        "country": "Pakistan",
        "title": "Murree Hills",
        "description": "A scenic hill destination famous for mountain views, forests and cool weather.",
        "images": [
            "Murree City Pakistan.jpg",
            "Murree-1.jpg",
            "Kashmir Point - Murree 1.jpg",
        ],
    },
]


def _image_url(filename: str) -> str:
    return "https://commons.wikimedia.org/wiki/Special:Redirect/file/" + quote(filename)


@router.get("/")
def list_trending_destinations():
    day_index = date.today().timetuple().tm_yday
    result = []

    for item in _DESTINATIONS:
        images = item["images"]
        image_index = (day_index - 1) % len(images)
        result.append(
            {
                "city": item["city"],
                "country": item["country"],
                "title": item["title"],
                "description": item["description"],
                "image_url": _image_url(images[image_index]),
                "image_day": day_index,
                "hotel_search_city": item["city"],
            }
        )

    return result
