"""
Simple test script to verify API endpoints
Run this after starting the server to test all endpoints
"""

import requests
import json
from typing import Dict, Any


BASE_URL = "http://localhost:8000"


def print_test(name: str, success: bool, details: str = ""):
    """Print test result"""
    symbol = "✓" if success else "✗"
    print(f"{symbol} {name}")
    if details:
        print(f"  {details}")


def test_health() -> bool:
    """Test health endpoint"""
    try:
        response = requests.get(f"{BASE_URL}/health", timeout=5)
        success = response.status_code == 200
        data = response.json()
        print_test(
            "Health Check",
            success,
            f"Status: {data.get('status', 'unknown')}"
        )
        return success
    except Exception as e:
        print_test("Health Check", False, str(e))
        return False


def test_root() -> bool:
    """Test root endpoint"""
    try:
        response = requests.get(f"{BASE_URL}/", timeout=5)
        success = response.status_code == 200
        data = response.json()
        print_test(
            "Root Endpoint",
            success,
            data.get('message', '')
        )
        return success
    except Exception as e:
        print_test("Root Endpoint", False, str(e))
        return False


def test_stats() -> bool:
    """Test stats endpoint"""
    try:
        response = requests.get(f"{BASE_URL}/api/stats", timeout=5)
        success = response.status_code == 200
        if success:
            data = response.json()
            print_test(
                "Stats Endpoint",
                success,
                f"Posts: {data.get('posts', 0)}, "
                f"Layouts: {data.get('layouts', 0)}, "
                f"Similarities: {data.get('similarities', 0)}"
            )
        else:
            print_test("Stats Endpoint", success, f"Status: {response.status_code}")
        return success
    except Exception as e:
        print_test("Stats Endpoint", False, str(e))
        return False


def test_get_posts() -> bool:
    """Test get all posts endpoint"""
    try:
        response = requests.get(f"{BASE_URL}/api/posts", timeout=10)
        success = response.status_code == 200
        if success:
            data = response.json()
            count = len(data) if isinstance(data, list) else 0
            print_test(
                "Get All Posts",
                success,
                f"Retrieved {count} posts"
            )
        else:
            print_test("Get All Posts", success, f"Status: {response.status_code}")
        return success
    except Exception as e:
        print_test("Get All Posts", False, str(e))
        return False


def test_graph_data() -> bool:
    """Test graph data endpoints"""
    all_success = True
    
    for view_mode in ['topic', 'tool', 'llm']:
        try:
            response = requests.get(
                f"{BASE_URL}/api/graph-data/{view_mode}",
                timeout=10
            )
            success = response.status_code == 200
            
            if success:
                data = response.json()
                nodes = len(data.get('nodes', []))
                edges = len(data.get('edges', []))
                print_test(
                    f"Graph Data ({view_mode})",
                    success,
                    f"Nodes: {nodes}, Edges: {edges}"
                )
            else:
                print_test(
                    f"Graph Data ({view_mode})",
                    success,
                    f"Status: {response.status_code}"
                )
                all_success = False
                
        except Exception as e:
            print_test(f"Graph Data ({view_mode})", False, str(e))
            all_success = False
    
    return all_success


def test_search() -> bool:
    """Test search endpoint"""
    try:
        # Test POST endpoint
        response = requests.post(
            f"{BASE_URL}/api/search",
            json={"query": "RNN", "view_mode": "topic", "limit": 10},
            timeout=10
        )
        success = response.status_code == 200
        
        if success:
            data = response.json()
            count = data.get('count', 0)
            print_test(
                "Search Endpoint (POST)",
                success,
                f"Found {count} results for 'RNN'"
            )
        else:
            print_test(
                "Search Endpoint (POST)",
                success,
                f"Status: {response.status_code}"
            )
        
        # Test GET endpoint
        response2 = requests.get(
            f"{BASE_URL}/api/search",
            params={"q": "learning", "view_mode": "content", "limit": 5},
            timeout=10
        )
        success2 = response2.status_code == 200
        
        if success2:
            data2 = response2.json()
            count2 = data2.get('count', 0)
            print_test(
                "Search Endpoint (GET)",
                success2,
                f"Found {count2} results for 'learning'"
            )
        else:
            print_test(
                "Search Endpoint (GET)",
                success2,
                f"Status: {response2.status_code}"
            )
        
        return success and success2
        
    except Exception as e:
        print_test("Search Endpoint", False, str(e))
        return False


def test_get_single_post() -> bool:
    """Test get single post endpoint"""
    try:
        # First, get list of posts to find a valid ID
        response = requests.get(f"{BASE_URL}/api/posts", timeout=10)
        if response.status_code != 200 or not response.json():
            print_test("Get Single Post", False, "No posts available to test")
            return False
        
        posts = response.json()
        test_post_id = posts[0]['id']
        
        # Now test getting single post
        response = requests.get(
            f"{BASE_URL}/api/posts/{test_post_id}",
            timeout=5
        )
        success = response.status_code == 200
        
        if success:
            data = response.json()
            print_test(
                "Get Single Post",
                success,
                f"Retrieved post: {data.get('title', 'Unknown')[:50]}..."
            )
        else:
            print_test(
                "Get Single Post",
                success,
                f"Status: {response.status_code}"
            )
        
        return success
        
    except Exception as e:
        print_test("Get Single Post", False, str(e))
        return False


def test_invalid_view_mode() -> bool:
    """Test that invalid view mode returns error"""
    try:
        response = requests.get(
            f"{BASE_URL}/api/graph-data/invalid",
            timeout=5
        )
        success = response.status_code == 400
        print_test(
            "Invalid View Mode Handling",
            success,
            "Correctly rejected invalid view mode" if success else "Failed to reject invalid view mode"
        )
        return success
    except Exception as e:
        print_test("Invalid View Mode Handling", False, str(e))
        return False


def test_interactive_docs() -> bool:
    """Test that interactive docs are accessible"""
    try:
        response = requests.get(f"{BASE_URL}/docs", timeout=5)
        success = response.status_code == 200
        print_test(
            "Interactive Docs (Swagger)",
            success,
            f"{BASE_URL}/docs is accessible" if success else "Docs not accessible"
        )
        return success
    except Exception as e:
        print_test("Interactive Docs (Swagger)", False, str(e))
        return False


def main():
    """Run all tests"""
    print("=" * 60)
    print("API Test Suite for EECS 182 Post Graph")
    print("=" * 60)
    print(f"Testing API at: {BASE_URL}")
    print()
    
    tests = [
        ("Basic Endpoints", [
            test_root,
            test_health,
            test_stats,
        ]),
        ("Data Endpoints", [
            test_get_posts,
            test_get_single_post,
            test_graph_data,
        ]),
        ("Search Functionality", [
            test_search,
        ]),
        ("Error Handling", [
            test_invalid_view_mode,
        ]),
        ("Documentation", [
            test_interactive_docs,
        ]),
    ]
    
    total_tests = 0
    passed_tests = 0
    
    for category, category_tests in tests:
        print(f"\n{category}")
        print("-" * 60)
        
        for test_func in category_tests:
            total_tests += 1
            if test_func():
                passed_tests += 1
    
    print("\n" + "=" * 60)
    print(f"Results: {passed_tests}/{total_tests} tests passed")
    
    if passed_tests == total_tests:
        print("All tests passed!")
    else:
        print(f"Warning: {total_tests - passed_tests} test(s) failed")
    
    print("=" * 60)
    
    return passed_tests == total_tests


if __name__ == "__main__":
    import sys
    
    try:
        success = main()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\nTest suite interrupted by user")
        sys.exit(1)
