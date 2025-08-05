# target-mock

A Singer.io target for mock data processing with state management, built with the Hotglue target SDK. This target supports both OAuth and API key authentication methods and provides comprehensive state tracking for customer records.

## Features

- **Customer Record Processing**: Create and update customer records with state management
- **Multiple Authentication Methods**: Supports both OAuth and API key authentication
- **State Management**: Comprehensive state tracking with bookmarks and summary statistics
- **Batch Processing**: Efficient batch processing with configurable batch sizes
- **Error Handling**: Robust error handling with detailed state reporting
- **Mock API Integration**: Simulates API interactions for testing purposes

## Installation

### From Source

```bash
# Clone the repository
git clone <repository-url>
cd target-mock

# Create and activate virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install in development mode
pip install -e .
```

### From PyPI (when published)

```bash
pip install target-mock
```

## Configuration

Create a `config.json` file with the appropriate authentication configuration:

### OAuth Configuration

```json
{
  "auth_type": "oauth",
  "client_id": "your_client_id",
  "client_secret": "your_client_secret",
  "refresh_token": "your_refresh_token",
  "rotate_refresh_token": false,
  "next_refresh_token": "your_next_refresh_token",
  "access_token": "your_access_token"
}
```

### API Key Configuration

```json
{
  "auth_type": "api_key",
  "api_key": "your_api_key"
}
```

### Configuration Attributes

- **`auth_type`**: Either `"oauth"` or `"api_key"` (required)
- **`client_id`**: OAuth client ID (required for OAuth)
- **`client_secret`**: OAuth client secret (required for OAuth)
- **`refresh_token`**: OAuth refresh token (required for OAuth)
- **`rotate_refresh_token`**: Enable refresh token rotation (optional, default: false)
- **`next_refresh_token`**: Next refresh token for rotation (required when `rotate_refresh_token` is true)
- **`access_token`**: OAuth access token (optional for OAuth)
- **`api_key`**: API key value (required for API key auth)

## Usage

### Process Customer Records

```bash
# Process customer records from a tap
tap-mock --config tap_config.json | target-mock --config config.json

# Process with state file
tap-mock --config tap_config.json | target-mock --config config.json --state state.json

# Process specific streams
tap-mock --config tap_config.json --catalog catalog.json | target-mock --config config.json
```

### Input Format

The target expects Singer protocol messages. For customer records, the expected format is:

```json
{
  "type": "RECORD",
  "stream": "customers",
  "record": {
    "externalId": "CUST-001",
    "name": "John Doe",
    "email": "john@example.com",
    "phone": "+1234567890"
  }
}
```

### State Output Format

The target generates state files with the following structure:

#### Create Operation
```json
{
  "bookmarks": {
    "Customers": [
      {
        "success": true,
        "id": "15142",
        "externalId": "TEST-EXT-CUST-1111"
      }
    ]
  },
  "summary": {
    "Customers": {
      "success": 1,
      "fail": 0,
      "existing": 0,
      "updated": 0
    }
  }
}
```

#### Update Operation
```json
{
  "bookmarks": {
    "Customers": [
      {
        "success": true,
        "id": "15142",
        "externalId": "TEST-EXT-CUST-1111"
      }
    ]
  },
  "summary": {
    "Customers": {
      "success": 0,
      "fail": 0,
      "existing": 0,
      "updated": 1
    }
  }
}
```

## State Management

The target maintains comprehensive state information:

### Bookmarks
- **success**: Boolean indicating if the operation was successful
- **id**: Generated or existing record ID
- **externalId**: External identifier for the record
- **hash**: Hash of the record for deduplication
- **created_at/updated_at**: Timestamp of the operation

### Summary Statistics
- **success**: Number of successfully created records
- **fail**: Number of failed operations
- **existing**: Number of existing records (deduplicated)
- **updated**: Number of updated records

## Development

### Project Structure

```
target-mock/
├── target_mock/
│   ├── __init__.py
│   ├── target.py          # Main target class
│   └── sinks.py           # Sink implementations
├── config.json            # Configuration file
├── setup.py               # Package setup
└── README.md              # This file
```

### Adding New Sinks

To add support for new record types, create a new sink class in `sinks.py`:

```python
class NewRecordSink(MockSink):
    name = "NewRecords"
    
    def process_record(self, record: dict, context: dict) -> None:
        # Custom processing logic
        pass
```

Then add it to the `SINK_TYPES` list in `target.py`.

### Testing

```bash
# Install development dependencies
pip install -e ".[dev]"

# Run tests
pytest

# Run linting
flake8 target_mock/
black target_mock/
isort target_mock/
```

## License

Apache 2.0

## Support

For support and questions, please contact the development team or create an issue in the repository. 