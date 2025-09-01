# -*- coding: utf-8 -*-
"""
이 스크립트는 네이버와 구글의 검색 API를 사용하여 블로그, 뉴스, 웹 검색 결과를 통합하여 제공합니다.
- .env 파일에서 API 키를 로드합니다.
- 각 검색 결과를 단일 리스트로 취합하여 JSON 형식으로 반환합니다.
- 검색 엔진별로 검색을 활성화/비활성화할 수 있는 옵션을 제공합니다.
- 검색 관련 로직을 SearchService 클래스로 캡슐화했습니다.
"""

import os
import json
import requests
from dotenv import load_dotenv
from googleapiclient.discovery import build

# .env 파일에서 환경 변수 로드
load_dotenv()

# --- 상수 정의 ---
# API URL 및 출처 문자열을 상수로 관리하여 일관성 유지 및 오타 방지
NAVER_API_BASE_URL = "https://openapi.naver.com/v1/search"
NAVER_SOURCE_MAP = {
    "blog": {"url_suffix": "/blog.json", "source_name": "Naver Blog"},
    "news": {"url_suffix": "/news.json", "source_name": "Naver News"},
}
GOOGLE_SOURCE_NAME = "Google Search"


class SearchService:
    """
    다양한 검색 엔진의 API를 사용하여 통합 검색 서비스를 제공하는 클래스.
    """
    def __init__(self):
        """
        SearchService의 인스턴스를 초기화합니다.
        .env 파일에서 API 키를 로드하여 인스턴스 변수로 저장합니다.
        """
        self.naver_client_id = os.getenv("NAVER_CLIENT_ID")
        self.naver_client_secret = os.getenv("NAVER_CLIENT_SECRET")
        self.google_api_key = os.getenv("GOOGLE_API_KEY")
        self.google_cse_id = os.getenv("GOOGLE_CSE_ID")

    def _search_naver(self, query, search_type):
        """
        네이버 검색 API를 호출하는 내부 헬퍼 메서드.
        :param query: str, 검색어
        :param search_type: str, 'blog' 또는 'news'
        :return: list, 검색 결과 리스트
        """
        results = []
        search_info = NAVER_SOURCE_MAP.get(search_type)
        if not search_info:
            return results

        try:
            headers = {
                "X-Naver-Client-Id": self.naver_client_id,
                "X-Naver-Client-Secret": self.naver_client_secret,
            }
            params = {"query": query, "display": 10}
            response = requests.get(f"{NAVER_API_BASE_URL}{search_info['url_suffix']}", headers=headers, params=params)
            response.raise_for_status()
            search_results = response.json()

            for item in search_results.get("items", []):
                results.append({
                    "title": item.get("title"),
                    "url": item.get("originallink" if search_type == "news" else "link"),
                    "content": item.get("description"),
                    "source": search_info['source_name']
                })
        except requests.exceptions.RequestException as e:
            print(f"{search_info['source_name']} search error: {e}")
        
        return results

    def _search_google(self, query):
        """
        구글 검색 API를 호출하는 내부 헬퍼 메서드.
        :param query: str, 검색어
        :return: list, 검색 결과 리스트
        """
        results = []
        try:
            service = build("customsearch", "v1", developerKey=self.google_api_key)
            res = service.cse().list(q=query, cx=self.google_cse_id, num=10).execute()
            
            for item in res.get("items", []):
                results.append({
                    "title": item.get("title"),
                    "url": item.get("link"),
                    "content": item.get("snippet"),
                    "source": GOOGLE_SOURCE_NAME
                })
        except Exception as e:
            print(f"Google Search error: {e}")
            
        return results

    def search(self, query, use_naver_blog=True, use_naver_news=True, use_google_search=True):
        """
        네이버 블로그, 네이버 뉴스, 구글 검색을 통합하여 수행하고 결과를 단일 리스트로 반환합니다.

        :param query: str, 검색할 키워드
        :param use_naver_blog: bool, 네이버 블로그 검색 사용 여부 (기본값: True)
        :param use_naver_news: bool, 네이버 뉴스 검색 사용 여부 (기본값: True)
        :param use_google_search: bool, 구글 검색 사용 여부 (기본값: True)
        :return: str, 검색 결과를 담은 JSON 형식의 문자열
        """
        all_results = []

        if use_naver_blog:
            all_results.extend(self._search_naver(query, "blog"))

        if use_naver_news:
            all_results.extend(self._search_naver(query, "news"))

        if use_google_search:
            all_results.extend(self._search_google(query))

        return json.dumps(all_results, ensure_ascii=False, indent=4)


if __name__ == "__main__":
    # SearchService 인스턴스 생성
    search_service = SearchService()
    
    search_query = "인공지능"
    
    # 모든 검색 엔진을 사용하여 검색 실행 후 결과 출력
    print("--- 통합 검색 결과 ---")
    all_results = search_service.search(search_query)
    print(all_results)