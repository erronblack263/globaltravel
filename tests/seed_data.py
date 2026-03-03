import asyncio
import uuid
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from core.database import AsyncSessionLocal, engine
from models.destination import Destination
from models import Base

async def seed_destinations():
    """Seed database with real holiday destinations."""
    
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    async with AsyncSessionLocal() as session:
        # Get existing destinations to avoid duplicates
        stmt = select(Destination)
        result = await session.execute(stmt)
        existing_destinations = result.scalars().all()
        existing_names = {dest.name for dest in existing_destinations}
        
        print(f"Found {len(existing_destinations)} existing destinations")
        
        # Real holiday destinations
        destinations = [
            # Beach Destinations
            Destination(
                name="Maldives Paradise Island",
                description="Luxurious tropical paradise with crystal-clear waters, overwater bungalows, and pristine white sand beaches. Perfect for honeymooners and luxury seekers.",
                type="beach",
                address="North Male Atoll, Maldives",
                city="Male",
                country="Maldives",
                latitude=3.2028,
                longitude=73.2207,
                entry_fee=0.0,
                visiting_hours="24/7",
                best_time_to_visit="November to April",
                images=[
                    "https://images.unsplash.com/photo-1573843981797-4fbc1f588c74?w=800",
                    "https://images.unsplash.com/photo-1506905925346-21bda4d32df4?w=800"
                ],
                is_active=True
            ),
            Destination(
                name="Santorini, Greece",
                description="Iconic Greek island known for stunning sunsets, white-washed buildings, blue-domed churches, and dramatic cliffs overlooking the Aegean Sea.",
                type="beach",
                address="Santorini, Cyclades, Greece",
                city="Santorini",
                country="Greece",
                latitude=36.3932,
                longitude=25.4615,
                entry_fee=0.0,
                visiting_hours="24/7",
                best_time_to_visit="April to November",
                images=[
                    "https://images.unsplash.com/photo-1570077188670-e3a8d69ac5ff?w=800",
                    "https://images.unsplash.com/photo-1533105079780-92b9be482077?w=800"
                ],
                is_active=True
            ),
            Destination(
                name="Bali, Indonesia",
                description="Tropical paradise known for ancient temples, terraced rice paddies, volcanic mountains, and world-class surfing beaches with rich Hindu culture.",
                type="beach",
                address="Bali, Indonesia",
                city="Denpasar",
                country="Indonesia",
                latitude=-8.3405,
                longitude=115.0920,
                entry_fee=0.0,
                visiting_hours="24/7",
                best_time_to_visit="April to October",
                images=[
                    "https://images.unsplash.com/photo-1537953773345-b1725c77a85a?w=800",
                    "https://images.unsplash.com/photo-1518548419970-58b3f7f4f9bb?w=800"
                ],
                is_active=True
            ),
            Destination(
                name="Phuket, Thailand",
                description="Thailand's largest island offering stunning beaches, crystal-clear waters, vibrant nightlife, and exotic Thai culture with world-class resorts.",
                type="beach",
                address="Phuket, Thailand",
                city="Phuket",
                country="Thailand",
                latitude=7.8804,
                longitude=98.3923,
                entry_fee=0.0,
                visiting_hours="24/7",
                best_time_to_visit="November to March",
                images=[
                    "https://images.unsplash.com/photo-1506905925346-21bda4d32df4?w=800",
                    "https://images.unsplash.com/photo-1542560885-a448e8100b6c?w=800"
                ],
                is_active=True
            ),
            Destination(
                name="Maui, Hawaii",
                description="Hawaiian paradise featuring dramatic volcanic landscapes, pristine beaches, whale watching, and the legendary Road to Hana with tropical rainforests.",
                type="beach",
                address="Maui, Hawaii, USA",
                city="Wailuku",
                country="United States",
                latitude=20.7984,
                longitude=-156.3319,
                entry_fee=0.0,
                visiting_hours="24/7",
                best_time_to_visit="April to May, September to November",
                images=[
                    "https://images.unsplash.com/photo-1542560885-a448e8100b6c?w=800",
                    "https://images.unsplash.com/photo-1507525428034-b723cf961d3e?w=800"
                ],
                is_active=True
            ),
            
            # Mountain Destinations
            Destination(
                name="Swiss Alps - Interlaken",
                description="Breathtaking mountain paradise nestled between two lakes, offering world-class skiing, hiking, and stunning Alpine scenery with snow-capped peaks year-round.",
                type="mountain",
                address="Interlaken, Bernese Oberland, Switzerland",
                city="Interlaken",
                country="Switzerland",
                latitude=46.6863,
                longitude=7.8633,
                entry_fee=0.0,
                visiting_hours="24/7",
                best_time_to_visit="June to September (hiking), December to March (skiing)",
                images=[
                    "https://images.unsplash.com/photo-1559827260-dc66d52bef19?w=800",
                    "https://images.unsplash.com/photo-1542560885-a448e8100b6c?w=800"
                ],
                is_active=True
            ),
            Destination(
                name="Dolomites, Italy",
                description="UNESCO World Heritage site featuring dramatic limestone peaks, charming alpine villages, and some of the most beautiful mountain landscapes in Europe.",
                type="mountain",
                address="Dolomites, South Tyrol, Italy",
                city="Cortina d'Ampezzo",
                country="Italy",
                latitude=46.4192,
                longitude=11.8698,
                entry_fee=0.0,
                visiting_hours="24/7",
                best_time_to_visit="June to September",
                images=[
                    "https://images.unsplash.com/photo-1559827261-a4b2216d3b2a?w=800",
                    "https://images.unsplash.com/photo-1464822759844-d150baec0494?w=800"
                ],
                is_active=True
            ),
            Destination(
                name="Rocky Mountains - Colorado",
                description="Majestic mountain range offering pristine wilderness, alpine lakes, wildlife, and world-class skiing in the heart of the American West.",
                type="mountain",
                address="Rocky Mountain National Park, Colorado, USA",
                city="Estes Park",
                country="United States",
                latitude=40.3428,
                longitude=-105.6836,
                entry_fee=30.0,
                visiting_hours="24/7",
                best_time_to_visit="June to September",
                images=[
                    "https://images.unsplash.com/photo-1506905925346-21bda4d32df4?w=800",
                    "https://images.unsplash.com/photo-1542546569-159d0a8c5d1d?w=800"
                ],
                is_active=True
            ),
            Destination(
                name="Himalayas - Nepal",
                description="World's highest mountain range featuring Mount Everest, ancient monasteries, Sherpa culture, and breathtaking trekking adventures.",
                type="mountain",
                address="Himalayas, Nepal",
                city="Kathmandu",
                country="Nepal",
                latitude=27.9881,
                longitude=86.9250,
                entry_fee=50.0,
                visiting_hours="24/7",
                best_time_to_visit="March to May, October to November",
                images=[
                    "https://images.unsplash.com/photo-1542560885-a448e8100b6c?w=800",
                    "https://images.unsplash.com/photo-1506905925346-21bda4d32df4?w=800"
                ],
                is_active=True
            ),
            
            # City Destinations
            Destination(
                name="Paris, France",
                description="The City of Light offers iconic landmarks like the Eiffel Tower, Louvre Museum, charming cafés, world-class shopping, and romantic atmosphere along the Seine.",
                type="city",
                address="Paris, Île-de-France, France",
                city="Paris",
                country="France",
                latitude=48.8566,
                longitude=2.3522,
                entry_fee=0.0,
                visiting_hours="24/7",
                best_time_to_visit="April to June, September to October",
                images=[
                    "https://images.unsplash.com/photo-1502602898657-3e91760cbb34?w=800",
                    "https://images.unsplash.com/photo-1549144511-f099e776c147?w=800"
                ],
                is_active=True
            ),
            Destination(
                name="Tokyo, Japan",
                description="Ultra-modern metropolis blending ancient traditions with cutting-edge technology, featuring temples, neon-lit streets, incredible cuisine, and unique pop culture.",
                type="city",
                address="Tokyo, Kanto Region, Japan",
                city="Tokyo",
                country="Japan",
                latitude=35.6762,
                longitude=139.6503,
                entry_fee=0.0,
                visiting_hours="24/7",
                best_time_to_visit="March to May, October to November",
                images=[
                    "https://images.unsplash.com/photo-1493976040374-85c8e12f0c0e?w=800",
                    "https://images.unsplash.com/photo-1540959733332-eab4deabeeaf?w=800"
                ],
                is_active=True
            ),
            Destination(
                name="New York City, USA",
                description="The Big Apple offers iconic skyscrapers, world-class museums, Broadway shows, Central Park, and diverse neighborhoods with endless entertainment.",
                type="city",
                address="New York, New York, USA",
                city="New York",
                country="United States",
                latitude=40.7128,
                longitude=-74.0060,
                entry_fee=0.0,
                visiting_hours="24/7",
                best_time_to_visit="April to June, September to November",
                images=[
                    "https://images.unsplash.com/photo-1496442226666-8ee41729d9cc?w=800",
                    "https://images.unsplash.com/photo-1518391846015-55a9cc003b25?w=800"
                ],
                is_active=True
            ),
            Destination(
                name="London, England",
                description="Historic capital featuring Tower Bridge, Big Ben, Buckingham Palace, world-class museums, royal history, and vibrant multicultural neighborhoods.",
                type="city",
                address="London, England, UK",
                city="London",
                country="United Kingdom",
                latitude=51.5074,
                longitude=-0.1278,
                entry_fee=0.0,
                visiting_hours="24/7",
                best_time_to_visit="May to September",
                images=[
                    "https://images.unsplash.com/photo-1515169460161-ted1a2737b81?w=800",
                    "https://images.unsplash.com/photo-1506905925346-21bda4d32df4?w=800"
                ],
                is_active=True
            ),
            Destination(
                name="Dubai, UAE",
                description="Futuristic oasis featuring the world's tallest building, luxury shopping, artificial islands, desert safaris, and stunning modern architecture.",
                type="city",
                address="Dubai, United Arab Emirates",
                city="Dubai",
                country="United Arab Emirates",
                latitude=25.2048,
                longitude=55.2708,
                entry_fee=0.0,
                visiting_hours="24/7",
                best_time_to_visit="November to March",
                images=[
                    "https://images.unsplash.com/photo-1512458937872-8e41a557a5d2?w=800",
                    "https://images.unsplash.com/photo-1542560885-a448e8100b6c?w=800"
                ],
                is_active=True
            ),
            
            # Cultural/Historical Destinations
            Destination(
                name="Machu Picchu, Peru",
                description="Ancient Incan citadel set high in the Andes Mountains, featuring mysterious stone structures, terraced hills, and breathtaking panoramic views.",
                type="cultural",
                address="Cusco Region, Peru",
                city="Cusco",
                country="Peru",
                latitude=-13.1631,
                longitude=-72.5450,
                entry_fee=70.0,
                visiting_hours="6:00 AM - 5:30 PM",
                best_time_to_visit="May to September",
                images=[
                    "https://images.unsplash.com/photo-1526392060635-9d6019884377?w=800",
                    "https://images.unsplash.com/photo-1587595431973-160d30d77fa1?w=800"
                ],
                is_active=True
            ),
            Destination(
                name="Petra, Jordan",
                description="Ancient archaeological wonder carved into rose-red cliffs, featuring the iconic Treasury building, elaborate facades, and rich Nabataean history.",
                type="cultural",
                address="Ma'an Governorate, Jordan",
                city="Petra",
                country="Jordan",
                latitude=30.3285,
                longitude=35.4444,
                entry_fee=50.0,
                visiting_hours="6:00 AM - 6:00 PM",
                best_time_to_visit="March to May, September to November",
                images=[
                    "https://images.unsplash.com/photo-1596445836528-2d6b5ab244d1?w=800",
                    "https://images.unsplash.com/photo-1544191516-5ba0c9c8b7b5?w=800"
                ],
                is_active=True
            ),
            Destination(
                name="Rome, Italy",
                description="Eternal City featuring Colosseum, Vatican City, ancient ruins, Renaissance art, world-class cuisine, and 3,000 years of history.",
                type="cultural",
                address="Rome, Italy",
                city="Rome",
                country="Italy",
                latitude=41.9028,
                longitude=12.4964,
                entry_fee=0.0,
                visiting_hours="24/7",
                best_time_to_visit="April to June, September to October",
                images=[
                    "https://images.unsplash.com/photo-1552832230-c21998305cd1?w=800",
                    "https://images.unsplash.com/photo-1506905925346-21bda4d32df4?w=800"
                ],
                is_active=True
            ),
            Destination(
                name="Cairo, Egypt",
                description="Ancient capital home to the Great Pyramids, Sphinx, Egyptian Museum, Islamic architecture, and thousands of years of pharaonic history.",
                type="cultural",
                address="Cairo, Egypt",
                city="Cairo",
                country="Egypt",
                latitude=30.0444,
                longitude=31.2357,
                entry_fee=40.0,
                visiting_hours="24/7",
                best_time_to_visit="October to April",
                images=[
                    "https://images.unsplash.com/photo-1548546283-91d6d9bfaa0e?w=800",
                    "https://images.unsplash.com/photo-1506905925346-21bda4d32df4?w=800"
                ],
                is_active=True
            ),
            Destination(
                name="Athens, Greece",
                description="Cradle of Western civilization featuring the Acropolis, Parthenon, ancient Agora, and birthplace of democracy, philosophy, and Olympic Games.",
                type="cultural",
                address="Athens, Greece",
                city="Athens",
                country="Greece",
                latitude=37.9838,
                longitude=23.7275,
                entry_fee=20.0,
                visiting_hours="24/7",
                best_time_to_visit="April to June, September to October",
                images=[
                    "https://images.unsplash.com/photo-1542560885-a448e8100b6c?w=800",
                    "https://images.unsplash.com/photo-1506905925346-21bda4d32df4?w=800"
                ],
                is_active=True
            ),
            
            # Adventure Destinations
            Destination(
                name="Iceland - Golden Circle",
                description="Land of fire and ice featuring geysers, waterfalls, volcanic landscapes, Northern Lights, and unique geological formations for adventure seekers.",
                type="adventure",
                address="Golden Circle, Iceland",
                city="Reykjavik",
                country="Iceland",
                latitude=64.9631,
                longitude=-19.0208,
                entry_fee=0.0,
                visiting_hours="24/7",
                best_time_to_visit="June to August (midnight sun), September to March (Northern Lights)",
                images=[
                    "https://images.unsplash.com/photo-1506905925346-21bda4d32df4?w=800",
                    "https://images.unsplash.com/photo-1542546569-159d0a8c5d1d?w=800"
                ],
                is_active=True
            ),
            Destination(
                name="Costa Rica Rainforest",
                description="Biodiverse paradise offering zip-lining, volcano tours, wildlife encounters, surfing, and eco-adventures in lush tropical rainforests.",
                type="adventure",
                address="Monteverde, Puntarenas, Costa Rica",
                city="Monteverde",
                country="Costa Rica",
                latitude=10.3007,
                longitude=-84.8168,
                entry_fee=25.0,
                visiting_hours="7:00 AM - 5:00 PM",
                best_time_to_visit="December to April",
                images=[
                    "https://images.unsplash.com/photo-1518548419970-58b3f7f4f9bb?w=800",
                    "https://images.unsplash.com/photo-1506905925346-21bda4d32df4?w=800"
                ],
                is_active=True
            ),
            Destination(
                name="Grand Canyon, Arizona",
                description="Natural wonder featuring dramatic red rock formations, Colorado River carving, hiking trails, and some of the most spectacular views on Earth.",
                type="adventure",
                address="Grand Canyon National Park, Arizona, USA",
                city="Grand Canyon Village",
                country="United States",
                latitude=36.1069,
                longitude=-112.1129,
                entry_fee=35.0,
                visiting_hours="24/7",
                best_time_to_visit="March to May, September to November",
                images=[
                    "https://images.unsplash.com/photo-1506905925346-21bda4d32df4?w=800",
                    "https://images.unsplash.com/photo-1542546569-159d0a8c5d1d?w=800"
                ],
                is_active=True
            ),
            Destination(
                name="Amazon Rainforest, Brazil",
                description="World's largest tropical rainforest offering incredible biodiversity, river cruises, wildlife encounters, and indigenous culture experiences.",
                type="adventure",
                address="Amazon Rainforest, Brazil",
                city="Manaus",
                country="Brazil",
                latitude=-3.4653,
                longitude=-62.2159,
                entry_fee=100.0,
                visiting_hours="24/7",
                best_time_to_visit="June to November",
                images=[
                    "https://images.unsplash.com/photo-1542560885-a448e8100b6c?w=800",
                    "https://images.unsplash.com/photo-1506905925346-21bda4d32df4?w=800"
                ],
                is_active=True
            ),
            Destination(
                name="Safari - Serengeti, Tanzania",
                description="Ultimate wildlife adventure featuring the Great Migration, Big Five animals, endless savanna plains, and authentic African safari experiences.",
                type="adventure",
                address="Serengeti National Park, Tanzania",
                city="Arusha",
                country="Tanzania",
                latitude=-2.3333,
                longitude=34.8333,
                entry_fee=60.0,
                visiting_hours="6:00 AM - 6:00 PM",
                best_time_to_visit="June to October, January to February",
                images=[
                    "https://images.unsplash.com/photo-1542560885-a448e8100b6c?w=800",
                    "https://images.unsplash.com/photo-1506905925346-21bda4d32df4?w=800"
                ],
                is_active=True
            )
        ]
        
        # Add only new destinations to database
        new_destinations = []
        for destination in destinations:
            if destination.name not in existing_names:
                new_destinations.append(destination)
        
        if new_destinations:
            for destination in new_destinations:
                session.add(destination)
            
            await session.commit()
            print(f"Successfully added {len(new_destinations)} new destinations!")
            print(f"Total destinations: {len(existing_destinations) + len(new_destinations)}")
        else:
            print("No new destinations to add (all already exist)")

if __name__ == "__main__":
    asyncio.run(seed_destinations())
