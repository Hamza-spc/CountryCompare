# 🌍 CountryCompare

A full-stack web application that allows users to compare countries across multiple indicators including economy, social metrics, and technology adoption. Built with Flask (Python) backend and React frontend, featuring interactive radar charts and bar charts for data visualization.

## ✨ Features

- **Country Comparison**: Compare any two countries across multiple indicators
- **Interactive Charts**:
  - Radar chart for multi-dimensional comparison
  - Bar chart for economic indicators
- **Comprehensive Data**:
  - General info (population, area, capital, region)
  - Economy (GDP, GDP per capita, inflation, currency)
  - Social indicators (HDI, life expectancy, literacy rate)
  - Technology (internet penetration, innovation index)
- **Real-time Data**: Fetches live data from REST Countries API and World Bank API
- **Responsive Design**: Modern dark theme with mobile-first approach
- **Caching**: In-memory caching to optimize API calls
- **Database**: PostgreSQL for data persistence
- **AWS Ready**: Pre-configured for AWS deployment

## 🏗️ Architecture

```
CountryCompare/
├── backend/                 # Flask API server
│   ├── app.py              # Main Flask application
│   ├── config.py           # Configuration settings
│   ├── requirements.txt    # Python dependencies
│   ├── Dockerfile         # Backend container
│   ├── tests/             # Unit tests
│   └── .ebextensions/     # AWS Elastic Beanstalk config
├── frontend/               # React application
│   ├── src/               # Source code
│   │   ├── components/    # React components
│   │   ├── pages/         # Page components
│   │   ├── services/      # API services
│   │   └── context/       # React context
│   ├── package.json       # Node dependencies
│   ├── Dockerfile        # Frontend container
│   └── nginx.conf        # Nginx configuration
├── docker-compose.yml     # Local development setup
├── aws-deploy.sh         # AWS deployment script
└── README.md             # This file
```

## 🚀 Quick Start

### Prerequisites

- Python 3.11+
- Node.js 18+
- PostgreSQL 15+
- Docker (optional)
- AWS CLI (for deployment)

### Local Development

1. **Clone the repository**

   ```bash
   git clone <repository-url>
   cd CountryCompare
   ```

2. **Set up the backend**

   ```bash
   cd backend
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

3. **Set up the database**

   ```bash
   # Install PostgreSQL and create database
   createdb countrycompare

   # Set environment variables
   export DATABASE_URL="postgresql://username:password@localhost/countrycompare"
   export SECRET_KEY="your-secret-key"
   ```

4. **Run the backend**

   ```bash
   python app.py
   ```

5. **Set up the frontend**

   ```bash
   cd frontend
   npm install
   ```

6. **Run the frontend**

   ```bash
   npm run dev
   ```

7. **Access the application**
   - Frontend: http://localhost:3000
   - Backend API: http://localhost:5000

### Using Docker

1. **Start all services**

   ```bash
   docker-compose up -d
   ```

2. **Access the application**
   - Frontend: http://localhost:3000
   - Backend API: http://localhost:5000
   - PostgreSQL: localhost:5432

## 🧪 Testing

### Backend Tests

```bash
cd backend
pip install pytest pytest-flask
pytest tests/ -v
```

### Frontend Tests

```bash
cd frontend
npm test
```

## 🌐 API Endpoints

### Countries

- `GET /api/countries` - Get all countries
- `GET /api/countries/<name>` - Get specific country details

### Comparison

- `GET /api/compare?c1=<country1>&c2=<country2>` - Compare two countries

### Health

- `GET /api/health` - Health check endpoint

### Example API Response

```json
{
  "country1": {
    "name": "United States",
    "capital": "Washington, D.C.",
    "population": 331002651,
    "area": 9833517.0,
    "region": "Americas",
    "gdp": 20953000000000,
    "gdp_per_capita": 63543.58
  },
  "country2": {
    "name": "China",
    "capital": "Beijing",
    "population": 1439323776,
    "area": 9706961.0,
    "region": "Asia",
    "gdp": 14722730697808,
    "gdp_per_capita": 10500.4
  },
  "comparison_metrics": {
    "population": {
      "country1": 331002651,
      "country2": 1439323776,
      "winner": "China"
    },
    "gdp": {
      "country1": 20953000000000,
      "country2": 14722730697808,
      "winner": "United States"
    }
  }
}
```

## ☁️ AWS Deployment

The application is pre-configured for AWS deployment using:

- **Elastic Beanstalk** for backend hosting
- **RDS PostgreSQL** for database
- **S3** for static assets
- **CloudFront** for CDN

### Automated Deployment

1. **Configure AWS CLI**

   ```bash
   aws configure
   ```

2. **Install EB CLI**

   ```bash
   pip install awsebcli
   ```

3. **Run deployment script**
   ```bash
   ./aws-deploy.sh
   ```

### Manual Deployment

#### Backend (Elastic Beanstalk)

1. **Initialize EB application**

   ```bash
   cd backend
   eb init countrycompare --region us-east-1
   ```

2. **Create environment**

   ```bash
   eb create countrycompare-prod --instance-type t3.medium
   ```

3. **Set environment variables**

   ```bash
   eb setenv DATABASE_URL="postgresql://user:pass@rds-endpoint:5432/dbname"
   eb setenv SECRET_KEY="your-secret-key"
   eb setenv FLASK_ENV="production"
   ```

4. **Deploy**
   ```bash
   eb deploy
   ```

#### Frontend (S3 + CloudFront)

1. **Build frontend**

   ```bash
   cd frontend
   npm run build
   ```

2. **Create S3 bucket**

   ```bash
   aws s3 mb s3://your-bucket-name
   ```

3. **Upload to S3**

   ```bash
   aws s3 sync dist/ s3://your-bucket-name
   ```

4. **Configure static website hosting**
   ```bash
   aws s3 website s3://your-bucket-name --index-document index.html
   ```

#### Database (RDS)

1. **Create RDS instance**

   ```bash
   aws rds create-db-instance \
     --db-instance-identifier countrycompare-db \
     --db-instance-class db.t3.micro \
     --engine postgres \
     --master-username postgres \
     --master-user-password yourpassword \
     --allocated-storage 20
   ```

2. **Update security groups** to allow connections from your EB environment

## 🔧 Configuration

### Environment Variables

#### Backend

- `DATABASE_URL` - PostgreSQL connection string
- `SECRET_KEY` - Flask secret key
- `FLASK_ENV` - Environment (development/production)
- `AWS_ACCESS_KEY_ID` - AWS access key
- `AWS_SECRET_ACCESS_KEY` - AWS secret key
- `S3_BUCKET_NAME` - S3 bucket for static assets
- `REDIS_URL` - Redis connection string (optional)

#### Frontend

- `VITE_API_URL` - Backend API URL

### Database Schema

#### Countries Table

```sql
CREATE TABLE countries (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) UNIQUE NOT NULL,
    capital VARCHAR(100) NOT NULL,
    population BIGINT NOT NULL,
    area FLOAT NOT NULL,
    region VARCHAR(100) NOT NULL,
    subregion VARCHAR(100) NOT NULL,
    currency VARCHAR(50) NOT NULL,
    flag_url VARCHAR(255) NOT NULL,
    gdp FLOAT,
    gdp_per_capita FLOAT,
    hdi FLOAT,
    life_expectancy FLOAT,
    internet_penetration FLOAT,
    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

