
"""
RSI, MACD, 거래량 기반 주식 추가매수 신호 분석 시스템
개발자: AI Assistant
버전: 1.0
"""

import yfinance as yf
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import warnings
warnings.filterwarnings('ignore')

class StockTechnicalAnalyzer:
    """주식 기술적 분석 클래스"""

    def __init__(self):
        self.rsi_oversold = 30
        self.rsi_overbought = 70
        self.volume_threshold_high = 1.5
        self.volume_threshold_low = 0.7

    def calculate_rsi(self, data, window=14):
        """RSI 계산"""
        delta = data.diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=window).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=window).mean()
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        return rsi

    def calculate_macd(self, data, fast=12, slow=26, signal=9):
        """MACD 계산"""
        exp1 = data.ewm(span=fast, adjust=False).mean()
        exp2 = data.ewm(span=slow, adjust=False).mean()
        macd = exp1 - exp2
        signal_line = macd.ewm(span=signal, adjust=False).mean()
        histogram = macd - signal_line
        return macd, signal_line, histogram

    def calculate_volume_indicators(self, data, volume):
        """거래량 지표 계산 (OBV 포함)"""
        volume_ma = volume.rolling(20).mean()

        # OBV 계산
        obv = []
        prev_close = data.iloc[0]
        obv_value = volume.iloc[0]
        obv.append(obv_value)

        for i in range(1, len(data)):
            if data.iloc[i] > prev_close:
                obv_value += volume.iloc[i]
            elif data.iloc[i] < prev_close:
                obv_value -= volume.iloc[i]

            obv.append(obv_value)
            prev_close = data.iloc[i]

        obv_series = pd.Series(obv, index=data.index)
        return volume_ma, obv_series

    def detect_crossover(self, line1, line2):
        """교차 신호 감지"""
        if len(line1) >= 2 and len(line2) >= 2:
            if (line1.iloc[-1] > line2.iloc[-1] and line1.iloc[-2] <= line2.iloc[-2]):
                return "골든크로스"
            elif (line1.iloc[-1] < line2.iloc[-1] and line1.iloc[-2] >= line2.iloc[-2]):
                return "데드크로스"
        return "없음"

    def analyze_signals(self, ticker, period="6mo"):
        """
        메인 분석 함수
        Args:
            ticker (str): 주식 티커 심볼
            period (str): 분석 기간 ('1mo', '3mo', '6mo', '1y' 등)
        """
        try:
            # 데이터 다운로드
            stock = yf.Ticker(ticker)
            data = stock.history(period=period)

            if data.empty:
                return f"Error: {ticker} 데이터를 가져올 수 없습니다."

            # 기술적 지표 계산
            close_prices = data['Close']
            volume = data['Volume']

            rsi = self.calculate_rsi(close_prices)
            macd, signal_line, histogram = self.calculate_macd(close_prices)
            volume_ma, obv = self.calculate_volume_indicators(close_prices, volume)

            # 현재 지표 값들 (최근 5일 평균)
            current_rsi = rsi.tail(5).mean()
            current_macd = macd.tail(5).mean()
            current_signal = signal_line.tail(5).mean()
            current_volume_ratio = (volume.tail(5).mean() / volume_ma.tail(5).mean())

            # 추세 분석
            rsi_trend = "상승" if rsi.iloc[-1] > rsi.iloc[-5] else "하락"
            obv_trend = "상승" if obv.iloc[-1] > obv.iloc[-10] else "하락"
            macd_crossover = self.detect_crossover(macd, signal_line)

            # 신호 강도 계산
            signal_strength = 0
            signals = []

            # RSI 신호 분석
            if current_rsi <= self.rsi_oversold:
                signal_strength += 3
                signals.append(f"🟢 RSI 과매도 구간 ({current_rsi:.1f}) - 강력한 매수신호")
            elif current_rsi <= 40:
                signal_strength += 2
                signals.append(f"🟡 RSI 매수 관심 구간 ({current_rsi:.1f})")
            elif current_rsi >= self.rsi_overbought:
                signal_strength -= 2
                signals.append(f"🔴 RSI 과매수 구간 ({current_rsi:.1f}) - 매수 자제")

            # MACD 신호 분석
            if macd_crossover == "골든크로스":
                if current_macd > 0:
                    signal_strength += 4
                    signals.append("🟢 MACD 0선 상향 골든크로스 - 강력한 상승신호")
                else:
                    signal_strength += 3
                    signals.append("🟡 MACD 골든크로스 발생")
            elif macd_crossover == "데드크로스":
                signal_strength -= 3
                signals.append("🔴 MACD 데드크로스 - 주의 필요")
            elif current_macd > current_signal:
                signal_strength += 1
                signals.append("🔵 MACD 상승 추세 지속")

            # 거래량 신호 분석
            if current_volume_ratio >= 3.0:
                signal_strength += 3
                signals.append(f"🟢 거래량 폭증 ({current_volume_ratio:.1f}배)")
            elif current_volume_ratio >= 2.0:
                signal_strength += 2
                signals.append(f"🟡 거래량 급증 ({current_volume_ratio:.1f}배)")
            elif current_volume_ratio >= self.volume_threshold_high:
                signal_strength += 1
                signals.append(f"🔵 거래량 증가 ({current_volume_ratio:.1f}배)")
            elif current_volume_ratio < self.volume_threshold_low:
                signal_strength -= 1
                signals.append(f"⚪ 거래량 부족 ({current_volume_ratio:.1f}배)")

            # OBV 추가 분석
            if obv_trend == "상승" and current_volume_ratio > 1.0:
                signal_strength += 1
                signals.append("🔵 OBV 상승 추세 - 매수 압력 증가")

            # 최종 판단
            if signal_strength >= 6:
                recommendation = "🟢 매우 강력한 추가매수 신호"
                action = "적극 매수"
            elif signal_strength >= 4:
                recommendation = "🟡 강력한 추가매수 신호"
                action = "매수 권장"
            elif signal_strength >= 2:
                recommendation = "🔵 적극적 추가매수 고려"
                action = "매수 검토"
            elif signal_strength >= 0:
                recommendation = "⚪ 신중한 추가매수 검토"
                action = "관망"
            elif signal_strength >= -2:
                recommendation = "🟠 관망 권장"
                action = "매수 자제"
            else:
                recommendation = "🔴 매수 자제 / 손절 검토"
                action = "매수 금지"

            return {
                'ticker': ticker,
                'current_price': close_prices.iloc[-1],
                'recommendation': recommendation,
                'action': action,
                'signal_strength': signal_strength,
                'technical_indicators': {
                    'RSI': round(current_rsi, 2),
                    'RSI_trend': rsi_trend,
                    'MACD': round(current_macd, 4),
                    'MACD_Signal': round(current_signal, 4),
                    'MACD_crossover': macd_crossover,
                    'Volume_ratio': round(current_volume_ratio, 2),
                    'OBV_trend': obv_trend
                },
                'signals': signals,
                'analysis_date': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            }

        except Exception as e:
            return f"Error analyzing {ticker}: {str(e)}"

    def print_analysis(self, result):
        """분석 결과 출력"""
        if isinstance(result, str):
            print(result)
            return

        print("="*60)
        print(f"📊 {result['ticker']} 기술적 분석 결과")
        print("="*60)
        print(f"💰 현재 가격: ${result['current_price']:.2f}")
        print(f"📈 최종 판단: {result['recommendation']}")
        print(f"🎯 액션: {result['action']}")
        print(f"🔥 신호 강도: {result['signal_strength']}/10")
        print(f"📅 분석 시점: {result['analysis_date']}")

        print("\n📊 기술적 지표 현황:")
        ti = result['technical_indicators']
        print(f"  • RSI: {ti['RSI']:.1f} ({ti['RSI_trend']})")
        print(f"  • MACD: {ti['MACD']:.4f} (Signal: {ti['MACD_Signal']:.4f})")
        print(f"  • MACD 교차: {ti['MACD_crossover']}")
        print(f"  • 거래량 비율: {ti['Volume_ratio']:.1f}배")
        print(f"  • OBV 추세: {ti['OBV_trend']}")

        print("\n🚨 주요 신호:")
        for i, signal in enumerate(result['signals'], 1):
            print(f"  {i}. {signal}")

        print("\n" + "="*60)

    def batch_analysis(self, tickers, save_csv=True, filename="stock_analysis.csv"):
        """여러 종목 일괄 분석"""
        results = []

        for ticker in tickers:
            print(f"🔍 {ticker} 분석 중...")
            result = self.analyze_signals(ticker)

            if not isinstance(result, str):
                results.append(result)
                self.print_analysis(result)
                print("\n" + "-"*40 + "\n")
            else:
                print(f"❌ {ticker} 분석 실패: {result}\n")

        if save_csv and results:
            df_data = []
            for result in results:
                row = {
                    'Ticker': result['ticker'],
                    'Current_Price': result['current_price'],
                    'Recommendation': result['recommendation'],
                    'Action': result['action'],
                    'Signal_Strength': result['signal_strength'],
                    'RSI': result['technical_indicators']['RSI'],
                    'RSI_Trend': result['technical_indicators']['RSI_trend'],
                    'MACD': result['technical_indicators']['MACD'],
                    'MACD_Signal': result['technical_indicators']['MACD_Signal'],
                    'MACD_Crossover': result['technical_indicators']['MACD_crossover'],
                    'Volume_Ratio': result['technical_indicators']['Volume_ratio'],
                    'OBV_Trend': result['technical_indicators']['OBV_trend'],
                    'Analysis_Date': result['analysis_date']
                }
                df_data.append(row)

            df = pd.DataFrame(df_data)
            df.to_csv(filename, index=False, encoding='utf-8-sig')
            print(f"✅ 분석 결과가 {filename}에 저장되었습니다.")

            return df

        return results


# 사용 예시
if __name__ == "__main__":
    # 분석기 초기화
    analyzer = StockTechnicalAnalyzer()

    # 단일 종목 분석
    print("🚀 Tempus AI (TEM) 분석:")
    tem_result = analyzer.analyze_signals("TEM")
    analyzer.print_analysis(tem_result)

    # 여러 종목 일괄 분석
    biotech_tickers = ["TEM", "GLUE", "RXRX"]
    print("\n📊 바이오테크 포트폴리오 일괄 분석:")
    biotech_results = analyzer.batch_analysis(biotech_tickers, 
                                            save_csv=True, 
                                            filename="biotech_portfolio_analysis.csv")
