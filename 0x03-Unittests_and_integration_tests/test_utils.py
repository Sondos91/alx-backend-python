#!/usr/bin/env python3
"""
Unit tests for utils module functions:
access_nested_map, get_json, and memoize.
"""

import unittest
from unittest.mock import Mock, patch

from parameterized import parameterized

from utils import (
    access_nested_map,
    get_json,
    memoize,
)


class TestAccessNestedMap(unittest.TestCase):
    """
    Unit tests for the access_nested_map function from the utils module.
    This function retrieves a value from a nested dictionary
    using a tuple path.
    """

    @parameterized.expand([
        ({"a": 1}, ("a",), 1),
        ({"a": {"b": 2}}, ("a",), {"b": 2}),
        ({"a": {"b": 2}}, ("a", "b"), 2),
        ({"a": {"b": {"c": 42}}}, ("a", "b", "c"), 42),
        ({"x": {"y": {"z": "found"}}}, ("x", "y", "z"), "found"),
        ({"a": 1}, (), {"a": 1}),
    ])
    def test_access_nested_map(self, nested_map, path, expected):
        """Test access_nested_map returns correct value for valid paths."""
        self.assertEqual(
            access_nested_map(nested_map, path),
            expected
        )

    @parameterized.expand([
        ({"a": 1}, ("b",), "b"),
        ({"a": {"b": 2}}, ("a", "c"), "c"),
        ({"a": {"b": 2}}, ("a", "b", "c"), "c"),
        ({"a": {"b": {"c": 42}}}, ("a", "x"), "x"),
        ({"a": 1}, ("a", "b"), "b"),
    ])
    def test_access_nested_map_missing_key(self, nested_map, path, missing_key):
        """Test access_nested_map raises KeyError for missing keys."""
        with self.assertRaises(KeyError) as cm:
            access_nested_map(nested_map, path)
        self.assertEqual(
            cm.exception.args[0],
            missing_key
        )

    @parameterized.expand([
        ({}, ("a",)),
        ({"a": 1}, ("a", "b")),
    ])
    def test_access_nested_map_exception(self, nested_map, path):
        """Test access_nested_map raises KeyError for invalid paths."""
        with self.assertRaises(KeyError):
            access_nested_map(nested_map, path)


class TestGetJson(unittest.TestCase):
    """
    Unit tests for the get_json function from the utils module.
    This function fetches and parses a JSON response from a given URL.
    """

    @parameterized.expand([
        ("http://example.com", {"payload": True}),
        ("http://holberton.io", {"payload": False}),
    ])
    def test_get_json(self, test_url, test_payload):
        """Test get_json returns correct payload from mocked response."""
        with patch('requests.get') as mock_get:
            mock_response = Mock()
            mock_response.json.return_value = test_payload
            mock_get.return_value = mock_response

            result = get_json(test_url)
            self.assertEqual(result, test_payload)
            mock_get.assert_called_once_with(test_url)


class TestMemoize(unittest.TestCase):
    """
    Unit tests for the memoize decorator from the utils module.
    It ensures that decorated methods are cached after the first call.
    """

    def test_memoize(self):
        """Test @memoize caches method results after first call."""
        class TestClass:
            def a_method(self):
                return 42

            @memoize
            def a_property(self):
                return self.a_method()

        test_instance = TestClass()

        with patch.object(
            test_instance,
            'a_method',
            return_value=42
        ) as mock_method:
            self.assertEqual(test_instance.a_property, 42)
            mock_method.assert_called_once()
            self.assertEqual(test_instance.a_property, 42)
            mock_method.assert_called_once()


if __name__ == '__main__':
    unittest.main()