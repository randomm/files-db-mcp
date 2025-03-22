# Test Suite Template

This template provides a structured approach for creating comprehensive test suites across different testing levels.

## Unit Tests

### Python Unit Test Template (pytest)

```python
# test_[module_name].py

import pytest
from [module_path] import [Class/Function]

@pytest.fixture
def setup_[resource]():
    # Setup code
    [resource] = [setup code]
    yield [resource]
    # Teardown code if needed

def test_[function_name]_[scenario]([fixtures]):
    # Arrange
    [setup test data]
    
    # Act
    result = [function_call]
    
    # Assert
    assert result == [expected_result]

def test_[function_name]_[edge_case]([fixtures]):
    # Test edge case
    pass

def test_[function_name]_[error_condition]([fixtures]):
    # Test error condition
    with pytest.raises([ExpectedException]):
        [function_call_that_should_raise_exception]
```

### JavaScript Unit Test Template (Jest)

```javascript
// [module_name].test.js

import { [function/component] } from './[module]';

describe('[function/component]', () => {
  let [test_variables];
  
  beforeEach(() => {
    // Setup code
    [test_variables] = [setup code];
  });
  
  afterEach(() => {
    // Teardown code
    [cleanup code];
  });
  
  test('should [expected behavior] when [scenario]', () => {
    // Arrange
    const [input] = [test data];
    
    // Act
    const result = [function_call];
    
    // Assert
    expect(result).toBe([expected_result]);
  });
  
  test('should handle [edge case]', () => {
    // Test edge case
  });
  
  test('should throw error when [error condition]', () => {
    // Test error condition
    expect(() => {
      [function_call_that_should_throw]
    }).toThrow([ExpectedException]);
  });
});
```

## Integration Tests

### API Integration Test Template

```python
# test_api_integration.py

import pytest
import requests

BASE_URL = "http://[service_url]/api"

@pytest.fixture
def api_client():
    # Setup code - e.g., authentication, create test data
    # Return a configured client or session
    session = requests.Session()
    # Add authentication headers etc.
    yield session
    # Cleanup test data

def test_api_[endpoint]_[scenario](api_client):
    # Arrange
    endpoint = f"{BASE_URL}/[endpoint_path]"
    payload = {...}
    
    # Act
    response = api_client.post(endpoint, json=payload)
    
    # Assert
    assert response.status_code == [expected_status]
    assert response.json() == [expected_response]

def test_api_[endpoint]_error_handling(api_client):
    # Test API error handling
    pass

def test_api_[endpoint]_performance(api_client):
    # Test API performance if applicable
    pass
```

### Database Integration Test Template

```python
# test_db_integration.py

import pytest
from [app_path] import db

@pytest.fixture
def db_session():
    # Setup test database or transaction
    conn = db.create_connection()
    transaction = conn.begin()
    yield conn
    # Rollback transaction to clean up
    transaction.rollback()
    conn.close()

def test_db_[operation]_[scenario](db_session):
    # Arrange
    [setup test data]
    
    # Act
    result = [db_operation]
    
    # Assert
    assert result == [expected_result]
    # Verify database state if needed
```

## End-to-End Tests

### Web Application E2E Test Template (Playwright/Pytest)

```python
# test_e2e_[feature].py

import pytest
from playwright.sync_api import Page, expect

@pytest.fixture(scope="function")
def setup_[feature](page: Page):
    # Navigate to starting page
    page.goto("http://[app_url]/[start_path]")
    # Login or other setup if needed
    yield page

def test_[user_journey](setup_[feature]):
    page = setup_[feature]
    
    # Step 1
    page.click("[selector1]")
    expect(page.locator("[result_selector1]")).to_be_visible()
    
    # Step 2
    page.fill("[input_selector]", "[test_data]")
    page.click("[submit_selector]")
    
    # Step 3
    expect(page.locator("[result_selector2]")).to_contain_text("[expected_text]")
```

## Performance Tests

### Load Test Template (Locust)

```python
# locustfile.py

from locust import HttpUser, task, between

class [FeatureName]LoadTest(HttpUser):
    wait_time = between(1, 5)  # Wait between 1-5 seconds between tasks
    
    def on_start(self):
        # Setup - e.g., login
        pass
    
    @task(10)  # Weight of 10
    def [common_operation](self):
        self.client.get("/[endpoint]")
    
    @task(3)  # Weight of 3
    def [less_common_operation](self):
        self.client.post("/[endpoint]", json={
            "[field]": "[value]"
        })
```

## Security Tests

### Security Test Checklist

- Input validation tests
  - SQL injection
  - XSS vulnerabilities
  - Command injection
- Authentication tests
  - Brute force protection
  - Password policy enforcement
  - Session management
- Authorization tests
  - Role-based access control
  - Resource access restrictions
- Data protection tests
  - Sensitive data encryption
  - Secure communication (HTTPS)

## Test Data Generation

### Python Factory Pattern Template

```python
# factories.py

import factory
import faker
from [app_path].models import [Model]

faker = faker.Faker()

class [Model]Factory(factory.Factory):
    class Meta:
        model = [Model]
    
    id = factory.Sequence(lambda n: n)
    name = factory.LazyFunction(lambda: faker.name())
    email = factory.LazyFunction(lambda: faker.email())
    # Add other fields
    
    @factory.post_generation
    def [related_objects](self, create, extracted, **kwargs):
        if not create:
            return
        
        if extracted:
            # Add related objects
            pass
```

## Test Run Configuration

### Pytest Configuration

```ini
# pytest.ini

[pytest]
addopts = --verbose
          --cov=[package_name]
          --cov-report=term
          --cov-report=html
testpaths = tests
python_files = test_*.py
python_classes = Test*
python_functions = test_*
```

## Continuous Integration Configuration

### GitHub Actions Test Workflow

```yaml
# .github/workflows/tests.yml

name: Tests

on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main, develop ]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Set up Python
        uses: actions/setup-python@v2
        with:
          python-version: '3.9'
      - name: Install dependencies
        run: |
          python -m pip install --upgrade pip
          pip install pytest pytest-cov
          if [ -f requirements.txt ]; then pip install -r requirements.txt; fi
      - name: Test with pytest
        run: |
          pytest --cov=./ --cov-report=xml
      - name: Upload coverage to Codecov
        uses: codecov/codecov-action@v2
```

## Test Documentation

### Test Plan Template

```markdown
# Test Plan: [Feature Name]

## Overview
[Brief description of the feature and its testing scope]

## Test Levels

### Unit Tests
- [List of unit test categories]

### Integration Tests
- [List of integration test categories]

### End-to-End Tests
- [List of E2E test scenarios]

## Test Environment
- [Required environment setup]
- [Dependencies]
- [Configuration]

## Test Data
- [Test data sources]
- [Data generation approach]

## Test Schedule
- [Timeline for test execution]

## Responsibilities
- [Team members and their responsibilities]

## Risks and Mitigations
- [Potential risks]
- [Mitigation strategies]
```