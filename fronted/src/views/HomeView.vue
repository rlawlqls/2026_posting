<template>
  <div class="home">
    <div class="container">
      
      <header class="header">
        <h1>News Sentiment</h1>
        <p class="tagline">AI-powered news analysis</p>
      </header>

     
      <div class="input-card">
        <div class="input-wrapper">
          <input
            v-model="newsUrl"
            type="text"
            placeholder="Paste news article URL here..."
            class="url-input"
            @keyup.enter="analyzeNews"
          />
          <button 
            @click="analyzeNews" 
            :disabled="loading" 
            class="analyze-btn"
          >
            <span v-if="!loading">Analyze</span>
            <span v-else class="loading-dots">
              <span></span><span></span><span></span>
            </span>
          </button>
        </div>
        
        <button @click="loadSample" class="sample-link">
          Try sample article →
        </button>
      </div>

      
      <div v-if="loading" class="loading-card">
        <div class="pulse-loader"></div>
        <p>Analyzing sentiment...</p>
      </div>

      
      <div v-if="error" class="error-card">
        <svg width="20" height="20" viewBox="0 0 20 20" fill="none">
          <path d="M10 0C4.48 0 0 4.48 0 10s4.48 10 10 10 10-4.48 10-10S15.52 0 10 0zm1 15H9v-2h2v2zm0-4H9V5h2v6z" fill="currentColor"/>
        </svg>
        <span>{{ error }}</span>
      </div>

    
      <transition name="fade">
        <div v-if="result && !loading" class="result-container">
          
          <div class="sentiment-card">
            <div class="sentiment-header">
              <div class="sentiment-label" :class="getSentimentClass(result.sentiment)">
                {{ result.sentiment }}
              </div>
              <div class="sentiment-score">
                {{ (result.sentiment_score * 100).toFixed(0) }}%
              </div>
            </div>
            
            <div class="progress-bar">
              <div 
                class="progress-fill" 
                :style="{ width: (result.sentiment_score * 100) + '%' }"
                :class="getSentimentClass(result.sentiment)"
              ></div>
            </div>
          </div>

          
          <div class="article-card">
            <div class="card-header">
              <h3>{{ result.title }}</h3>
              <a :href="result.url" target="_blank" class="external-link">
                <svg width="16" height="16" viewBox="0 0 16 16" fill="none">
                  <path d="M12 8.66667V12.6667C12 13.0203 11.8595 13.3594 11.6095 13.6095C11.3594 13.8595 11.0203 14 10.6667 14H3.33333C2.97971 14 2.64057 13.8595 2.39052 13.6095C2.14048 13.3594 2 13.0203 2 12.6667V5.33333C2 4.97971 2.14048 4.64057 2.39052 4.39052C2.64057 4.14048 2.97971 4 3.33333 4H7.33333M10 2H14M14 2V6M14 2L6.66667 9.33333" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/>
                </svg>
              </a>
            </div>

            <div class="card-section">
              <h4>Analysis</h4>
              <p class="analysis-text">{{ result.reason }}</p>
            </div>

            <div class="card-section">
              <h4>Preview</h4>
              <p class="preview-text">{{ result.content }}</p>
            </div>
          </div>
        </div>
      </transition>
    </div>
  </div>
</template>

<script>
import axios from 'axios'

export default {
  name: 'HomeView',
  data() {
    return {
      newsUrl: '',
      result: null,
      loading: false,
      error: null
    }
  },
  methods: {
    async analyzeNews() {
      if (!this.newsUrl.trim()) {
        this.error = 'Please enter a URL'
        setTimeout(() => this.error = null, 3000)
        return
      }

      this.loading = true
      this.error = null
      this.result = null

      try {
        const apiUrl = import.meta.env.VITE_API_URL || 'http://localhost:8000'
        const response = await axios.post(`${apiUrl}/analyze`, {
          url: this.newsUrl
        })
        this.result = response.data
      } catch (err) {
        this.error = err.response?.data?.detail || 'Analysis failed. Please try again.'
        setTimeout(() => this.error = null, 5000)
      } finally {
        this.loading = false
      }
    },

    async loadSample() {
      try {
        const apiUrl = import.meta.env.VITE_API_URL || 'http://localhost:8000'
        const response = await axios.get(`${apiUrl}/sample-urls`)
        this.newsUrl = response.data.urls[0]
      } catch (err) {
        this.error = 'Failed to load sample'
        setTimeout(() => this.error = null, 3000)
      }
    },

    getSentimentClass(sentiment) {
      if (sentiment.includes('긍정')) return 'positive'
      if (sentiment.includes('부정')) return 'negative'
      return 'neutral'
    }
  }
}
</script>

<style scoped>
* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

