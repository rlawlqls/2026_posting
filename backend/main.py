from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import requests
from bs4 import BeautifulSoup
import google.generativeai as genai
from dotenv import load_dotenv
import os


# 환경변수 로드
load_dotenv()

# FastAPI 앱 생성
app = FastAPI(title="News Sentiment Analyzer")

# CORS 설정 (Vue에서 접근 가능하도록)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173","http://localhost:8000","http://localhost:3000","https://news-sentiment-analyzer-woad.vercel.app","https://*.vercel.app"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Gemini API 설정
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
model = genai.GenerativeModel('gemini-2.5-flash')

# 데이터 모델
class NewsArticle(BaseModel):
    title: str
    url: str
    content: str
    sentiment: str = ""
    sentiment_score: float = 0.0

class AnalysisRequest(BaseModel):
    url: str


def crawl_news(url: str) -> dict:
    """네이버 뉴스 크롤링"""
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.text, 'html.parser')
        
        
        title = soup.select_one('#title_area, .media_end_head_headline')
        content = soup.select_one('#dic_area, #newsct_article, .news_end_body_content')
        
        if not title or not content:
            
            title = soup.find('h1') or soup.find('title')
            content = soup.find('article') or soup.find('div', class_='content')
        
        title_text = title.get_text(strip=True) if title else "제목 없음"
        content_text = content.get_text(strip=True) if content else "내용 없음"
        
        # 내용이 너무 길면 잘라내기 (Gemini API 토큰 제한)
        if len(content_text) > 3000:
            content_text = content_text[:3000] + "..."
        
        return {
            "title": title_text,
            "content": content_text,
            "url": url
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"크롤링 실패: {str(e)}")

# 감정 분석 함수
def analyze_sentiment(text: str) -> dict:
    """Gemini API를 사용한 감정 분석"""
    try:
        prompt = f"""
        다음 뉴스 기사의 감정을 분석해주세요.
        
        기사 내용:
        {text}
        
        다음 형식으로 답변해주세요:
        감정: [긍정/부정/중립]
        점수: [0.0~1.0 사이의 숫자, 1.0에 가까울수록 강한 긍정]
        이유: [약간 구체적인 분석 이유]
        
        예시:
        감정: 긍정
        점수: 0.8
        이유: 경제 성장과 고용 증가에 대한 긍정적인 내용이 주를 이룸...등
        """
        
        response = model.generate_content(prompt)
        result_text = response.text
        
        # 결과 파싱
        lines = result_text.strip().split('\n')
        sentiment = "중립"
        score = 0.5
        reason = ""
        
        for line in lines:
            if '감정:' in line:
                sentiment = line.split(':')[1].strip()
            elif '점수:' in line:
                try:
                    score = float(line.split(':')[1].strip())
                except:
                    score = 0.5
            elif '이유:' in line:
                reason = line.split(':')[1].strip()
        
        return {
            "sentiment": sentiment,
            "score": score,
            "reason": reason
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"분석 실패: {str(e)}")

# API 엔드포인트
@app.get("/")
def read_root():
    return {"message": "News Sentiment Analyzer API"}

@app.post("/analyze")
async def analyze_news(request: AnalysisRequest):
    """뉴스 크롤링 및 감정 분석"""
    
    # 1. 뉴스 크롤링
    news_data = crawl_news(request.url)
    
    # 2. 감정 분석
    sentiment_result = analyze_sentiment(
        f"제목: {news_data['title']}\n내용: {news_data['content']}"
    )
    
    return {
        "title": news_data["title"],
        "url": news_data["url"],
        "content": news_data["content"][:500] + "...",  # 앞부분만 반환
        "sentiment": sentiment_result["sentiment"],
        "sentiment_score": sentiment_result["score"],
        "reason": sentiment_result["reason"]
    }

@app.get("/sample-urls")
def get_sample_urls():
    """테스트용 샘플 URL"""
    return {
        "urls": [
            "https://n.news.naver.com/mnews/article/008/0005111025",
            "https://n.news.naver.com/mnews/article/023/0003868164"
        ]
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)