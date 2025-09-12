import pytest
import json
from unittest.mock import patch, MagicMock
from app import app, db, Country, Comparison, RestCountriesService, WorldBankService

@pytest.fixture
def client():
    """Create a test client for the Flask application."""
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    app.config['WTF_CSRF_ENABLED'] = False
    
    with app.test_client() as client:
        with app.app_context():
            db.create_all()
            yield client
            db.session.remove()
            db.drop_all()

@pytest.fixture
def sample_country_data():
    """Sample country data for testing."""
    return {
        'name': {'common': 'Test Country'},
        'capital': ['Test Capital'],
        'population': 1000000,
        'area': 1000.5,
        'region': 'Test Region',
        'subregion': 'Test Subregion',
        'currencies': {'USD': {'name': 'US Dollar', 'symbol': '$'}},
        'flags': {'png': 'https://example.com/flag.png'}
    }

@pytest.fixture
def sample_country():
    """Create a sample country in the database."""
    country = Country(
        name='Test Country',
        capital='Test Capital',
        population=1000000,
        area=1000.5,
        region='Test Region',
        subregion='Test Subregion',
        currency='USD',
        flag_url='https://example.com/flag.png',
        gdp=5000000000,
        gdp_per_capita=5000,
        hdi=0.8,
        life_expectancy=75.5,
        internet_penetration=80.0
    )
    db.session.add(country)
    db.session.commit()
    return country

class TestHealthEndpoint:
    """Test the health check endpoint."""
    
    def test_health_check(self, client):
        """Test health check endpoint returns 200."""
        response = client.get('/api/health')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['status'] == 'healthy'
        assert 'timestamp' in data

class TestRootEndpoint:
    """Test the root endpoint."""
    
    def test_root_endpoint(self, client):
        """Test root endpoint returns API information."""
        response = client.get('/')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['message'] == 'CountryCompare API'
        assert 'endpoints' in data

class TestCountriesEndpoint:
    """Test the countries endpoint."""
    
    @patch('app.RestCountriesService.get_all_countries')
    def test_get_countries_from_api(self, mock_get_countries, client, sample_country_data):
        """Test fetching countries from API when database is empty."""
        mock_get_countries.return_value = [sample_country_data]
        
        response = client.get('/api/countries')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert len(data) > 0
        assert data[0]['name'] == 'Test Country'
    
    def test_get_countries_from_database(self, client, sample_country):
        """Test fetching countries from database."""
        response = client.get('/api/countries')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert len(data) == 1
        assert data[0]['name'] == 'Test Country'
    
    @patch('app.RestCountriesService.get_all_countries')
    def test_get_countries_api_error(self, mock_get_countries, client):
        """Test handling API errors when fetching countries."""
        mock_get_countries.return_value = []
        
        response = client.get('/api/countries')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert len(data) == 0

class TestCountryEndpoint:
    """Test the individual country endpoint."""
    
    @patch('app.RestCountriesService.get_country_details')
    def test_get_country_from_api(self, mock_get_country, client, sample_country_data):
        """Test fetching individual country from API."""
        mock_get_country.return_value = [sample_country_data]
        
        response = client.get('/api/countries/Test%20Country')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['name'] == 'Test Country'
    
    def test_get_country_from_database(self, client, sample_country):
        """Test fetching individual country from database."""
        response = client.get('/api/countries/Test%20Country')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['name'] == 'Test Country'
    
    @patch('app.RestCountriesService.get_country_details')
    def test_get_country_not_found(self, mock_get_country, client):
        """Test handling country not found."""
        mock_get_country.return_value = None
        
        response = client.get('/api/countries/NonExistentCountry')
        assert response.status_code == 404
        data = json.loads(response.data)
        assert 'error' in data

