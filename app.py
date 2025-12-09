from flask import Flask, render_template, request, jsonify
import yfinance as yf
import pandas as pd
import numpy as np

app = Flask(__name__)

stock_cache = {}

def get_df(symbol):
    if symbol in stock_cache: return stock_cache[symbol]
    stock = yf.Ticker(symbol)
    df = stock.history(period='max', interval='1wk')
    if df.empty: return None
    stock_cache[symbol] = df
    return df

def calculate_basic(df):
    close = df['Close']
    for period in [5, 20, 60, 120, 240]:
        df[f'MA{period}'] = close.rolling(window=period).mean()
    return df

def calculate_specific_indicator(df, indicator_type):
    close = df['Close']
    high = df['High']
    low = df['Low']
    volume = df['Volume']
    result = {}

    if indicator_type == 'macd':
        exp1 = close.ewm(span=12, adjust=False).mean()
        exp2 = close.ewm(span=26, adjust=False).mean()
        macd_dif = exp1 - exp2
        macd_dea = macd_dif.ewm(span=9, adjust=False).mean()
        result = { 'macd_dif': macd_dif.tail(1000).fillna(0).tolist(), 'macd_dea': macd_dea.tail(1000).fillna(0).tolist() }
    elif indicator_type == 'sar':
        ma20 = close.rolling(window=20).mean()
        sar_bull = low.rolling(3).min()
        sar_bear = high.rolling(3).max()
        sar = np.where(close > ma20, sar_bull, sar_bear)
        result = {'sar': pd.Series(sar, index=df.index).tail(1000).fillna(0).tolist()}
    elif indicator_type == 'rsi':
        delta = close.diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        result = {'rsi': rsi.tail(1000).fillna(0).tolist()}
    elif indicator_type == 'kdj':
        low_min = low.rolling(window=9).min()
        high_max = high.rolling(window=9).max()
        rsv = (close - low_min) / (high_max - low_min) * 100
        k = rsv.ewm(com=2).mean()
        d = k.ewm(com=2).mean()
        j = 3 * k - 2 * d
        result = { 'k': k.tail(1000).fillna(0).tolist(), 'd': d.tail(1000).fillna(0).tolist(), 'j': j.tail(1000).fillna(0).tolist() }
    elif indicator_type == 'cci':
        tp = (high + low + close) / 3
        sma_tp = tp.rolling(window=14).mean()
        mad = (tp - sma_tp).abs().rolling(window=14).mean()
        cci = (tp - sma_tp) / (0.015 * mad)
        result = {'cci': cci.tail(1000).fillna(0).tolist()}
    elif indicator_type == 'obv':
        obv = (np.sign(close.diff()) * volume).fillna(0).cumsum()
        result = {'obv': obv.tail(1000).fillna(0).tolist()}
    elif indicator_type == 'vwap':
        cum_vol = volume.cumsum()
        cum_vol_price = (volume * (high + low + close) / 3).cumsum()
        vwap = cum_vol_price / cum_vol
        result = {'vwap': vwap.tail(1000).fillna(0).tolist()}
    elif indicator_type == 'boll':
        sma20 = close.rolling(window=20).mean()
        std20 = close.rolling(window=20).std()
        result = { 'boll_upper': (sma20 + std20 * 2).tail(1000).fillna(0).tolist(), 'boll_mid': sma20.tail(1000).fillna(0).tolist(), 'boll_lower': (sma20 - std20 * 2).tail(1000).fillna(0).tolist() }
    elif indicator_type == 'atr':
        tr1 = high - low
        tr2 = (high - close.shift()).abs()
        tr3 = (low - close.shift()).abs()
        tr = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
        atr = tr.rolling(window=14).mean()
        result = {'atr': atr.tail(1000).fillna(0).tolist()}

    return result

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/get_basic_data')
def get_basic_data():
    symbol = request.args.get('symbol')
    if not symbol: return jsonify({'error': '請提供代碼'}), 400
    if symbol in stock_cache: del stock_cache[symbol]

    try:
        df = get_df(symbol)
        if df is None: return jsonify({'error': '無數據'}), 404
        
        df = calculate_basic(df)
        df_display = df.tail(1000).fillna(0)
        
        result = {
            'current_price': round(df['Close'].iloc[-1], 2),
            'change_percent': round(((df['Close'].iloc[-1] - df['Close'].iloc[-2]) / df['Close'].iloc[-2]) * 100, 2),
            'dates': df_display.index.strftime('%Y-%m-%d').tolist(),
            'candles': [],
            # 新增 volume 數據
            'volume': df_display['Volume'].tolist(),
            'ma5': df_display['MA5'].tolist(),
            'ma20': df_display['MA20'].tolist(),
            'ma60': df_display['MA60'].tolist(),
            'ma120': df_display['MA120'].tolist(),
            'ma240': df_display['MA240'].tolist(),
        }
        for index, row in df_display.iterrows():
            result['candles'].append({
                'x': index.strftime('%Y-%m-%d'),
                'y': [round(row['Open'], 2), round(row['High'], 2), round(row['Low'], 2), round(row['Close'], 2)]
            })
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/get_specific_indicator')
def get_specific_indicator():
    symbol = request.args.get('symbol')
    ind_type = request.args.get('type')
    try:
        df = get_df(symbol)
        if df is None: return jsonify({'error': '請先加載基礎數據'}), 400
        data = calculate_specific_indicator(df, ind_type)
        return jsonify(data)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)