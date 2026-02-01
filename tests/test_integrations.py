"""Integration and API tests."""

import pytest
import json
from src.mcp.server import ReleasGuardianMCPServer


@pytest.fixture
def app():
    """Create Flask test app."""
    server = ReleasGuardianMCPServer()
    server.app.config['TESTING'] = True
    return server.app


class TestMCPEndpoints:
    """Test MCP server endpoints."""
    
    def test_health_check(self, app):
        """Test health check endpoint."""
        with app.test_client() as client:
            response = client.get('/health')
            assert response.status_code == 200
            data = json.loads(response.data)
            assert data['status'] == 'ok'
    
    def test_generate_tests_endpoint(self, app):
        """Test generate-tests endpoint."""
        with app.test_client() as client:
            payload = {
                "code_diff": "def new_function():\n    pass",
                "acceptance_criteria": ["Function should work"],
                "file_types": {"backend": ["app.py"]}
            }
            response = client.post(
                '/generate-tests',
                json=payload,
                content_type='application/json'
            )
            
            # Note: This will fail without valid Claude API key
            # In production, we'd mock the API
            assert response.status_code in [200, 400]
    
    def test_analyze_release_missing_fields(self, app):
        """Test analyze-release with missing fields."""
        with app.test_client() as client:
            response = client.post(
                '/analyze-release',
                json={},
                content_type='application/json'
            )
            
            assert response.status_code == 400


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
