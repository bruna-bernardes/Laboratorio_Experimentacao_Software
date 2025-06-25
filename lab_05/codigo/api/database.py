import sqlite3
import os
import random
import json

DB_PATH = os.path.join(os.path.dirname(__file__), "experiment.db")

COUNTRIES = [
    "Brazil", "United States", "China", "India", "Japan", "Germany", "France",
    "United Kingdom", "Italy", "Canada", "Australia", "Russia", "South Korea",
    "Spain", "Mexico", "Indonesia", "Netherlands", "Saudi Arabia", "Turkey",
    "Switzerland", "Argentina", "Sweden", "Norway", "Poland", "Belgium",
    "Austria", "Denmark", "Finland", "Ireland", "Portugal", "New Zealand",
    "Greece", "Czech Republic", "South Africa", "Colombia", "Thailand",
    "Vietnam", "Philippines", "Chile", "Peru", "Egypt", "Nigeria", "Kenya",
    "Morocco", "Ukraine", "Romania", "Hungary", "Israel", "Singapore",
    "Malaysia"
]

REGIONS = ["Americas", "Europe", "Asia", "Africa", "Oceania"]

LANGUAGES = [
    "Portuguese", "English", "Mandarin", "Hindi", "Japanese", "German",
    "French", "Italian", "Spanish", "Korean", "Dutch", "Arabic", "Turkish",
    "Swedish", "Norwegian", "Polish", "Danish", "Finnish", "Greek", "Czech",
    "Russian", "Thai", "Vietnamese", "Filipino", "Swahili", "Hebrew",
    "Romanian", "Hungarian", "Malay", "Ukrainian"
]

CITIES = [
    "Sao Paulo", "Rio de Janeiro", "Brasilia", "Salvador", "Fortaleza",
    "New York", "Los Angeles", "Chicago", "Houston", "Phoenix",
    "Shanghai", "Beijing", "Guangzhou", "Shenzhen", "Chengdu",
    "Mumbai", "Delhi", "Bangalore", "Chennai", "Kolkata",
    "Tokyo", "Osaka", "Yokohama", "Nagoya", "Sapporo",
    "Berlin", "Munich", "Hamburg", "Frankfurt", "Cologne",
    "Paris", "Marseille", "Lyon", "Toulouse", "Nice",
    "London", "Birmingham", "Manchester", "Leeds", "Liverpool",
    "Rome", "Milan", "Naples", "Turin", "Florence",
    "Toronto", "Vancouver", "Montreal", "Calgary", "Ottawa",
    "Sydney", "Melbourne", "Brisbane", "Perth", "Adelaide",
    "Moscow", "Saint Petersburg", "Novosibirsk", "Yekaterinburg", "Kazan",
    "Seoul", "Busan", "Incheon", "Daegu", "Daejeon",
    "Madrid", "Barcelona", "Valencia", "Seville", "Bilbao",
    "Mexico City", "Guadalajara", "Monterrey", "Puebla", "Tijuana",
    "Jakarta", "Surabaya", "Bandung", "Medan", "Semarang",
    "Amsterdam", "Rotterdam", "The Hague", "Utrecht", "Eindhoven",
    "Riyadh", "Jeddah", "Mecca", "Medina", "Dammam",
    "Istanbul", "Ankara", "Izmir", "Bursa", "Antalya",
    "Zurich", "Geneva", "Basel", "Bern", "Lausanne",
    "Buenos Aires", "Cordoba", "Rosario", "Mendoza", "La Plata",
    "Stockholm", "Gothenburg", "Malmo", "Uppsala", "Linkoping",
    "Oslo", "Bergen", "Stavanger", "Trondheim", "Tromso",
    "Warsaw", "Krakow", "Wroclaw", "Gdansk", "Poznan",
    "Brussels", "Antwerp", "Ghent", "Charleroi", "Liege",
    "Vienna", "Graz", "Linz", "Salzburg", "Innsbruck",
    "Copenhagen", "Aarhus", "Odense", "Aalborg", "Esbjerg",
    "Helsinki", "Espoo", "Tampere", "Oulu", "Turku",
    "Dublin", "Cork", "Limerick", "Galway", "Waterford",
    "Lisbon", "Porto", "Braga", "Coimbra", "Faro",
    "Auckland", "Wellington", "Christchurch", "Hamilton", "Dunedin",
    "Athens", "Thessaloniki", "Patras", "Heraklion", "Larissa",
    "Prague", "Brno", "Ostrava", "Plzen", "Liberec",
    "Johannesburg", "Cape Town", "Durban", "Pretoria", "Port Elizabeth",
    "Bogota", "Medellin", "Cali", "Barranquilla", "Cartagena",
    "Bangkok", "Chiang Mai", "Nakhon Ratchasima", "Hat Yai", "Pattaya",
    "Hanoi", "Ho Chi Minh City", "Da Nang", "Hai Phong", "Can Tho",
    "Manila", "Cebu", "Davao", "Quezon City", "Makati",
    "Santiago", "Valparaiso", "Concepcion", "La Serena", "Antofagasta",
    "Lima", "Arequipa", "Cusco", "Trujillo", "Chiclayo",
    "Cairo", "Alexandria", "Giza", "Shubra El Kheima", "Port Said",
    "Lagos", "Abuja", "Kano", "Ibadan", "Port Harcourt",
    "Nairobi", "Mombasa", "Kisumu", "Nakuru", "Eldoret",
    "Casablanca", "Rabat", "Marrakech", "Fes", "Tangier",
    "Kyiv", "Kharkiv", "Odessa", "Dnipro", "Donetsk",
    "Bucharest", "Cluj-Napoca", "Timisoara", "Iasi", "Constanta",
    "Budapest", "Debrecen", "Szeged", "Miskolc", "Pecs",
    "Tel Aviv", "Jerusalem", "Haifa", "Beersheba", "Ashdod",
    "Singapore City", "Woodlands", "Jurong East", "Tampines", "Bedok",
    "Kuala Lumpur", "Penang", "Johor Bahru", "Ipoh", "Shah Alam"
]