#### Comparisons Table

```sql
CREATE TABLE comparisons (
    id SERIAL PRIMARY KEY,
    country1_name VARCHAR(100) NOT NULL,
    country2_name VARCHAR(100) NOT NULL,
    comparison_data TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

## 📊 Data Sources

- **REST Countries API**: Basic country information, flags, currencies
- **World Bank API**: Economic indicators, development metrics
- **HDI Database**: Human Development Index data
- **Internet Statistics**: Technology adoption metrics

## 🛠️ Development

### Adding New Metrics

1. **Update backend models** in `backend/app.py`
2. **Add API service methods** for new data sources
3. **Update frontend components** to display new metrics
4. **Add chart configurations** for new visualizations

### Customizing Charts

Charts are built using Chart.js and Recharts. To customize:

1. **Radar Chart**: Edit `frontend/src/components/charts/RadarChart.jsx`
2. **Bar Chart**: Edit `frontend/src/components/charts/BarChart.jsx`
3. **Styling**: Update Tailwind CSS classes

### API Extensions

To add new endpoints:

1. **Create new resource class** in `backend/app.py`
2. **Add route** using `api.add_resource()`
3. **Update frontend API service** in `frontend/src/services/api.js`

## 🚨 Troubleshooting

### Common Issues

1. **Database connection errors**

   - Check PostgreSQL is running
   - Verify connection string format
   - Ensure database exists

2. **API rate limiting**

   - Implement caching (already included)
   - Add request delays if needed
   - Use API keys if available

3. **Frontend build errors**

   - Clear node_modules and reinstall
   - Check Node.js version compatibility
   - Verify environment variables

4. **AWS deployment issues**
   - Check IAM permissions
   - Verify region settings
   - Review CloudWatch logs

### Performance Optimization

1. **Database indexing**

   ```sql
   CREATE INDEX idx_countries_name ON countries(name);
   CREATE INDEX idx_countries_region ON countries(region);
   ```

2. **API caching**

   - Redis for production
   - In-memory cache for development

3. **Frontend optimization**
   - Code splitting
   - Lazy loading
   - Image optimization

## 📝 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📞 Support

For support and questions:

- Create an issue on GitHub
- Check the troubleshooting section
- Review AWS documentation for deployment issues

## 🎯 Roadmap

- [ ] Add more data sources (UN, WHO, etc.)
- [ ] Implement user accounts and saved comparisons
- [ ] Add historical data and trends
- [ ] Create mobile app version
- [ ] Add more chart types (line charts, heatmaps)
- [ ] Implement real-time data updates
- [ ] Add country recommendations based on similarity

---

**Built with ❤️ using Flask, React, and AWS**
