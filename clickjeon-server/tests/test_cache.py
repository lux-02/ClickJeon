import json
import pytest
from unittest.mock import MagicMock, patch

from cache.kv_cache import cache_get, cache_set

def test_cache_get_returns_parsed_dict():
    mock_redis = MagicMock()
    mock_redis.get.return_value = json.dumps({"grade": "OFFICIAL"})

    with patch("cache.kv_cache._get_redis", return_value=mock_redis):
        result = cache_get("vt:kakao.com")

    assert result == {"grade": "OFFICIAL"}
    mock_redis.get.assert_called_once_with("vt:kakao.com")

def test_cache_get_returns_none_on_miss():
    mock_redis = MagicMock()
    mock_redis.get.return_value = None

    with patch("cache.kv_cache._get_redis", return_value=mock_redis):
        result = cache_get("vt:missing.com")

    assert result is None

def test_cache_get_returns_none_on_error():
    mock_redis = MagicMock()
    mock_redis.get.side_effect = Exception("Redis unavailable")

    with patch("cache.kv_cache._get_redis", return_value=mock_redis):
        result = cache_get("vt:any.com")

    assert result is None

def test_cache_set_stores_with_ttl():
    mock_redis = MagicMock()

    with patch("cache.kv_cache._get_redis", return_value=mock_redis):
        cache_set("vt:kakao.com", {"grade": "OFFICIAL"}, 3600)

    mock_redis.setex.assert_called_once_with(
        "vt:kakao.com", 3600, json.dumps({"grade": "OFFICIAL"})
    )

def test_cache_set_silently_fails_on_error():
    mock_redis = MagicMock()
    mock_redis.setex.side_effect = Exception("Redis unavailable")

    with patch("cache.kv_cache._get_redis", return_value=mock_redis):
        cache_set("vt:any.com", {}, 3600)  # should not raise
