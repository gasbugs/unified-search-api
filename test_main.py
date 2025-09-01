# -*- coding: utf-8 -*-
"""
이 스크립트는 main.py의 unified_search 함수에 대한 단위 테스트를 포함합니다.
- 외부 API 호출을 모의(Mock) 객체로 대체하여 네트워크 연결 없이 테스트를 수행합니다.
- 각 검색 엔진의 활성화/비활성화 시나리오를 검증합니다.
- API 에러 발생 시의 동작을 테스트합니다.
"""

import unittest
import json
from unittest.mock import patch, MagicMock
from main import unified_search
import requests

class TestUnifiedSearch(unittest.TestCase):
    """unified_search 함수에 대한 테스트 케이스 클래스"""

    # --- 모의(Mock) 데이터 설정 ---
    # 테스트 시 실제 API 대신 사용할 가짜 응답 데이터입니다.

    # 네이버 블로그 API 모의 응답
    mock_naver_blog_response = {
        "items": [
            {
                "title": "테스트 네이버 블로그 제목",
                "link": "https://blog.naver.com/test",
                "description": "테스트 네이버 블로그 설명입니다."
            }
        ]
    }

    # 네이버 뉴스 API 모의 응답
    mock_naver_news_response = {
        "items": [
            {
                "title": "테스트 네이버 뉴스 제목",
                "originallink": "https://news.naver.com/test",
                "description": "테스트 네이버 뉴스 설명입니다."
            }
        ]
    }

    # 구글 검색 API 모의 응답
    mock_google_search_response = {
        "items": [
            {
                "title": "테스트 구글 검색 제목",
                "link": "https://google.com/test",
                "snippet": "테스트 구글 검색 스니펫입니다."
            }
        ]
    }

    @patch('main.build')
    @patch('main.requests.get')
    def test_all_searches_enabled(self, mock_requests_get, mock_build):
        """
        [성공 케이스] 모든 검색 엔진이 활성화된 경우,
        결과가 단일 리스트로 통합되고 각 항목에 정확한 출처가 포함되는지 테스트합니다.
        """
        # --- 모의 객체 설정 ---
        # requests.get 함수가 호출될 때 반환할 모의 응답을 설정합니다.
        mock_response_blog = MagicMock()
        mock_response_blog.json.return_value = self.mock_naver_blog_response
        mock_response_blog.raise_for_status.return_value = None
        
        mock_response_news = MagicMock()
        mock_response_news.json.return_value = self.mock_naver_news_response
        mock_response_news.raise_for_status.return_value = None

        # 호출 순서에 따라 다른 모의 응답을 반환하도록 설정 (블로그 -> 뉴스)
        mock_requests_get.side_effect = [mock_response_blog, mock_response_news]

        # googleapiclient.discovery.build 함수에 대한 모의 객체를 설정합니다.
        mock_service = MagicMock()
        mock_cse = MagicMock()
        mock_list = MagicMock()
        mock_list.execute.return_value = self.mock_google_search_response
        mock_cse.list.return_value = mock_list
        mock_service.cse.return_value = mock_cse
        mock_build.return_value = mock_service

        # --- 테스트 실행 ---
        result_json = unified_search("테스트 쿼리")
        results = json.loads(result_json)

        # --- 검증 ---
        self.assertIsInstance(results, list)  # 결과가 리스트 형태인지 확인
        self.assertEqual(len(results), 3)     # 3개의 검색 엔진 결과가 모두 포함되었는지 확인

        # 각 결과의 출처(source) 필드가 정확한지 확인
        self.assertEqual(results[0]['source'], 'Naver Blog')
        self.assertEqual(results[1]['source'], 'Naver News')
        self.assertEqual(results[2]['source'], 'Google Search')

        # 각 결과의 내용이 정확한지 확인
        self.assertEqual(results[0]['title'], '테스트 네이버 블로그 제목')
        self.assertEqual(results[1]['title'], '테스트 네이버 뉴스 제목')
        self.assertEqual(results[2]['title'], '테스트 구글 검색 제목')


    @patch('main.requests.get')
    def test_only_naver_blog(self, mock_requests_get):
        """
        [성공 케이스] 네이버 블로그 검색만 활성화된 경우,
        결과 리스트에 네이버 블로그 결과만 포함되는지 테스트합니다.
        """
        mock_response = MagicMock()
        mock_response.json.return_value = self.mock_naver_blog_response
        mock_response.raise_for_status.return_value = None
        mock_requests_get.return_value = mock_response

        result_json = unified_search("테스트 쿼리", use_naver_news=False, use_google_search=False)
        results = json.loads(result_json)

        self.assertIsInstance(results, list)
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]['source'], 'Naver Blog')

    @patch('main.print')
    @patch('main.requests.get')
    def test_naver_api_error(self, mock_requests_get, mock_print):
        """
        [예외 케이스] 네이버 API 요청 시 에러가 발생하는 경우,
        결과 리스트에 해당 내용이 포함되지 않고 에러 메시지가 출력되는지 테스트합니다.
        """
        # raise_for_status() 호출 시 예외를 발생시키도록 설정
        mock_requests_get.side_effect = requests.exceptions.RequestException("API Error")

        result_json = unified_search("테스트 쿼리", use_google_search=False)
        results = json.loads(result_json)

        self.assertIsInstance(results, list)
        self.assertEqual(len(results), 0)  # 에러가 발생했으므로 결과는 비어 있어야 함
        
        # print 함수가 예상된 에러 메시지와 함께 호출되었는지 확인
        mock_print.assert_any_call("Naver Blog search error: API Error")
        mock_print.assert_any_call("Naver News search error: API Error")


    @patch('main.print')
    @patch('main.build')
    def test_google_api_error(self, mock_build, mock_print):
        """
        [예외 케이스] 구글 API 요청 시 에러가 발생하는 경우,
        결과 리스트에 해당 내용이 포함되지 않고 에러 메시지가 출력되는지 테스트합니다.
        """
        # build() 함수 호출 시 예외를 발생시키도록 설정
        mock_build.side_effect = Exception("API Error")

        result_json = unified_search("테스트 쿼리", use_naver_blog=False, use_naver_news=False)
        results = json.loads(result_json)

        self.assertIsInstance(results, list)
        self.assertEqual(len(results), 0) # 에러가 발생했으므로 결과는 비어 있어야 함
        
        # print 함수가 예상된 에러 메시지와 함께 호출되었는지 확인
        mock_print.assert_called_with("Google Search error: API Error")

# 이 스크립트가 직접 실행될 때만 테스트를 실행
if __name__ == '__main__':
    unittest.main()
