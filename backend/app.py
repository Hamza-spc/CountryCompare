from flask import Flask, request, jsonify
from flask_restful import Api, Resource
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from datetime import datetime, timedelta
import requests
import os
from functools import lru_cache
import logging
from dataclasses import dataclass
from typing import Dict, List, Optional
import json

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-secret-key')
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get(
    'DATABASE_URL', 
    'sqlite:///countrycompare.db'
)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize extensions
db = SQLAlchemy(app)
migrate = Migrate(app, db)
api = Api(app)
CORS(app)

# Data classes for clean data structures
@dataclass
class CountryInfo:
    name: str
    capital: str
    population: int
    area: float
    region: str
    subregion: str
    currency: str
    flag_url: str
    gdp: Optional[float] = None
    gdp_per_capita: Optional[float] = None
    hdi: Optional[float] = None
    life_expectancy: Optional[float] = None
    internet_penetration: Optional[float] = None
    last_updated: Optional[datetime] = None

@dataclass
class ComparisonResult:
    country1: CountryInfo
    country2: CountryInfo
    comparison_metrics: Dict[str, Dict[str, float]]

# Database Models
class Country(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)
    capital = db.Column(db.String(100), nullable=False)
    population = db.Column(db.BigInteger, nullable=False)
    area = db.Column(db.Float, nullable=False)
    region = db.Column(db.String(100), nullable=False)
    subregion = db.Column(db.String(100), nullable=False)
    currency = db.Column(db.String(50), nullable=False)
    flag_url = db.Column(db.String(255), nullable=False)
    gdp = db.Column(db.Float, nullable=True)
    gdp_per_capita = db.Column(db.Float, nullable=True)
    hdi = db.Column(db.Float, nullable=True)
    life_expectancy = db.Column(db.Float, nullable=True)
    internet_penetration = db.Column(db.Float, nullable=True)
    last_updated = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'capital': self.capital,
            'population': self.population,
            'area': self.area,
            'region': self.region,
            'subregion': self.subregion,
            'currency': self.currency,
            'flag_url': self.flag_url,
            'gdp': self.gdp,
            'gdp_per_capita': self.gdp_per_capita,
            'hdi': self.hdi,
            'life_expectancy': self.life_expectancy,
            'internet_penetration': self.internet_penetration,
            'last_updated': self.last_updated.isoformat() if self.last_updated else None
        }

class Comparison(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    country1_name = db.Column(db.String(100), nullable=False)
    country2_name = db.Column(db.String(100), nullable=False)
    comparison_data = db.Column(db.Text, nullable=False)  # JSON string
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'country1_name': self.country1_name,
            'country2_name': self.country2_name,
            'comparison_data': json.loads(self.comparison_data),
            'created_at': self.created_at.isoformat()
        }

# API Service Classes
class RestCountriesService:
    BASE_URL = "https://restcountries.com/v3.1"
    
    @staticmethod
    def get_all_countries():
        """Fetch all countries from REST Countries API"""
        try:
            response = requests.get(f"{RestCountriesService.BASE_URL}/all", timeout=10)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            logger.error(f"Error fetching countries: {e}")
            return []
    
    @staticmethod
    def get_country_details(country_name):
        """Fetch details for a specific country"""
        try:
            response = requests.get(
                f"{RestCountriesService.BASE_URL}/name/{country_name}", 
                timeout=10
            )
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            logger.error(f"Error fetching country {country_name}: {e}")
            return None

class WorldBankService:
    BASE_URL = "https://api.worldbank.org/v2"
    
    @staticmethod
    def get_gdp_data(country_code, year=2022):
        """Fetch GDP data from World Bank API"""
        try:
            # This is a simplified version - you'd need to map country names to ISO codes
            response = requests.get(
                f"{WorldBankService.BASE_URL}/country/{country_code}/indicator/NY.GDP.MKTP.CD",
                params={'date': year, 'format': 'json'},
                timeout=10
            )
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            logger.error(f"Error fetching GDP data for {country_code}: {e}")
            return None

