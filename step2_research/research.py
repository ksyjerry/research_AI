import time
from typing import List, Dict, Optional
import os
from pydantic import BaseModel
from firecrawl import FirecrawlApp

from utils import JSON_llm, system_prompt



class SearchResult(BaseModel):
    url: str
    markdown: str
    description: str
    title: str


## 이거 자체가 1회
def firecrawl_search(query: str, timeout: int = 15000, limit: int = 5) ->List[SearchResult]:
    time.sleep(30)
    """
    Firecrawl 검색 API를 호출하여 결과를 반환하는 동기 함수.
    """
    try:
        app = FirecrawlApp(api_key=os.getenv("FIRECRAWL_API_KEY", ""))
        response = app.search(
            query=query,
            params={"timeout": timeout, "limit": limit, "scrapeOptions": {"formats": ["markdown"]}}
        )
        return response.get("data", [])
    except Exception as e:
        print(f"Firecrawl 검색 오류: {e}")

class SerpQuery(BaseModel):
    query: str
    research_goal: str

class SerpQueryResponse(BaseModel):
    queries: List[SerpQuery]


def generate_serp_queries(
    query: str,
    client,
    model: str,
    num_queries: int = 3,
    learnings: Optional[List[str]] = None,
) -> List[SerpQuery]:
    """
    사용자의 쿼리와 이전 연구 결과를 바탕으로 SERP 검색 쿼리를 생성합니다.
    JSON_llm을 사용하여 구조화된 JSON을 반환합니다.
    """
    prompt = (
        f"다음 사용자 입력을 기반으로 연구 주제를 조사하기 위한 SERP 검색 쿼리를 생성하세요. "
        f"JSON 객체를 반환하며, 'queries' 배열 필드에 {num_queries}개의 검색 쿼리를 포함해야 합니다 (쿼리가 명확할 경우 더 적을 수도 있음). "
        f"각 쿼리 객체에는 'query'와 'research_goal' 필드가 포함되어야 하며, 각 쿼리는 고유해야 합니다: "
        f"<입력>{query}</입력>"
    )
    if learnings:
        prompt += f"\n\n다음은 이전 연구에서 얻은 학습 내용입니다. 이를 활용하여 더 구체적인 쿼리를 생성하세요: {' '.join(learnings)}"
    
    sys_prompt = system_prompt()
    response_json = JSON_llm(prompt, SerpQueryResponse, client, system_prompt=sys_prompt, model=model)
    try:
        result = SerpQueryResponse.model_validate(response_json)
        queries = result.queries if result.queries else []
        print(f"리서치 주제에 대한 SERP 검색 쿼리 {len(queries)}개 생성됨")
        return queries[:num_queries]
    except Exception as e:
        print(f"오류: generate_serp_queries에서 JSON 응답을 처리하는 중 오류 발생: {e}")
        print(f"원시 응답: {response_json}")
        print(f"오류: 쿼리 '{query}'에 대한 JSON 응답 처리 실패")
        return []



class ResearchResult(BaseModel):
    learnings: List[str]
    visited_urls: List[str]
class SerpResultResponse(BaseModel):
    learnings: List[str]
    followUpQuestions: List[str]

def process_serp_result(
    query: str,
    search_result: List[SearchResult],
    client,
    model: str,
    num_learnings: int = 3,
    num_follow_up_questions: int = 3,
) -> Dict[str, List[str]]:
    """
    검색 결과를 처리하여 학습 내용과 후속 질문을 추출합니다.
    JSON_llm을 사용하여 구조화된 JSON 출력을 얻습니다.
    """
    contents = [
        item.get("markdown", "").strip()[:25000]
        for item in search_result["data"] if item.get("markdown")
    ]
    contents_str = "".join(f"<내용>\n{content}\n</내용>" for content in contents)
    prompt = (
        f"다음은 쿼리 <쿼리>{query}</쿼리>에 대한 SERP 검색 결과입니다. "
        f"이 내용을 바탕으로 학습 내용을 추출하고 후속 질문을 생성하세요. "
        f"JSON 객체로 반환하며, 'learnings' 및 'followUpQuestions' 키를 포함한 배열을 반환하세요. "
        f"각 학습 내용은 고유하고 간결하며 정보가 풍부해야 합니다. 최대 {num_learnings}개의 학습 내용과 "
        f"{num_follow_up_questions}개의 후속 질문을 포함해야 합니다.\n\n"
        f"<검색 결과>{contents_str}</검색 결과>"
    )
    sys_prompt = system_prompt()
    response_json = JSON_llm(prompt, SerpResultResponse, client, system_prompt=sys_prompt, model=model)
    try:
        result = SerpResultResponse.model_validate(response_json)
        return {
            "learnings": result.learnings,
            "followUpQuestions": result.followUpQuestions[:num_follow_up_questions],
        }
    except Exception as e:
        print(f"오류: process_serp_result에서 JSON 응답을 처리하는 중 오류 발생: {e}")
        print(f"원시 응답: {response_json}")
        return {"learnings": [], "followUpQuestions": []}

def deep_research(
    query: str,
    breadth: int,
    depth: int,
    client,
    model: str,
    learnings: Optional[List[str]] = None,
    visited_urls: Optional[List[str]] = None,
    attempt: int = 1  # Added to track attempt index
) -> ResearchResult:
    """
    주제를 재귀적으로 탐색하여 SERP 쿼리를 생성하고, 검색 결과를 처리하며,
    학습 내용과 방문한 URL을 수집합니다.
    """
    learnings = learnings or []
    visited_urls = visited_urls or []

    print(f"Deep Research {attempt}차 시도 \n 주제 \n {query})")

    serp_queries = generate_serp_queries(query=query, client=client, model=model, num_queries=breadth, learnings=learnings)
    
    for index, serp_query in enumerate(serp_queries, start=1):
        print(f"  - {attempt}.{index}번째 검색 쿼리: {serp_query.query}") 

        result = firecrawl_search(serp_query.query)
        new_urls = [item.get("url") for item in result["data"] if item.get("url")]
        serp_result = process_serp_result(
            query=serp_query.query,
            search_result=result,
            client=client,
            model=model,
            num_follow_up_questions=breadth
        )

        all_learnings = learnings + serp_result["learnings"]
        all_urls = visited_urls + new_urls
        new_depth = depth - 1
        new_breadth = max(1, breadth // 2)

        if new_depth > 0:
            next_query = (
                f"이전 연구목표: {serp_query.research_goal}\n"
                f"후속 연구방향: {' '.join(serp_result['followUpQuestions'])}"
            )

            # 증가된 시도 횟수로 재귀 호출
            sub_result = deep_research(
                query=next_query,
                breadth=new_breadth, 
                depth=new_depth,
                client=client,
                model=model,
                learnings=all_learnings,
                visited_urls=all_urls,
                attempt=attempt + 1  # 시도 횟수 증가
            )

            learnings = sub_result["learnings"]
            visited_urls = sub_result["visited_urls"]
        else:
            learnings = all_learnings
            visited_urls = all_urls

    return {"learnings": list(set(learnings)), "visited_urls": list(set(visited_urls))}

