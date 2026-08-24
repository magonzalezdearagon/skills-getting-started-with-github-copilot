# Backend Tests - Mergington High School Activities API

This directory contains comprehensive unit and integration tests for the FastAPI application using pytest with the **AAA (Arrange-Act-Assert)** pattern.

## Running Tests

### Run all tests
```bash
pytest tests/
```

### Run tests with verbose output (shows test names and results)
```bash
pytest tests/ -v
```

### Run tests with coverage report
```bash
pytest tests/ --cov=src --cov-report=html
```

This generates a detailed coverage report in `htmlcov/index.html` showing which lines of code are tested.

### Run specific test class or method
```bash
pytest tests/app_test.py::TestSignupEndpoint -v
pytest tests/app_test.py::TestSignupEndpoint::test_signup_success -v
```

### Run tests and stop on first failure
```bash
pytest tests/ -x
```

## Test Organization

Tests are organized by API endpoint using class grouping:

### `TestRootEndpoint`
- Tests for `GET /` redirection to `/static/index.html`

### `TestGetActivities`
- Tests for `GET /activities` retrieving all activities
- Verifies response structure, participant lists, and various activity states

### `TestSignupEndpoint`
- Tests for `POST /activities/{activity_name}/signup`
- Happy path: successful registration
- Error cases: duplicate email, activity not found, capacity limits
- State verification: participant list updates

### `TestUnregisterEndpoint`
- Tests for `POST /activities/{activity_name}/unregister`
- Happy path: successful unregistration
- Error cases: activity not found, participant not registered
- State verification: participant removal

### `TestIntegrationFlow`
- End-to-end workflow tests
- Full signup workflow with GET → POST → GET verification
- Signup and unregister complete flow
- Multi-participant scenarios
- Selective unregistration with other participants remaining

## Understanding the AAA Pattern

Each test follows the **Arrange-Act-Assert** pattern:

```python
def test_signup_success(self, client_with_data, test_activities):
    # Arrange: Set up test data and fixtures
    email = "new_student@mergington.edu"
    activity = "Chess Club"
    
    # Act: Execute the API call
    response = client_with_data.post(f"/activities/{activity}/signup?email={email}")
    
    # Assert: Verify response and state changes
    assert response.status_code == 200
    assert response.json()["message"] == f"Signed up {email} for {activity}"
    assert email in test_activities[activity]["participants"]
```

**Benefits:**
- Clear test intent and flow
- Easy to identify where failures occur
- Simple to add new assertions
- Facilitates debugging

## Test Fixtures

### `client` (conftest.py)
Provides a `TestClient` instance for making HTTP requests to the FastAPI app without running a server.

```python
def test_example(client):
    response = client.get("/activities")
    assert response.status_code == 200
```

### `test_activities` (conftest.py)
Fresh, isolated in-memory activities dict for each test. Prevents cross-test pollution.

```python
def test_example(test_activities):
    assert "Chess Club" in test_activities
    assert len(test_activities["Chess Club"]["participants"]) == 2
```

### `client_with_data` (conftest.py)
TestClient with pre-populated test activities injected. Combines `client` and `test_activities`.

```python
def test_example(client_with_data, test_activities):
    response = client_with_data.get("/activities")
    # Response contains test_activities data
```

## Test Data

Tests use a consistent set of sample activities defined in `conftest.py`:

- **Chess Club**: 2/12 participants
- **Programming Class**: 2/20 participants
- **Gym Class**: 2/30 participants
- **Empty Activity**: 0/5 participants (for testing capacity)
- **Full Activity**: 2/2 participants (at max capacity)

## Adding New Tests

### Basic Structure
```python
class TestNewFeature:
    """Tests for new feature"""
    
    def test_happy_path(self, client_with_data, test_activities):
        # Arrange
        test_data = "value"
        
        # Act
        response = client_with_data.get("/endpoint")
        
        # Assert
        assert response.status_code == 200
    
    def test_error_case(self, client_with_data):
        # Arrange
        invalid_data = "invalid"
        
        # Act
        response = client_with_data.post("/endpoint", json=invalid_data)
        
        # Assert
        assert response.status_code == 400
```

### Best Practices
1. Use descriptive test names: `test_signup_duplicate_email_rejected`
2. Include one assertion focus per test when possible
3. Use AAA pattern consistently
4. Add docstrings explaining what is being tested
5. Use fixtures to avoid duplicating setup code
6. Test both happy paths and error cases

## Coverage Goals

Current coverage targets:
- **Endpoints**: >80% (all API endpoints tested)
- **Error handling**: All error codes tested
- **State changes**: All participant list mutations verified
- **Edge cases**: Empty lists, full capacity, duplicates

Check coverage:
```bash
pytest tests/ --cov=src --cov-report=term-missing
```

## Troubleshooting

### `ModuleNotFoundError: No module named 'src'`
Ensure you run pytest from the workspace root, and `pytest.ini` has `pythonpath = .`

### Fixture not found
Verify fixtures are defined in `conftest.py` and function signatures match exactly.

### Test isolation issues
Each test gets a fresh `test_activities` fixture. If tests are interfering, check that you're not modifying global state outside fixtures.

### Import errors from `src.app`
The `src/app.py` must exist and be importable. Check the path in `conftest.py`.

## Future Enhancements

- **Parameterized tests**: Use `pytest.mark.parametrize` for testing multiple email formats, special characters
- **Error message validation**: Extend assertions to check exact error message content
- **Performance tests**: Add tests for response time expectations
- **Mock external services**: If auth or external APIs are added, use `pytest-mock`
- **GitHub Actions CI**: Automate test runs on push/PR
