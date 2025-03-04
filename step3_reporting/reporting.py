from typing import List
from utils import llm_call, system_prompt

def write_final_report(
    prompt: str,
    learnings: List[str],
    visited_urls: List[str],
    client,
    model: str,
) -> str:
    """
    수집된 정보를 바탕으로 최종 보고서를 작성합니다.
    """
    prompt = f"""
    다음은 연구 주제와 수집된 정보입니다. 이 정보를 바탕으로 구조화된 보고서를 작성해주세요.

    <연구 주제>
    {prompt}
    </연구 주제>

    <수집된 정보>
    {chr(10).join(learnings)}
    </수집된 정보>

    <참조 URL>
    {chr(10).join(visited_urls)}
    </참조 URL>

    보고서 작성 시 다음 지침을 따라주세요:

    1. 보고서는 마크다운 형식으로 작성해주세요.
    
    2. 표 작성 시 다음 규칙을 반드시 준수해주세요:
       - 각 열의 제목은 명확하고 간단하게 작성
       - 모든 열은 왼쪽 정렬로 통일
       - 구분선은 하이픈(-)만 사용하여 작성
       - 표 예시:
       | 구분 | 내용 | 비고 |
       |------|------|------|
       | 항목1 | 설명1 | 참고1 |
       | 항목2 | 설명2 | 참고2 |

    3. 다음과 같은 정보는 반드시 표로 작성해주세요:
       - 단계별 정보나 프로세스
       - 비교 데이터
       - 시간순 정보
       - 분류 정보
       - 기준이나 조건
       - 수치 데이터

    4. 보고서 구조:
       - 제목 (# 사용)
       - 개요 (## 사용)
       - 주요 내용 (### 사용, 표 형식 활용)
       - 세부 분석 (### 사용)
       - 결론 (## 사용)
       - 참고 자료 (## 사용)

    5. 표 작성 시 주의사항:
       - 표의 각 열 너비는 내용에 맞게 설정
       - 내용이 긴 경우 적절히 줄바꿈하여 작성
       - 각 셀의 내용은 명확하고 간단하게 작성
       - 복잡한 표는 여러 개의 작은 표로 분리
    """

    response = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": "당신은 전문적인 연구 보고서 작성자입니다. 데이터를 명확하고 구조화된 방식으로 표현하는 것이 중요합니다. 특히 표 형식을 사용할 때는 마크다운 문법을 정확히 준수하여 표가 깨지지 않도록 작성해야 합니다."},
            {"role": "user", "content": prompt}
        ]
    )

    return response.choices[0].message.content