# Cache for API responses
class APICache:
    _cache = {}
    
    @staticmethod
    def get(key):
        if key in APICache._cache:
            data, timestamp = APICache._cache[key]
            if datetime.now() - timestamp < timedelta(hours=1):
                return data
            else:
                del APICache._cache[key]
        return None
    
    @staticmethod
    def set(key, data):
        APICache._cache[key] = (data, datetime.now())
    
    @staticmethod
    def clear():
        APICache._cache.clear()

# Helper functions
def parse_country_data(country_data, additional_data=None):
    """Parse country data from REST Countries API"""
    try:
        currencies = country_data.get('currencies', {})
        currency_name = list(currencies.keys())[0] if currencies else 'Unknown'
        
        return CountryInfo(
            name=country_data.get('name', {}).get('common', 'Unknown'),
            capital=', '.join(country_data.get('capital', ['Unknown'])),
            population=country_data.get('population', 0),
            area=country_data.get('area', 0.0),
            region=country_data.get('region', 'Unknown'),
            subregion=country_data.get('subregion', 'Unknown'),
            currency=currency_name,
            flag_url=country_data.get('flags', {}).get('png', ''),
            gdp=additional_data.get('gdp') if additional_data else None,
            gdp_per_capita=additional_data.get('gdp_per_capita') if additional_data else None,
            hdi=additional_data.get('hdi') if additional_data else None,
            life_expectancy=additional_data.get('life_expectancy') if additional_data else None,
            internet_penetration=additional_data.get('internet_penetration') if additional_data else None,
            last_updated=datetime.utcnow()
        )
    except Exception as e:
        logger.error(f"Error parsing country data: {e}")
        return None

def get_or_create_country(country_info):
    """Get country from database or create if not exists"""
    country = Country.query.filter_by(name=country_info.name).first()
    
    if not country:
        country = Country(
            name=country_info.name,
            capital=country_info.capital,
            population=country_info.population,
            area=country_info.area,
            region=country_info.region,
            subregion=country_info.subregion,
            currency=country_info.currency,
            flag_url=country_info.flag_url,
            gdp=country_info.gdp,
            gdp_per_capita=country_info.gdp_per_capita,
            hdi=country_info.hdi,
            life_expectancy=country_info.life_expectancy,
            internet_penetration=country_info.internet_penetration,
            last_updated=country_info.last_updated
        )
        db.session.add(country)
        db.session.commit()
    elif country.last_updated < datetime.utcnow() - timedelta(days=1):
        # Update if data is older than 1 day
        country.population = country_info.population
        country.area = country_info.area
        country.gdp = country_info.gdp
        country.gdp_per_capita = country_info.gdp_per_capita
        country.hdi = country_info.hdi
        country.life_expectancy = country_info.life_expectancy
        country.internet_penetration = country_info.internet_penetration
        country.last_updated = country_info.last_updated
        db.session.commit()
    
    return country

# API Resources
class CountriesResource(Resource):
    def get(self):
        """Get all countries"""
        try:
            # Check cache first
            cache_key = "all_countries"
            cached_data = APICache.get(cache_key)
            if cached_data:
                return jsonify(cached_data)
            
            # Fetch from database first
            countries = Country.query.all()
            if countries:
                result = [country.to_dict() for country in countries]
                APICache.set(cache_key, result)
                return jsonify(result)
            
            # If no data in database, fetch from API
            countries_data = RestCountriesService.get_all_countries()
            result = []
            
            for country_data in countries_data[:50]:  # Limit to first 50 for demo
                country_info = parse_country_data(country_data)
                if country_info:
                    country = get_or_create_country(country_info)
                    result.append(country.to_dict())
            
            APICache.set(cache_key, result)
            return jsonify(result)
            
        except Exception as e:
            logger.error(f"Error in CountriesResource: {e}")
            return {'error': 'Failed to fetch countries'}, 500

class CountryResource(Resource):
    def get(self, country_name):
        """Get details for a specific country"""
        try:
            # Check database first
            country = Country.query.filter_by(name=country_name).first()
            if country and country.last_updated > datetime.utcnow() - timedelta(hours=1):
                return jsonify(country.to_dict())
            
            # Fetch from API
            country_data = RestCountriesService.get_country_details(country_name)
            if not country_data:
                return {'error': 'Country not found'}, 404
            
            country_info = parse_country_data(country_data[0])
            if not country_info:
                return {'error': 'Failed to parse country data'}, 500
            
            country = get_or_create_country(country_info)
            return jsonify(country.to_dict())
            
        except Exception as e:
            logger.error(f"Error in CountryResource: {e}")
            return {'error': 'Failed to fetch country details'}, 500

