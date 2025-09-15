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
    __tablename__ = 'countries'
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
    __tablename__ = 'comparisons'
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
            fields = "name,capital,population,area,region,subregion,currencies,flags"
            response = requests.get(f"{RestCountriesService.BASE_URL}/all?fields={fields}", timeout=10)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            logger.error(f"Error fetching countries: {e}")
            return []
    
    @staticmethod
    def get_country_details(country_name):
        """Fetch details for a specific country"""
        try:
            fields = "name,capital,population,area,region,subregion,currencies,flags"
            response = requests.get(
                f"{RestCountriesService.BASE_URL}/name/{country_name}?fields={fields}", 
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
def get_sample_economic_data(country_name, population, region=None):
    """Generate sample economic data for demonstration purposes"""
    # This is sample data for demonstration - in production you'd fetch from World Bank API
    sample_data = {
        'Morocco': {'gdp': 126000000000, 'hdi': 0.683, 'life_expectancy': 76.1, 'internet_penetration': 74.4},
        'Algeria': {'gdp': 163000000000, 'hdi': 0.748, 'life_expectancy': 77.0, 'internet_penetration': 63.0},
        'Jamaica': {'gdp': 15000000000, 'hdi': 0.734, 'life_expectancy': 74.5, 'internet_penetration': 55.0},
        'Comoros': {'gdp': 1200000000, 'hdi': 0.554, 'life_expectancy': 64.3, 'internet_penetration': 8.0},
        'United Kingdom': {'gdp': 3100000000000, 'hdi': 0.929, 'life_expectancy': 81.3, 'internet_penetration': 95.0},
        'Germany': {'gdp': 4200000000000, 'hdi': 0.942, 'life_expectancy': 81.0, 'internet_penetration': 90.0},
        'Brazil': {'gdp': 1600000000000, 'hdi': 0.754, 'life_expectancy': 75.9, 'internet_penetration': 70.0},
        'China': {'gdp': 18000000000000, 'hdi': 0.761, 'life_expectancy': 77.1, 'internet_penetration': 70.0},
        'United States': {'gdp': 25000000000000, 'hdi': 0.921, 'life_expectancy': 78.9, 'internet_penetration': 90.0},
        'Japan': {'gdp': 4900000000000, 'hdi': 0.919, 'life_expectancy': 84.6, 'internet_penetration': 93.0},
        'India': {'gdp': 3400000000000, 'hdi': 0.645, 'life_expectancy': 70.4, 'internet_penetration': 45.0},
        'France': {'gdp': 2900000000000, 'hdi': 0.901, 'life_expectancy': 82.7, 'internet_penetration': 88.0},
        'Canada': {'gdp': 2000000000000, 'hdi': 0.929, 'life_expectancy': 82.3, 'internet_penetration': 95.0},
        'Australia': {'gdp': 1600000000000, 'hdi': 0.944, 'life_expectancy': 83.4, 'internet_penetration': 90.0},
        'South Korea': {'gdp': 1800000000000, 'hdi': 0.906, 'life_expectancy': 83.0, 'internet_penetration': 96.0},
        'Italy': {'gdp': 2100000000000, 'hdi': 0.895, 'life_expectancy': 83.5, 'internet_penetration': 76.0},
        'Spain': {'gdp': 1400000000000, 'hdi': 0.904, 'life_expectancy': 83.2, 'internet_penetration': 88.0},
        'Mexico': {'gdp': 1300000000000, 'hdi': 0.779, 'life_expectancy': 75.0, 'internet_penetration': 70.0},
        'Russia': {'gdp': 1800000000000, 'hdi': 0.824, 'life_expectancy': 73.2, 'internet_penetration': 80.0},
        'South Africa': {'gdp': 420000000000, 'hdi': 0.713, 'life_expectancy': 64.3, 'internet_penetration': 60.0}
    }
    
    data = sample_data.get(country_name, {})
    if data:
        gdp_per_capita = data['gdp'] / population if population > 0 else 0
        return {
            'gdp': data.get('gdp', 0),
            'gdp_per_capita': gdp_per_capita,
            'hdi': data.get('hdi', 0),
            'life_expectancy': data.get('life_expectancy', 0),
            'internet_penetration': data.get('internet_penetration', 0)
        }
    
    # Fallback: Generate realistic economic data based on population and region
    # This ensures all countries have economic data
    region_multipliers = {
        'Europe': 1.5,
        'North America': 1.8,
        'Asia': 0.8,
        'South America': 0.6,
        'Africa': 0.3,
        'Oceania': 1.2
    }
    
    # Estimate GDP based on population and region
    base_gdp_per_capita = 5000  # Base GDP per capita
    region_key = region if region else 'Asia'  # Use provided region or default to Asia
    multiplier = region_multipliers.get(region_key, 0.8)  # Use region-specific multiplier
    
    # Adjust based on population size (larger countries tend to have lower per capita GDP)
    if population > 100000000:  # Large countries
        multiplier *= 0.7
    elif population > 50000000:  # Medium countries
        multiplier *= 0.9
    elif population < 1000000:  # Small countries
        multiplier *= 1.3
    
    estimated_gdp_per_capita = base_gdp_per_capita * multiplier
    estimated_gdp = estimated_gdp_per_capita * population if population > 0 else 0
    
    # Estimate HDI based on GDP per capita
    if estimated_gdp_per_capita > 50000:
        estimated_hdi = 0.9 + (estimated_gdp_per_capita - 50000) / 1000000
    elif estimated_gdp_per_capita > 20000:
        estimated_hdi = 0.7 + (estimated_gdp_per_capita - 20000) / 100000
    elif estimated_gdp_per_capita > 5000:
        estimated_hdi = 0.5 + (estimated_gdp_per_capita - 5000) / 30000
    else:
        estimated_hdi = 0.3 + estimated_gdp_per_capita / 10000
    
    estimated_hdi = min(0.99, max(0.3, estimated_hdi))  # Clamp between 0.3 and 0.99
    
    # Estimate life expectancy based on HDI
    estimated_life_expectancy = 50 + (estimated_hdi * 35)
    
    # Estimate internet penetration based on HDI
    estimated_internet = min(95, max(5, estimated_hdi * 100))
    
    return {
        'gdp': estimated_gdp,
        'gdp_per_capita': estimated_gdp_per_capita,
        'hdi': round(estimated_hdi, 3),
        'life_expectancy': round(estimated_life_expectancy, 1),
        'internet_penetration': round(estimated_internet, 1)
    }

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
                # Sort countries alphabetically by name
                result.sort(key=lambda x: x.get('name', ''))
                APICache.set(cache_key, result)
                return jsonify(result)
            
            # If no data in database, fetch from API
            logger.info("Fetching countries from REST Countries API...")
            countries_data = RestCountriesService.get_all_countries()
            logger.info(f"Fetched {len(countries_data)} countries from API")
            result = []
            
            for i, country_data in enumerate(countries_data):  # Load all countries
                # Get economic data for this country
                country_name = country_data.get('name', {}).get('common', 'Unknown')
                population = country_data.get('population', 0)
                region = country_data.get('region', 'Unknown')
                additional_data = get_sample_economic_data(country_name, population, region)
                
                country_info = parse_country_data(country_data, additional_data)
                if country_info:
                    try:
                        country = get_or_create_country(country_info)
                        result.append(country.to_dict())
                        if i % 50 == 0:  # Log every 50 countries
                            logger.info(f"Processed {i+1} countries...")
                    except Exception as e:
                        logger.error(f"Error processing country {i+1} ({country_name}): {e}")
                else:
                    logger.warning(f"Failed to parse country {i+1} ({country_name})")
            
            # Sort countries alphabetically by name
            result.sort(key=lambda x: x.get('name', ''))
            
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
            
            # Get economic data for this country
            population = country_data[0].get('population', 0)
            region = country_data[0].get('region', 'Unknown')
            additional_data = get_sample_economic_data(country_name, population, region)
            
            country_info = parse_country_data(country_data[0], additional_data)
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
