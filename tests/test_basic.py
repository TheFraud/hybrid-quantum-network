import pytest

def test_basic():
    """Test minimal"""
    assert True

@pytest.mark.asyncio
async def test_async_basic():
    """Test async minimal"""
    assert True

