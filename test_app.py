# -*- coding: utf-8 -*-
"""
이 스크립트는 app.py의 FastAPI 엔드포인트에 대한 단위 테스트를 포함합니다.
- FastAPI의 TestClient를 사용하여 실제 서버 구동 없이 API를 테스트합니다.
- SearchService의 search 메서드를 모의(Mock) 처리하여 외부 API 호출을 방지합니다.
"""

import unittest
import json
from unittest.mock import patch
from fastapi.testclient import TestClient
from app import app

class TestApp(unittest.TestCase):
    """FastAPI 애플리케이션에 대한 테스트 케이스 클래스"""

    def setUp(self):
        """
        각 테스트가 실행되기 전에 호출됩니다.
        TestClient 인스턴스를 생성합니다.
        """
        self.client = TestClient(app)

    @patch('app.search_service.search')
    def test_search_success(self, mock_search):
        """
        [성공 케이스] /search 엔드포인트가 정상적으로 호출되고,
        모의 처리된 검색 결과를 올바르게 반환하는지 테스트합니다.
        """
        # --- 모의 객체 설정 ---
        # search_service.search 메서드가 반환할 가짜 결과 데이터
        mock_result = [
            {"title": "테스트 결과", "url": "http://test.com", "content": "내용", "source": "Mock"}
        ]
        # search 메서드가 위 데이터를 JSON 문자열 형태로 반환하도록 설정
        mock_search.return_value = json.dumps(mock_result)

        # --- 테스트 실행 ---
        # TestClient를 사용하여 API에 GET 요청 보내기
        response = self.client.get("/search?query=테스트")

        # --- 검증 ---
        self.assertEqual(response.status_code, 200)  # HTTP 상태 코드가 200인지 확인
        self.assertEqual(response.json(), mock_result) # 응답 본문이 모의 결과와 일치하는지 확인

        # search 메서드가 올바른 인자와 함께 호출되었는지 확인
        mock_search.assert_called_once_with(
            query='테스트',
            use_naver_blog=True,
            use_naver_news=True,
            use_google_search=True
        )

    @patch('app.search_service.search')
    def test_search_with_params(self, mock_search):
        """
        [성공 케이스] 쿼리 파라미터를 사용하여 특정 검색을 비활성화했을 때,
        API가 이를 올바르게 처리하여 SearchService에 전달하는지 테스트합니다.
        """
        mock_search.return_value = "[]" # 빈 리스트 반환

        # 네이버 뉴스와 구글 검색을 비활성화하여 요청
        response = self.client.get("/search?query=테스트&use_naver_news=false&use_google_search=false")

        self.assertEqual(response.status_code, 200)
        
        # search 메서드가 쿼리 파라미터에 맞게 호출되었는지 확인
        mock_search.assert_called_once_with(
            query='테스트',
            use_naver_blog=True,
            use_naver_news=False, # False로 전달되었는지 확인
            use_google_search=False # False로 전달되었는지 확인
        )

    def test_search_no_query(self):
        """
        [실패 케이스] 필수 파라미터인 'query' 없이 요청했을 때,
        FastAPI가 422 Unprocessable Entity 에러를 반환하는지 테스트합니다.
        """
        response = self.client.get("/search")
        self.assertEqual(response.status_code, 422) # 유효성 검사 실패 시 422 상태 코드

    @patch('app.search_service.search')
    def test_search_internal_error(self, mock_search):
        """
        [예외 케이스] SearchService에서 예외가 발생했을 때,
        API가 500 Internal Server Error를 반환하는지 테스트합니다.
        """
        # search 메서드가 호출될 때 Exception을 발생시키도록 설정
        mock_search.side_effect = Exception("Internal Error")

        response = self.client.get("/search?query=테스트")

        self.assertEqual(response.status_code, 500) # 서버 내부 에러 시 500 상태 코드
        self.assertIn("error", response.json()) # 응답 본문에 'error' 키가 포함되어 있는지 확인
        self.assertEqual(response.json()["error"], "Internal Error")

if __name__ == '__main__':
    unittest.main()
