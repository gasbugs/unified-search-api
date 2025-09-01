# -*- coding: utf-8 -*-
"""
이 스크립트는 app.py의 FastAPI 엔드포인트에 대한 단위 테스트를 포함합니다.
- FastAPI의 TestClient를 사용하여 실제 서버 구동 없이 API를 테스트합니다.
- SearchService의 search 메서드를 모의(Mock) 처리하여 외부 API 호출을 방지합니다.
- API 키 검증 로직을 테스트합니다.
"""

import unittest
import json
from unittest.mock import patch
from fastapi.testclient import TestClient
from app import app, API_KEY, API_KEY_NAME

class TestApp(unittest.TestCase):
    """FastAPI 애플리케이션에 대한 테스트 케이스 클래스"""

    def setUp(self):
        """
        각 테스트가 실행되기 전에 호출됩니다.
        TestClient 인스턴스를 생성하고, 유효한 API 키를 포함한 헤더를 설정합니다.
        """
        self.client = TestClient(app)
        self.valid_headers = {API_KEY_NAME: API_KEY}

    @patch('app.search_service.search')
    def test_search_success_with_valid_key(self, mock_search):
        """
        [성공 케이스] 유효한 API 키로 /search 엔드포인트를 호출했을 때,
        정상적으로 검색 결과를 반환하는지 테스트합니다.
        """
        # --- 모의 객체 설정 ---
        mock_result = [{"title": "테스트 결과", "url": "http://test.com", "content": "내용", "source": "Mock"}]
        mock_search.return_value = json.dumps(mock_result)

        # --- 테스트 실행 ---
        response = self.client.get("/search?query=테스트", headers=self.valid_headers)

        # --- 검증 ---
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), mock_result)
        mock_search.assert_called_once_with(
            query='테스트',
            use_naver_blog=True,
            use_naver_news=True,
            use_google_search=True
        )

    def test_search_with_invalid_key(self):
        """
        [실패 케이스] 유효하지 않은 API 키로 요청했을 때,
        403 Forbidden 에러를 반환하는지 테스트합니다.
        """
        invalid_headers = {API_KEY_NAME: "invalid_key"}
        response = self.client.get("/search?query=테스트", headers=invalid_headers)
        self.assertEqual(response.status_code, 403)
        self.assertEqual(response.json(), {"detail": "Invalid API Key"})

    def test_search_without_key(self):
        """
        [실패 케이스] API 키 헤더 없이 요청했을 때,
        422 Unprocessable Entity 에러를 반환하는지 테스트합니다.
        (FastAPI가 헤더 누락을 유효성 검사 실패로 처리)
        """
        response = self.client.get("/search?query=테스트")
        self.assertEqual(response.status_code, 422)

    @patch('app.search_service.search')
    def test_search_with_params_and_valid_key(self, mock_search):
        """
        [성공 케이스] 유효한 API 키와 함께 쿼리 파라미터를 사용했을 때,
        API가 이를 올바르게 처리하는지 테스트합니다.
        """
        mock_search.return_value = "[]"

        response = self.client.get(
            "/search?query=테스트&use_naver_news=false&use_google_search=false",
            headers=self.valid_headers
        )

        self.assertEqual(response.status_code, 200)
        mock_search.assert_called_once_with(
            query='테스트',
            use_naver_blog=True,
            use_naver_news=False,
            use_google_search=False
        )

    def test_search_no_query_with_valid_key(self):
        """
        [실패 케이스] 유효한 API 키를 사용했지만 필수 파라미터 'query'가 없을 때,
        422 Unprocessable Entity 에러를 반환하는지 테스트합니다.
        """
        response = self.client.get("/search", headers=self.valid_headers)
        self.assertEqual(response.status_code, 422)

    @patch('app.search_service.search')
    def test_search_internal_error_with_valid_key(self, mock_search):
        """
        [예외 케이스] 유효한 API 키를 사용했지만 서비스 내부에서 예외가 발생했을 때,
        API가 500 Internal Server Error를 반환하는지 테스트합니다.
        """
        mock_search.side_effect = Exception("Internal Error")

        response = self.client.get("/search?query=테스트", headers=self.valid_headers)

        self.assertEqual(response.status_code, 500)
        self.assertIn("error", response.json())
        self.assertEqual(response.json()["error"], "Internal Error")

if __name__ == '__main__':
    unittest.main()
