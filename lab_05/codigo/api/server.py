import sqlite3
import os
from typing import Optional, List
from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
import strawberry
from strawberry.fastapi import GraphQLRouter

DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "experiment.db")


def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA synchronous=NORMAL")
    return conn


app = FastAPI(title="GraphQL vs REST Experiment API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


# ===================== REST ENDPOINTS =====================

@app.get("/api/countries")
def list_countries(
    region: Optional[str] = Query(None),
    limit: int = Query(50, le=500),
    offset: int = Query(0, ge=0),
):
    conn = get_db()
    try:
        query = "SELECT * FROM countries"
        params = []
        if region:
            query += " WHERE region = ?"
            params.append(region)
        query += " ORDER BY id LIMIT ? OFFSET ?"
        params.extend([limit, offset])
        rows = conn.execute(query, params).fetchall()
        countries = [dict(r) for r in rows]
        return {"data": countries, "count": len(countries)}
    finally:
        conn.close()


@app.get("/api/countries/{country_id}")
def get_country(country_id: int):
    conn = get_db()
    try:
        row = conn.execute("SELECT * FROM countries WHERE id = ?", (country_id,)).fetchone()
        if not row:
            raise HTTPException(404, "Country not found")
        return dict(row)
    finally:
        conn.close()


@app.get("/api/countries/{country_id}/cities")
def get_country_cities(country_id: int):
    conn = get_db()
    try:
        rows = conn.execute("SELECT * FROM cities WHERE country_id = ?", (country_id,)).fetchall()
        return {"data": [dict(r) for r in rows]}
    finally:
        conn.close()


@app.get("/api/countries/{country_id}/languages")
def get_country_languages(country_id: int):
    conn = get_db()
    try:
        rows = conn.execute("""
            SELECT l.*, cl.is_official, cl.percentage
            FROM country_languages cl
            JOIN languages l ON cl.language_id = l.id
            WHERE cl.country_id = ?
        """, (country_id,)).fetchall()
        return {"data": [dict(r) for r in rows]}
    finally:
        conn.close()


@app.get("/api/countries/{country_id}/universities")
def get_country_universities(country_id: int):
    conn = get_db()
    try:
        rows = conn.execute("SELECT * FROM universities WHERE country_id = ?", (country_id,)).fetchall()
        return {"data": [dict(r) for r in rows]}
    finally:
        conn.close()


@app.get("/api/cities")
def list_cities(
    country_id: Optional[int] = Query(None),
    limit: int = Query(50, le=500),
    offset: int = Query(0, ge=0),
):
    conn = get_db()
    try:
        query = "SELECT * FROM cities"
        params = []
        if country_id:
            query += " WHERE country_id = ?"
            params.append(country_id)
        query += " ORDER BY id LIMIT ? OFFSET ?"
        params.extend([limit, offset])
        rows = conn.execute(query, params).fetchall()
        return {"data": [dict(r) for r in rows]}
    finally:
        conn.close()


@app.get("/api/languages")
def list_languages():
    conn = get_db()
    try:
        rows = conn.execute("SELECT * FROM languages ORDER BY id").fetchall()
        return {"data": [dict(r) for r in rows]}
    finally:
        conn.close()


@app.get("/api/universities")
def list_universities(
    country_id: Optional[int] = Query(None),
    city_id: Optional[int] = Query(None),
    limit: int = Query(50, le=500),
    offset: int = Query(0, ge=0),
):
    conn = get_db()
    try:
        query = "SELECT * FROM universities"
        conditions = []
        params = []
        if country_id:
            conditions.append("country_id = ?")
            params.append(country_id)
        if city_id:
            conditions.append("city_id = ?")
            params.append(city_id)
        if conditions:
            query += " WHERE " + " AND ".join(conditions)
        query += " ORDER BY id LIMIT ? OFFSET ?"
        params.extend([limit, offset])
        rows = conn.execute(query, params).fetchall()
        return {"data": [dict(r) for r in rows]}
    finally:
        conn.close()


# REST endpoint complexo: país com cidades, línguas e universidades (dados aninhados)
@app.get("/api/countries/{country_id}/details")
def get_country_details(country_id: int):
    conn = get_db()
    try:
        country = conn.execute("SELECT * FROM countries WHERE id = ?", (country_id,)).fetchone()
        if not country:
            raise HTTPException(404, "Country not found")
        result = dict(country)
        result["cities"] = [dict(r) for r in conn.execute("SELECT * FROM cities WHERE country_id = ?", (country_id,)).fetchall()]
        result["languages"] = [dict(r) for r in conn.execute("""
            SELECT l.*, cl.is_official, cl.percentage
            FROM country_languages cl JOIN languages l ON cl.language_id = l.id
            WHERE cl.country_id = ?
        """, (country_id,)).fetchall()]
        result["universities"] = [dict(r) for r in conn.execute("SELECT * FROM universities WHERE country_id = ?", (country_id,)).fetchall()]
        return result
    finally:
        conn.close()


# ===================== GRAPHQL SCHEMA =====================

@strawberry.type
class CountryType:
    id: int
    name: str
    region: str
    population: int
    area: float
    gdp: float
    capital: str
    established: str


@strawberry.type
class CityType:
    id: int
    name: str
    country_id: int
    population: int
    area: float
    is_capital: int
    elevation: int
    timezone: str


@strawberry.type
class LanguageType:
    id: int
    name: str
    family: str
    speakers: int
    countries_count: int
    writing_system: str
    is_official: int


@strawberry.type
class CountryLanguageType:
    id: int
    language: LanguageType
    is_official: int
    percentage: float


@strawberry.type
class UniversityType:
    id: int
    name: str
    country_id: int
    city_id: int
    founded_year: int
    students_count: int
    ranking: int
    type: str


@strawberry.type
class CountryDetailType:
    id: int
    name: str
    region: str
    population: int
    area: float
    gdp: float
    capital: str
    established: str
    cities: List[CityType]
    languages: List[CountryLanguageType]
    universities: List[UniversityType]


@strawberry.type
class Query:
    @strawberry.field
    def countries(self, region: Optional[str] = None, limit: int = 50, offset: int = 0) -> List[CountryType]:
        conn = get_db()
        try:
            query = "SELECT * FROM countries"
            params = []
            if region:
                query += " WHERE region = ?"
                params.append(region)
            query += " ORDER BY id LIMIT ? OFFSET ?"
            params.extend([limit, offset])
            rows = conn.execute(query, params).fetchall()
            return [CountryType(**dict(r)) for r in rows]
        finally:
            conn.close()

    @strawberry.field
    def country(self, country_id: int) -> Optional[CountryType]:
        conn = get_db()
        try:
            row = conn.execute("SELECT * FROM countries WHERE id = ?", (country_id,)).fetchone()
            if not row:
                return None
            return CountryType(**dict(row))
        finally:
            conn.close()

    @strawberry.field
    def country_detail(self, country_id: int) -> Optional[CountryDetailType]:
        conn = get_db()
        try:
            row = conn.execute("SELECT * FROM countries WHERE id = ?", (country_id,)).fetchone()
            if not row:
                return None
            c = dict(row)
            cities = [CityType(**dict(r)) for r in conn.execute("SELECT * FROM cities WHERE country_id = ?", (country_id,)).fetchall()]
            langs = []
            for lr in conn.execute("""
                SELECT l.*, cl.is_official, cl.percentage
                FROM country_languages cl JOIN languages l ON cl.language_id = l.id
                WHERE cl.country_id = ?
            """, (country_id,)).fetchall():
                ld = dict(lr)
                langs.append(CountryLanguageType(
                    id=ld["id"],
                    language=LanguageType(id=ld["id"], name=ld["name"], family=ld["family"],
                                          speakers=ld["speakers"], countries_count=ld["countries_count"],
                                          writing_system=ld["writing_system"], is_official=ld["is_official"]),
                    is_official=ld["is_official"],
                    percentage=ld["percentage"]
                ))
            unis = [UniversityType(**dict(r)) for r in conn.execute("SELECT * FROM universities WHERE country_id = ?", (country_id,)).fetchall()]
            return CountryDetailType(
                id=c["id"], name=c["name"], region=c["region"], population=c["population"],
                area=c["area"], gdp=c["gdp"], capital=c["capital"], established=c["established"],
                cities=cities, languages=langs, universities=unis
            )
        finally:
            conn.close()

    @strawberry.field
    def cities(self, country_id: Optional[int] = None, limit: int = 50, offset: int = 0) -> List[CityType]:
        conn = get_db()
        try:
            query = "SELECT * FROM cities"
            params = []
            if country_id:
                query += " WHERE country_id = ?"
                params.append(country_id)
            query += " ORDER BY id LIMIT ? OFFSET ?"
            params.extend([limit, offset])
            rows = conn.execute(query, params).fetchall()
            return [CityType(**dict(r)) for r in rows]
        finally:
            conn.close()

    @strawberry.field
    def languages(self) -> List[LanguageType]:
        conn = get_db()
        try:
            rows = conn.execute("SELECT * FROM languages ORDER BY id").fetchall()
            return [LanguageType(**dict(r)) for r in rows]
        finally:
            conn.close()

    @strawberry.field
    def universities(self, country_id: Optional[int] = None, city_id: Optional[int] = None, limit: int = 50, offset: int = 0) -> List[UniversityType]:
        conn = get_db()
        try:
            query = "SELECT * FROM universities"
            conditions = []
            params = []
            if country_id:
                conditions.append("country_id = ?")
                params.append(country_id)
            if city_id:
                conditions.append("city_id = ?")
                params.append(city_id)
            if conditions:
                query += " WHERE " + " AND ".join(conditions)
            query += " ORDER BY id LIMIT ? OFFSET ?"
            params.extend([limit, offset])
            rows = conn.execute(query, params).fetchall()
            return [UniversityType(**dict(r)) for r in rows]
        finally:
            conn.close()


schema = strawberry.Schema(query=Query)
graphql_app = GraphQLRouter(schema)

app.include_router(graphql_app, prefix="/graphql")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)