class TestCompareEndpoint:
    """Test the compare endpoint."""
    
    def test_compare_missing_parameters(self, client):
        """Test compare endpoint with missing parameters."""
        response = client.get('/api/compare')
        assert response.status_code == 400
        data = json.loads(response.data)
        assert 'error' in data
    
    def test_compare_invalid_parameters(self, client):
        """Test compare endpoint with invalid parameters."""
        response = client.get('/api/compare?c1=Country1')
        assert response.status_code == 400
        data = json.loads(response.data)
        assert 'error' in data
    
    def test_compare_countries_from_database(self, client, sample_country):
        """Test comparing countries from database."""
        # Create second country
        country2 = Country(
            name='Test Country 2',
            capital='Test Capital 2',
            population=2000000,
            area=2000.0,
            region='Test Region 2',
            subregion='Test Subregion 2',
            currency='EUR',
            flag_url='https://example.com/flag2.png',
            gdp=10000000000,
            gdp_per_capita=5000,
            hdi=0.9,
            life_expectancy=80.0,
            internet_penetration=90.0
        )
        db.session.add(country2)
        db.session.commit()
        
        response = client.get('/api/compare?c1=Test%20Country&c2=Test%20Country%202')
        assert response.status_code == 200
        data = json.loads(response.data)
        
        assert 'country1' in data
        assert 'country2' in data
        assert 'comparison_metrics' in data
        assert data['country1']['name'] == 'Test Country'
        assert data['country2']['name'] == 'Test Country 2'
    
    @patch('app.RestCountriesService.get_country_details')
    def test_compare_countries_with_api_fallback(self, mock_get_country, client, sample_country_data):
        """Test comparing countries with API fallback."""
        mock_get_country.return_value = [sample_country_data]
        
        # Create one country in database
        sample_country = Country(
            name='Test Country',
            capital='Test Capital',
            population=1000000,
            area=1000.5,
            region='Test Region',
            subregion='Test Subregion',
            currency='USD',
            flag_url='https://example.com/flag.png'
        )
        db.session.add(sample_country)
        db.session.commit()
        
        response = client.get('/api/compare?c1=Test%20Country&c2=New%20Country')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert 'country1' in data
        assert 'country2' in data

class TestDataModels:
    """Test database models."""
    
    def test_country_model(self, client):
        """Test Country model creation and serialization."""
        country = Country(
            name='Test Country',
            capital='Test Capital',
            population=1000000,
            area=1000.5,
            region='Test Region',
            subregion='Test Subregion',
            currency='USD',
            flag_url='https://example.com/flag.png'
        )
        
        db.session.add(country)
        db.session.commit()
        
        # Test serialization
        country_dict = country.to_dict()
        assert country_dict['name'] == 'Test Country'
        assert country_dict['population'] == 1000000
        assert country_dict['area'] == 1000.5
    
    def test_comparison_model(self, client):
        """Test Comparison model creation and serialization."""
        comparison_data = {
            'country1': {'name': 'Country 1'},
            'country2': {'name': 'Country 2'},
            'metrics': {'population': {'country1': 1000, 'country2': 2000}}
        }
        
        comparison = Comparison(
            country1_name='Country 1',
            country2_name='Country 2',
            comparison_data=json.dumps(comparison_data)
        )
        
        db.session.add(comparison)
        db.session.commit()
        
        # Test serialization
        comparison_dict = comparison.to_dict()
        assert comparison_dict['country1_name'] == 'Country 1'
        assert comparison_dict['country2_name'] == 'Country 2'
        assert 'comparison_data' in comparison_dict

class TestAPIServices:
    """Test API service classes."""
    
    @patch('requests.get')
    def test_rest_countries_service(self, mock_get):
        """Test REST Countries service."""
        mock_response = MagicMock()
        mock_response.json.return_value = [{'name': {'common': 'Test Country'}}]
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response
        
        result = RestCountriesService.get_all_countries()
        assert len(result) == 1
        assert result[0]['name']['common'] == 'Test Country'
    
    @patch('requests.get')
    def test_world_bank_service(self, mock_get):
        """Test World Bank service."""
        mock_response = MagicMock()
        mock_response.json.return_value = [{'data': [{'value': 1000000}]}]
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response
        
        result = WorldBankService.get_gdp_data('US', 2022)
        assert result is not None
        assert len(result) == 1

class TestCaching:
    """Test caching functionality."""
    
    def test_api_cache(self, client):
        """Test API cache functionality."""
        from app import APICache
        
        # Test cache set and get
        test_data = {'test': 'data'}
        APICache.set('test_key', test_data)
        
        cached_data = APICache.get('test_key')
        assert cached_data == test_data
        
        # Test cache miss
        cached_data = APICache.get('non_existent_key')
        assert cached_data is None
        
        # Test cache clear
        APICache.clear()
        cached_data = APICache.get('test_key')
        assert cached_data is None

class TestErrorHandling:
    """Test error handling."""
    
    def test_internal_server_error(self, client):
        """Test internal server error handling."""
        with patch('app.Country.query') as mock_query:
            mock_query.all.side_effect = Exception('Database error')
            
            response = client.get('/api/countries')
            assert response.status_code == 500
            data = json.loads(response.data)
            assert 'error' in data

if __name__ == '__main__':
    pytest.main([__file__])
