# 파이썬으로 딥리서치 만들어보기


참고 자료 : https://github.com/dzhng/deep-research


OpenAI의 언어 모델을 활용하여 주제를 심층적으로 탐구하는 AI 기반 연구 도구입니다.

## 설치

```
pip install openai python-dotenv firecrawl-py
```

## 프로젝트 구조

```
python_deepresearch/
│
├── main.py                    # 메인 진입점
├── utils.py                   # 유틸리티 함수
│
├── step1_feedback/            # 1단계: 피드백 생성
│   └── feedback.py            # 후속 질문 생성
│
├── step2_research/            # 2단계: 심층 연구
│   └── research.py            # 심층 연구 수행
│
├── step3_reporting/           # 3단계: 최종 보고서
│   └── reporting.py           # 최종 보고서 생성
│
└── output/                    # 생성된 보고서 저장 디렉토리
```

## 사용법

1. `.env` 파일을 생성하고 OpenAI API 키를 추가하세요:
   ```
   OPENAI_API_KEY=your_api_key_here
   ```

2. 메인 스크립트 실행:
   ```
   python main.py
   ```

3. 프롬프트에 따라 연구 주제를 입력하고 후속 질문에 답변하세요.

4. 최종 보고서는 `output` 디렉토리에 저장됩니다.


rate limit 5이기 때문에 2/2밖에 안됨



a -> a1/a2
b -? b1/b2