class CompareResource(Resource):
    def get(self):
        """Compare two countries"""
        try:
            country1_name = request.args.get('c1')
            country2_name = request.args.get('c2')
            
            if not country1_name or not country2_name:
                return {'error': 'Both country parameters (c1 and c2) are required'}, 400
            
            # Get countries from database
            country1 = Country.query.filter_by(name=country1_name).first()
            country2 = Country.query.filter_by(name=country2_name).first()
            
            if not country1:
                country1_data = RestCountriesService.get_country_details(country1_name)
                if country1_data:
                    country1_info = parse_country_data(country1_data[0])
                    country1 = get_or_create_country(country1_info)
                else:
                    return {'error': f'Country {country1_name} not found'}, 404
            
            if not country2:
                country2_data = RestCountriesService.get_country_details(country2_name)
                if country2_data:
                    country2_info = parse_country_data(country2_data[0])
                    country2 = get_or_create_country(country2_info)
                else:
                    return {'error': f'Country {country2_name} not found'}, 404
            
            # Create comparison metrics
            comparison_metrics = {
                'population': {
                    'country1': country1.population,
                    'country2': country2.population,
                    'winner': country1_name if country1.population > country2.population else country2_name
                },
                'area': {
                    'country1': country1.area,
                    'country2': country2.area,
                    'winner': country1_name if country1.area > country2.area else country2_name
                },
                'gdp': {
                    'country1': country1.gdp or 0,
                    'country2': country2.gdp or 0,
                    'winner': country1_name if (country1.gdp or 0) > (country2.gdp or 0) else country2_name
                },
                'gdp_per_capita': {
                    'country1': country1.gdp_per_capita or 0,
                    'country2': country2.gdp_per_capita or 0,
                    'winner': country1_name if (country1.gdp_per_capita or 0) > (country2.gdp_per_capita or 0) else country2_name
                },
                'hdi': {
                    'country1': country1.hdi or 0,
                    'country2': country2.hdi or 0,
                    'winner': country1_name if (country1.hdi or 0) > (country2.hdi or 0) else country2_name
                },
                'life_expectancy': {
                    'country1': country1.life_expectancy or 0,
                    'country2': country2.life_expectancy or 0,
                    'winner': country1_name if (country1.life_expectancy or 0) > (country2.life_expectancy or 0) else country2_name
                },
                'internet_penetration': {
                    'country1': country1.internet_penetration or 0,
                    'country2': country2.internet_penetration or 0,
                    'winner': country1_name if (country1.internet_penetration or 0) > (country2.internet_penetration or 0) else country2_name
                }
            }
            
            result = {
                'country1': country1.to_dict(),
                'country2': country2.to_dict(),
                'comparison_metrics': comparison_metrics
            }
            
            # Store comparison in database
            comparison = Comparison(
                country1_name=country1_name,
                country2_name=country2_name,
                comparison_data=json.dumps(result)
            )
            db.session.add(comparison)
            db.session.commit()
            
            return jsonify(result)
            
        except Exception as e:
            logger.error(f"Error in CompareResource: {e}")
            return {'error': 'Failed to compare countries'}, 500

# API Routes
api.add_resource(CountriesResource, '/api/countries')
api.add_resource(CountryResource, '/api/countries/<string:country_name>')
api.add_resource(CompareResource, '/api/compare')

@app.route('/api/health')
def health_check():
    """Health check endpoint"""
    return jsonify({'status': 'healthy', 'timestamp': datetime.utcnow().isoformat()})

@app.route('/')
def index():
    """Root endpoint"""
    return jsonify({
        'message': 'CountryCompare API',
        'version': '1.0.0',
        'endpoints': {
            'countries': '/api/countries',
            'country_details': '/api/countries/<name>',
            'compare': '/api/compare?c1=<country1>&c2=<country2>',
            'health': '/api/health'
        }
    })

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True, host='0.0.0.0', port=5001)
