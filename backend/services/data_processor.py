"""
Data processing utilities for country comparison.
"""

import json
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
import statistics

logger = logging.getLogger(__name__)


class CountryDataProcessor:
    """Process and analyze country data."""
    
    def __init__(self):
        self.cache = {}
        self.cache_ttl = timedelta(hours=1)
    
    def normalize_currency_data(self, countries_data: List[Dict]) -> List[Dict]:
        """Normalize currency data across countries."""
        processed_data = []
        
        for country in countries_data:
            try:
                # Extract currency information
                currencies = country.get('currencies', {})
                if currencies:
                    currency_code = list(currencies.keys())[0]
                    currency_info = currencies[currency_code]
                    
                    country['currency_code'] = currency_code
                    country['currency_name'] = currency_info.get('name', 'Unknown')
                    country['currency_symbol'] = currency_info.get('symbol', '$')
                else:
                    country['currency_code'] = 'USD'
                    country['currency_name'] = 'US Dollar'
                    country['currency_symbol'] = '$'
                
                processed_data.append(country)
                
            except Exception as e:
                logger.error(f"Error processing currency data for country {country.get('name', 'Unknown')}: {e}")
                processed_data.append(country)
        
        return processed_data
    
    def calculate_economic_metrics(self, country_data: Dict) -> Dict:
        """Calculate additional economic metrics."""
        try:
            population = country_data.get('population', 0)
            area = country_data.get('area', 0)
            gdp = country_data.get('gdp', 0)
            
            metrics = {}
            
            # GDP per capita
            if population > 0 and gdp:
                metrics['gdp_per_capita'] = gdp / population
            
            # Population density
            if area > 0 and population > 0:
                metrics['population_density'] = population / area
            
            # Economic indicators
            if gdp:
                metrics['economic_size_category'] = self._categorize_economic_size(gdp)
            
            return metrics
            
        except Exception as e:
            logger.error(f"Error calculating economic metrics: {e}")
            return {}
    
    def _categorize_economic_size(self, gdp: float) -> str:
        """Categorize economic size based on GDP."""
        if gdp >= 5000000000000:  # 5 trillion
            return "Very Large"
        elif gdp >= 1000000000000:  # 1 trillion
            return "Large"
        elif gdp >= 100000000000:  # 100 billion
            return "Medium"
        elif gdp >= 10000000000:  # 10 billion
            return "Small"
        else:
            return "Very Small"
    
    def generate_comparison_summary(self, country1_data: Dict, country2_data: Dict) -> Dict:
        """Generate a summary of comparison between two countries."""
        summary = {
            'comparison_date': datetime.utcnow().isoformat(),
            'metrics_comparison': {},
            'winner_analysis': {},
            'insights': []
        }
        
        # Compare key metrics
        metrics_to_compare = [
            'population', 'area', 'gdp', 'gdp_per_capita', 
            'hdi', 'life_expectancy', 'internet_penetration'
        ]
        
        for metric in metrics_to_compare:
            val1 = country1_data.get(metric, 0)
            val2 = country2_data.get(metric, 0)
            
            if val1 and val2:
                ratio = val1 / val2 if val2 != 0 else 0
                winner = country1_data['name'] if val1 > val2 else country2_data['name']
                
                summary['metrics_comparison'][metric] = {
                    'country1_value': val1,
                    'country2_value': val2,
                    'ratio': ratio,
                    'winner': winner,
                    'difference_percentage': abs((val1 - val2) / val2 * 100) if val2 != 0 else 0
                }
        
        # Generate insights
        summary['insights'] = self._generate_insights(summary['metrics_comparison'])
        
        return summary
    
    def _generate_insights(self, metrics_comparison: Dict) -> List[str]:
        """Generate insights based on comparison data."""
        insights = []
        
        try:
            # Population insight
            if 'population' in metrics_comparison:
                pop_ratio = metrics_comparison['population']['ratio']
                if pop_ratio > 10:
                    insights.append("Significant population size difference")
                elif pop_ratio < 0.1:
                    insights.append("Major population size difference")
            
            # Economic insight
            if 'gdp' in metrics_comparison:
                gdp_ratio = metrics_comparison['gdp']['ratio']
                if gdp_ratio > 5:
                    insights.append("Large economic gap between countries")
                elif abs(gdp_ratio - 1) < 0.2:
                    insights.append("Similar economic sizes")
            
            # Development insight
            if 'hdi' in metrics_comparison:
                hdi_diff = metrics_comparison['hdi']['difference_percentage']
                if hdi_diff < 5:
                    insights.append("Similar development levels")
                elif hdi_diff > 20:
                    insights.append("Significant development gap")
            
            # Technology insight
            if 'internet_penetration' in metrics_comparison:
                tech_ratio = metrics_comparison['internet_penetration']['ratio']
                if tech_ratio > 2:
                    insights.append("Major digital divide")
                elif abs(tech_ratio - 1) < 0.3:
                    insights.append("Similar technology adoption")
        
        except Exception as e:
            logger.error(f"Error generating insights: {e}")
        
        return insights
    
    def aggregate_statistics(self, countries_data: List[Dict]) -> Dict:
        """Calculate aggregate statistics for a list of countries."""
        if not countries_data:
            return {}
        
        stats = {
            'total_countries': len(countries_data),
            'population_stats': {},
            'area_stats': {},
            'gdp_stats': {},
            'hdi_stats': {},
            'regional_distribution': {},
            'currency_distribution': {}
        }
        
        try:
            # Extract numeric data
            populations = [c.get('population', 0) for c in countries_data if c.get('population')]
            areas = [c.get('area', 0) for c in countries_data if c.get('area')]
            gdps = [c.get('gdp', 0) for c in countries_data if c.get('gdp')]
            hdis = [c.get('hdi', 0) for c in countries_data if c.get('hdi')]
            
            # Population statistics
            if populations:
                stats['population_stats'] = {
                    'total': sum(populations),
                    'average': statistics.mean(populations),
                    'median': statistics.median(populations),
                    'min': min(populations),
                    'max': max(populations)
                }
            
            # Area statistics
            if areas:
                stats['area_stats'] = {
                    'total': sum(areas),
                    'average': statistics.mean(areas),
                    'median': statistics.median(areas),
                    'min': min(areas),
                    'max': max(areas)
                }
            
            # GDP statistics
            if gdps:
                stats['gdp_stats'] = {
                    'total': sum(gdps),
                    'average': statistics.mean(gdps),
                    'median': statistics.median(gdps),
                    'min': min(gdps),
                    'max': max(gdps)
                }
            
            # HDI statistics
            if hdis:
                stats['hdi_stats'] = {
                    'average': statistics.mean(hdis),
                    'median': statistics.median(hdis),
                    'min': min(hdis),
                    'max': max(hdis)
                }
            
            # Regional distribution
            regions = {}
            for country in countries_data:
                region = country.get('region', 'Unknown')
                regions[region] = regions.get(region, 0) + 1
            stats['regional_distribution'] = regions
            
            # Currency distribution
            currencies = {}
            for country in countries_data:
                currency = country.get('currency_code', 'USD')
                currencies[currency] = currencies.get(currency, 0) + 1
            stats['currency_distribution'] = currencies
        
        except Exception as e:
            logger.error(f"Error calculating aggregate statistics: {e}")
        
        return stats
    
    def validate_country_data(self, country_data: Dict) -> Dict:
        """Validate and clean country data."""
        validation_result = {
            'is_valid': True,
            'errors': [],
            'warnings': [],
            'cleaned_data': country_data.copy()
        }
        
        try:
            # Required fields validation
            required_fields = ['name', 'capital', 'population', 'area', 'region']
            for field in required_fields:
                if not country_data.get(field):
                    validation_result['errors'].append(f"Missing required field: {field}")
                    validation_result['is_valid'] = False
            
            # Data type validation
            if country_data.get('population'):
                try:
                    pop = int(country_data['population'])
                    if pop <= 0:
                        validation_result['warnings'].append("Population should be positive")
                    validation_result['cleaned_data']['population'] = pop
                except (ValueError, TypeError):
                    validation_result['errors'].append("Invalid population data")
                    validation_result['is_valid'] = False
            
            if country_data.get('area'):
                try:
                    area = float(country_data['area'])
                    if area <= 0:
                        validation_result['warnings'].append("Area should be positive")
                    validation_result['cleaned_data']['area'] = area
                except (ValueError, TypeError):
                    validation_result['errors'].append("Invalid area data")
                    validation_result['is_valid'] = False
            
            # Range validation
            if country_data.get('hdi'):
                try:
                    hdi = float(country_data['hdi'])
                    if not (0 <= hdi <= 1):
                        validation_result['warnings'].append("HDI should be between 0 and 1")
                    validation_result['cleaned_data']['hdi'] = hdi
                except (ValueError, TypeError):
                    validation_result['errors'].append("Invalid HDI data")
                    validation_result['is_valid'] = False
            
            # Internet penetration validation
            if country_data.get('internet_penetration'):
                try:
                    penetration = float(country_data['internet_penetration'])
                    if not (0 <= penetration <= 100):
                        validation_result['warnings'].append("Internet penetration should be between 0 and 100%")
                    validation_result['cleaned_data']['internet_penetration'] = penetration
                except (ValueError, TypeError):
                    validation_result['errors'].append("Invalid internet penetration data")
                    validation_result['is_valid'] = False
        
        except Exception as e:
            logger.error(f"Error validating country data: {e}")
            validation_result['errors'].append(f"Validation error: {str(e)}")
            validation_result['is_valid'] = False
        
        return validation_result
    
    def export_data_to_json(self, data: Any, filename: str) -> bool:
        """Export data to JSON file."""
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False, default=str)
            return True
        except Exception as e:
            logger.error(f"Error exporting data to JSON: {e}")
            return False
    
    def import_data_from_json(self, filename: str) -> Optional[Any]:
        """Import data from JSON file."""
        try:
            with open(filename, 'r', encoding='utf-8') as f:
                data = json.load(f)
            return data
        except Exception as e:
            logger.error(f"Error importing data from JSON: {e}")
            return None
