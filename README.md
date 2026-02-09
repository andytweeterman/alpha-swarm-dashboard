# Alpha Swarm - Tiedeman Research Dashboard

A Streamlit-based financial analysis dashboard for portfolio governance and market analysis.

## Project Structure

```
Alpha Swarm Prod/
├── src/                          # Main application source code
│   ├── app.py                   # Main Streamlit application
│   ├── audit_sectors.py         # Sector auditing utilities
│   └── verify_context_dev.py    # Development utilities
├── data/                         # Data files and datasets
│   ├── update.csv               # Update data
│   └── raw_data/                # Raw data CSV files
│       ├── ^GSPC.csv
│       ├── audit_data_full.csv
│       ├── governance_history.csv
│       └── governance_history_v2.csv
├── tests/                        # Test suite
│   └── test_app.py
├── docs/                         # Documentation
│   ├── ALPHA SWARM PRODUCT ROADMAP (v2.0).txt
│   ├── USER_GUIDE.md
│   ├── Governance_Report.txt
│   └── ... (other documentation)
├── config/                       # Configuration files
├── logs/                         # Application logs
├── archive/                      # Archived research and old code
│   ├── research/                # Historical research scripts
│   └── verification/            # Old verification scripts
├── requirements.txt              # Python dependencies
├── README.md                     # This file
└── .streamlit/                  # Streamlit configuration
    └── config.toml
```

## Setup

### Prerequisites
- Python 3.8+
- pip or conda

### Installation

1. Clone or download the repository:
   ```bash
   cd "Alpha Swarm Prod"
   ```

2. Create a virtual environment (recommended):
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Running the Application

Start the Streamlit application:

```bash
streamlit run src/app.py
```

The dashboard will open in your default browser at `http://localhost:8501`

## Development

### File Organization

- **src/**: All production code
  - `app.py` - Main Streamlit UI and logic
  - `audit_sectors.py` - Sector analysis utilities
  - `verify_context_dev.py` - Development and testing utilities

- **tests/**: Test files
  - Run with: `pytest tests/`

- **data/**: Data storage
  - `raw_data/` - CSV datasets
  - `update.csv` - Update tracking data

- **docs/**: Documentation
  - User guides and technical specifications

- **archive/**: Historical code (not used in production)
  - `research/` - Experimental research scripts
  - `verification/` - Old verification tooling

## Configuration

Streamlit configuration is in `.streamlit/config.toml`. For secrets or sensitive data, create `.streamlit/secrets.toml` (added to .gitignore).

## Dependencies

See `requirements.txt` for all Python package requirements:
- streamlit
- pandas
- yfinance
- plotly
- openpyxl

## Production Deployment

For production deployment:

1. Ensure `.streamlit/secrets.toml` is properly configured with credentials
2. Update `logs/` directory permissions if using systemd or docker
3. Consider using a production WSGI server or Docker container
4. Configure appropriate logging levels in `.streamlit/config.toml`

## Documentation

Detailed documentation available in `docs/`:
- Product roadmap
- User guide
- Governance reports
- Governance status

## License

Tiedeman Research