.home {
  min-height: 100vh;
  background: linear-gradient(135deg, #0f0f0f 0%, #1a1a1a 100%);
  padding: 2rem;
  font-family: -apple-system, BlinkMacSystemFont, 'Inter', 'Segoe UI', sans-serif;
}

.container {
  max-width: 720px;
  margin: 0 auto;
}

/* 헤더 */
.header {
  text-align: center;
  margin-bottom: 3rem;
  padding-top: 2rem;
}

.header h1 {
  font-size: 2.5rem;
  font-weight: 700;
  background: linear-gradient(135deg, #fff 0%, #888 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
  margin-bottom: 0.5rem;
  letter-spacing: -0.02em;
}

.tagline {
  color: #666;
  font-size: 0.95rem;
  font-weight: 400;
}

/* 입력 카드 */
.input-card {
  background: rgba(255, 255, 255, 0.03);
  backdrop-filter: blur(10px);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 16px;
  padding: 1.5rem;
  margin-bottom: 2rem;
}

.input-wrapper {
  display: flex;
  gap: 0.75rem;
  margin-bottom: 1rem;
}

.url-input {
  flex: 1;
  background: rgba(255, 255, 255, 0.05);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 12px;
  padding: 1rem 1.25rem;
  color: #fff;
  font-size: 0.95rem;
  outline: none;
  transition: all 0.2s ease;
}

.url-input::placeholder {
  color: #666;
}

.url-input:focus {
  background: rgba(255, 255, 255, 0.08);
  border-color: rgba(255, 255, 255, 0.2);
}

.analyze-btn {
  background: #fff;
  color: #000;
  border: none;
  border-radius: 12px;
  padding: 1rem 2rem;
  font-size: 0.95rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s ease;
  min-width: 120px;
}

.analyze-btn:hover:not(:disabled) {
  background: #f0f0f0;
  transform: translateY(-1px);
}

.analyze-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.loading-dots {
  display: inline-flex;
  gap: 4px;
}

.loading-dots span {
  width: 6px;
  height: 6px;
  background: #000;
  border-radius: 50%;
  animation: bounce 1.4s infinite ease-in-out both;
}

.loading-dots span:nth-child(1) { animation-delay: -0.32s; }
.loading-dots span:nth-child(2) { animation-delay: -0.16s; }

@keyframes bounce {
  0%, 80%, 100% { transform: scale(0); }
  40% { transform: scale(1); }
}

.sample-link {
  background: none;
  border: none;
  color: #888;
  font-size: 0.875rem;
  cursor: pointer;
  transition: color 0.2s ease;
  padding: 0.5rem 0;
}

.sample-link:hover {
  color: #fff;
}

/* 로딩 카드 */
.loading-card {
  background: rgba(255, 255, 255, 0.03);
  backdrop-filter: blur(10px);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 16px;
  padding: 3rem;
  text-align: center;
  color: #999;
}

.pulse-loader {
  width: 40px;
  height: 40px;
  margin: 0 auto 1.5rem;
  border: 3px solid rgba(255, 255, 255, 0.1);
  border-top-color: #fff;
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

/* 에러 카드 */
.error-card {
  background: rgba(239, 68, 68, 0.1);
  border: 1px solid rgba(239, 68, 68, 0.3);
  border-radius: 12px;
  padding: 1rem 1.25rem;
  display: flex;
  align-items: center;
  gap: 0.75rem;
  color: #ef4444;
  font-size: 0.9rem;
  margin-bottom: 2rem;
}

/* 결과 컨테이너 */
.result-container {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

/* 감정 카드 */
.sentiment-card {
  background: rgba(255, 255, 255, 0.03);
  backdrop-filter: blur(10px);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 16px;
  padding: 1.5rem;
}

.sentiment-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1rem;
}

.sentiment-label {
  font-size: 0.875rem;
  font-weight: 600;
  padding: 0.5rem 1rem;
  border-radius: 8px;
  text-transform: uppercase;
  letter-spacing: 0.05em;
}

.sentiment-label.positive {
  background: rgba(34, 197, 94, 0.15);
  color: #22c55e;
}

.sentiment-label.negative {
  background: rgba(239, 68, 68, 0.15);
  color: #ef4444;
}

.sentiment-label.neutral {
  background: rgba(251, 146, 60, 0.15);
  color: #fb923c;
}

.sentiment-score {
  font-size: 2rem;
  font-weight: 700;
  color: #fff;
}

.progress-bar {
  height: 8px;
  background: rgba(255, 255, 255, 0.05);
  border-radius: 4px;
  overflow: hidden;
}

.progress-fill {
  height: 100%;
  transition: width 0.6s cubic-bezier(0.4, 0, 0.2, 1);
  border-radius: 4px;
}

.progress-fill.positive {
  background: linear-gradient(90deg, #22c55e, #10b981);
}

.progress-fill.negative {
  background: linear-gradient(90deg, #ef4444, #dc2626);
}

.progress-fill.neutral {
  background: linear-gradient(90deg, #fb923c, #f97316);
}

/* 기사 카드 */
.article-card {
  background: rgba(255, 255, 255, 0.03);
  backdrop-filter: blur(10px);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 16px;
  padding: 1.5rem;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: 1rem;
  margin-bottom: 1.5rem;
  padding-bottom: 1.5rem;
  border-bottom: 1px solid rgba(255, 255, 255, 0.05);
}

.card-header h3 {
  color: #fff;
  font-size: 1.25rem;
  font-weight: 600;
  line-height: 1.4;
  letter-spacing: -0.01em;
}

.external-link {
  color: #888;
  transition: color 0.2s ease;
  flex-shrink: 0;
  padding: 0.25rem;
}

.external-link:hover {
  color: #fff;
}

.card-section {
  margin-bottom: 1.5rem;
}

.card-section:last-child {
  margin-bottom: 0;
}

.card-section h4 {
  color: #888;
  font-size: 0.75rem;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.1em;
  margin-bottom: 0.75rem;
}

.analysis-text,
.preview-text {
  color: #ccc;
  font-size: 0.95rem;
  line-height: 1.6;
}

/* 애니메이션 */
.fade-enter-active,
.fade-leave-active {
  transition: all 0.3s ease;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
  transform: translateY(10px);
}

/* 반응형 */
@media (max-width: 640px) {
  .home {
    padding: 1rem;
  }

  .header h1 {
    font-size: 2rem;
  }

  .input-wrapper {
    flex-direction: column;
  }

  .analyze-btn {
    width: 100%;
  }

  .sentiment-score {
    font-size: 1.5rem;
  }
}
</style>