def create_database():
    if os.path.exists(DB_PATH):
        os.remove(DB_PATH)

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.executescript("""
        CREATE TABLE IF NOT EXISTS countries (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            region TEXT NOT NULL,
            population INTEGER NOT NULL,
            area REAL NOT NULL,
            gdp REAL,
            capital TEXT,
            established TEXT
        );

        CREATE TABLE IF NOT EXISTS languages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            family TEXT NOT NULL,
            speakers INTEGER NOT NULL,
            countries_count INTEGER NOT NULL,
            writing_system TEXT NOT NULL,
            is_official INTEGER NOT NULL DEFAULT 0
        );

        CREATE TABLE IF NOT EXISTS cities (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            country_id INTEGER NOT NULL,
            population INTEGER NOT NULL,
            area REAL NOT NULL,
            is_capital INTEGER NOT NULL DEFAULT 0,
            elevation INTEGER,
            timezone TEXT,
            FOREIGN KEY (country_id) REFERENCES countries(id)
        );

        CREATE TABLE IF NOT EXISTS country_languages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            country_id INTEGER NOT NULL,
            language_id INTEGER NOT NULL,
            is_official INTEGER NOT NULL DEFAULT 0,
            percentage REAL NOT NULL,
            FOREIGN KEY (country_id) REFERENCES countries(id),
            FOREIGN KEY (language_id) REFERENCES languages(id)
        );

        CREATE TABLE IF NOT EXISTS universities (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            country_id INTEGER NOT NULL,
            city_id INTEGER NOT NULL,
            founded_year INTEGER,
            students_count INTEGER,
            ranking INTEGER,
            type TEXT NOT NULL,
            FOREIGN KEY (country_id) REFERENCES countries(id),
            FOREIGN KEY (city_id) REFERENCES cities(id)
        );
    """)

    conn.commit()

    countries_data = []
    for i, country in enumerate(COUNTRIES):
        region = REGIONS[i % len(REGIONS)]
        population = random.randint(1_000_000, 1_400_000_000)
        area = random.uniform(20_000, 17_000_000)
        gdp = random.uniform(50_000_000_000, 25_000_000_000_000)
        capital = country + " City"
        established = f"{random.randint(1700, 1991)}-{random.randint(1,12):02d}-{random.randint(1,28):02d}"
        countries_data.append((country, region, population, area, gdp, capital, established))

    cursor.executemany(
        "INSERT INTO countries (name, region, population, area, gdp, capital, established) VALUES (?, ?, ?, ?, ?, ?, ?)",
        countries_data
    )

    families = ["Indo-European", "Sino-Tibetan", "Afro-Asiatic", "Austronesian", "Niger-Congo", "Turkic", "Uralic", "Japonic", "Koreanic", "Dravidian"]
    writing_systems = ["Latin", "Cyrillic", "Arabic", "Han", "Devanagari", "Hangul", "Hiragana", "Greek"]

    languages_data = []
    for i, lang in enumerate(LANGUAGES):
        family = families[i % len(families)]
        speakers = random.randint(1_000_000, 1_000_000_000)
        countries_count = random.randint(1, 50)
        writing = writing_systems[i % len(writing_systems)]
        is_official = random.randint(0, 1)
        languages_data.append((lang, family, speakers, countries_count, writing, is_official))

    cursor.executemany(
        "INSERT INTO languages (name, family, speakers, countries_count, writing_system, is_official) VALUES (?, ?, ?, ?, ?, ?)",
        languages_data
    )

    conn.commit()

    cities_data = []
    city_idx = 0
    for country_row in cursor.execute("SELECT id FROM countries ORDER BY id"):
        country_id = country_row[0]
        num_cities = random.randint(8, 15)
        for j in range(num_cities):
            if city_idx < len(CITIES):
                city_name = CITIES[city_idx]
                city_idx += 1
            else:
                city_name = f"City_{country_id}_{j}"
            city_pop = random.randint(100_000, 30_000_000)
            city_area = random.uniform(100, 30000)
            is_cap = 1 if j == 0 else 0
            elevation = random.randint(0, 4000)
            tz = f"UTC{'+' if random.random() > 0.3 else '-'}{random.randint(0,12)}"
            cities_data.append((city_name, country_id, city_pop, city_area, is_cap, elevation, tz))

    cursor.executemany(
        "INSERT INTO cities (name, country_id, population, area, is_capital, elevation, timezone) VALUES (?, ?, ?, ?, ?, ?, ?)",
        cities_data
    )

    conn.commit()

    country_langs = []
    for country_row in cursor.execute("SELECT id FROM countries ORDER BY id"):
        country_id = country_row[0]
        num_langs = random.randint(2, 5)
        lang_ids = random.sample(range(1, len(languages_data) + 1), min(num_langs, len(languages_data)))
        for lang_id in lang_ids:
            is_off = random.randint(0, 1)
            pct = random.uniform(5, 95)
            country_langs.append((country_id, lang_id, is_off, pct))

    cursor.executemany(
        "INSERT INTO country_languages (country_id, language_id, is_official, percentage) VALUES (?, ?, ?, ?)",
        country_langs
    )

    conn.commit()

    university_names = [
        "University of", "National University of", "Federal University of",
        "State University of", "Institute of Technology of", "Academy of",
        "Polytechnic of", "College of", "School of Mines of"
    ]

    universities_data = []
    for city_row in cursor.execute("SELECT id, country_id, name FROM cities ORDER BY id"):
        city_id, country_id, city_name = city_row
        num_unis = random.randint(1, 4)
        for k in range(num_unis):
            prefix = random.choice(university_names)
            uni_name = f"{prefix} {city_name}"
            founded = random.randint(1100, 2020)
            students = random.randint(5_000, 100_000)
            ranking = random.randint(1, 5000)
            utype = random.choice(["Public", "Private", "Research"])
            universities_data.append((uni_name, country_id, city_id, founded, students, ranking, utype))

    cursor.executemany(
        "INSERT INTO universities (name, country_id, city_id, founded_year, students_count, ranking, type) VALUES (?, ?, ?, ?, ?, ?, ?)",
        universities_data
    )

    conn.commit()

    count_countries = cursor.execute("SELECT COUNT(*) FROM countries").fetchone()[0]
    count_cities = cursor.execute("SELECT COUNT(*) FROM cities").fetchone()[0]
    count_languages = cursor.execute("SELECT COUNT(*) FROM languages").fetchone()[0]
    count_country_langs = cursor.execute("SELECT COUNT(*) FROM country_languages").fetchone()[0]
    count_universities = cursor.execute("SELECT COUNT(*) FROM universities").fetchone()[0]

    print(f"Banco criado com sucesso: {DB_PATH}")
    print(f"  Paises: {count_countries}")
    print(f"  Cidades: {count_cities}")
    print(f"  Linguas: {count_languages}")
    print(f"  Pais-Lingua: {count_country_langs}")
    print(f"  Universidades: {count_universities}")

    conn.close()


if __name__ == "__main__":
    create_database()