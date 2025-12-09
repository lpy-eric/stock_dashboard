# stock_dashboard
初級版：個人化股票即時儀表板 (Real-time Stock Dashboard)
這個專案最適合練習 前端視覺化 和 API 數據抓取。

核心功能：

- 用戶在 HTML 頁面輸入股票代碼 (e.g., AAPL, TSLA)。

- 後端調用 API 獲取當前價格、今日漲跌幅、以及過去 30 天的歷史數據。

- 前端使用圖表庫 (如 Chart.js) 畫出 K 線圖或折線圖。

- 設定一個「觀察清單」，將喜歡的股票存在網頁上 (Local Storage 或簡單資料庫)。

技術堆疊 (Tech Stack)：

- Frontend: HTML5, CSS (Bootstrap 或 Tailwind), JavaScript (Chart.js 或 TradingView Widget)。

- Backend: Python (Flask 或 FastAPI) - 用來處理 API 請求。

- Data API: yfinance (免費、簡單、Python 庫) 或 Alpha Vantage (免費 Key)。

為什麼選這個？ 成就感很高，做出來的介面很酷，且不涉及真實交易風險。
