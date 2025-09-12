"""
RSI, MACD, 거래량 기반 주식 추가매수 신호 분석 시스템 (개선판)
개발자: AI Assistant
버전: 2.0
"""

from dataclasses import dataclass, asdict
from typing import Dict, List, Any, Optional
import yfinance as yf
import pandas as pd
import numpy as np
from datetime import datetime
import warnings

warnings.filterwarnings("ignore")


@dataclass
class AnalyzerConfig:
    # 임계치
    rsi_oversold: float = 30.0
    rsi_overbought: float = 70.0
    volume_threshold_high: float = 1.5
    volume_threshold_low: float = 0.7

    # 윈도우
    rsi_window: int = 14
    macd_fast: int = 12
    macd_slow: int = 26
    macd_signal: int = 9
    volume_ma_window: int = 20

    # 현재값 계산 시 사용(최근 n일 평균)
    tail_avg_window: int = 5

    # 추세 판정 윈도우
    rsi_trend_window: int = 5
    obv_trend_window: int = 10

    # 타임존
    timezone: str = "Asia/Seoul"


class StockTechnicalAnalyzerV2:
    """개선된 주식 기술적 분석 클래스"""

    def __init__(self, config: Optional[AnalyzerConfig] = None):
        self.cfg = config or AnalyzerConfig()

    # ---------- 유틸 ----------

    @staticmethod
    def _safe_tail_mean(s: pd.Series, n: int, min_count: int = 2) -> float:
        """마지막 n개 중 NaN 제외 평균. min_count 미만이면 NaN."""
        tail = s.tail(n).dropna()
        return float(tail.mean()) if len(tail) >= min_count else np.nan

    @staticmethod
    def _level_crossover(series: pd.Series, level: float) -> str:
        """지표가 특정 level을 최근 2개 구간에서 상향/하향 돌파했는지."""
        s = series.dropna().tail(2)
        if len(s) < 2:
            return "없음"
        prev, curr = s.iloc[-2], s.iloc[-1]
        if prev <= level < curr:
            return "상향돌파"
        if prev >= level > curr:
            return "하향돌파"
        return "없음"

    @staticmethod
    def _detect_crossover(a: pd.Series, b: pd.Series) -> str:
        """두 선(a,b)의 최근 골든/데드 크로스 감지."""
        a2, b2 = a.dropna().tail(2), b.dropna().tail(2)
        if len(a2) < 2 or len(b2) < 2:
            return "없음"
        if a2.iloc[-1] > b2.iloc[-1] and a2.iloc[-2] <= b2.iloc[-2]:
            return "골든크로스"
        if a2.iloc[-1] < b2.iloc[-1] and a2.iloc[-2] >= b2.iloc[-2]:
            return "데드크로스"
        return "없음"

    @staticmethod
    def _detect_zero_cross(series: pd.Series) -> str:
        """시리즈가 0선을 최근에 상향/하향 돌파했는지."""
        s = series.dropna().tail(2)
        if len(s) < 2:
            return "없음"
        prev, curr = s.iloc[-2], s.iloc[-1]
        if prev <= 0 < curr:
            return "상향돌파"
        if prev >= 0 > curr:
            return "하향돌파"
        return "없음"

    # ---------- 지표 계산 ----------

    def calculate_rsi(self, close: pd.Series, window: Optional[int] = None) -> pd.Series:
        """RSI (Wilder 방식)"""
        w = window or self.cfg.rsi_window
        delta = close.diff()
        up = delta.clip(lower=0.0)
        down = -delta.clip(upper=0.0)
        # Wilder smoothing (EMA, alpha=1/window), min_periods=w로 초기 불안정 구간 보호
        roll_up = up.ewm(alpha=1 / w, adjust=False, min_periods=w).mean()
        roll_down = down.ewm(alpha=1 / w, adjust=False, min_periods=w).mean()
        rs = roll_up / roll_down.replace(0, np.nan)
        rsi = 100 - (100 / (1 + rs))
        return rsi

    def calculate_macd(
        self,
        close: pd.Series,
        fast: Optional[int] = None,
        slow: Optional[int] = None,
        signal: Optional[int] = None,
    ):
        """MACD, Signal, Histogram"""
        f = fast or self.cfg.macd_fast
        s = slow or self.cfg.macd_slow
        g = signal or self.cfg.macd_signal
        ema_fast = close.ewm(span=f, adjust=False).mean()
        ema_slow = close.ewm(span=s, adjust=False).mean()
        macd = ema_fast - ema_slow
        signal_line = macd.ewm(span=g, adjust=False).mean()
        histogram = macd - signal_line
        return macd, signal_line, histogram

    def calculate_volume_indicators(
        self, close: pd.Series, volume: pd.Series
    ) -> Dict[str, pd.Series]:
        """거래량 20MA(+min_periods), 벡터화 OBV(0에서 시작)"""
        w = self.cfg.volume_ma_window
        volume_ma = volume.rolling(window=w, min_periods=max(5, w // 2)).mean()
        sign = np.sign(close.diff().fillna(0))
        obv = (sign * volume.fillna(0)).cumsum()
        return {"volume_ma": volume_ma, "obv": obv}

    # ---------- 메인 분석 ----------

    def analyze_signals(self, ticker: str, period: str = "6mo") -> Dict[str, Any]:
        """
        메인 분석 함수
        Args:
            ticker: 종목 티커
            period: yfinance 기간 문자열 (예: '3mo','6mo','1y'...)
        """
        try:
            stock = yf.Ticker(ticker)
            data = stock.history(period=period)
            if data.empty:
                return {"error": f"{ticker} 데이터를 가져올 수 없습니다.", "ticker": ticker}

            # 기본 시리즈
            close = data["Close"].astype(float)
            volume = data["Volume"].astype(float)

            # 지표 계산
            rsi = self.calculate_rsi(close)
            macd, signal_line, histogram = self.calculate_macd(close)
            vols = self.calculate_volume_indicators(close, volume)
            volume_ma, obv = vols["volume_ma"], vols["obv"]

            # 현재값 계산(최근 n일 평균) - 길이 기반 자동 축소
            n = min(self.cfg.tail_avg_window, len(close))
            current_price = float(close.iloc[-1])

            current_rsi = self._safe_tail_mean(rsi, n, min_count=2)
            current_macd = self._safe_tail_mean(macd, n, min_count=2)
            current_signal = self._safe_tail_mean(signal_line, n, min_count=2)

            vol_recent_mean = self._safe_tail_mean(volume, n, min_count=2)
            volma_recent_mean = self._safe_tail_mean(volume_ma, n, min_count=1)

            # 분모가 NaN/0이면 확장 평균으로 대체
            if np.isnan(volma_recent_mean) or volma_recent_mean == 0:
                volma_recent_mean = float(
                    volume.rolling(self.cfg.volume_ma_window, min_periods=1).mean().tail(n).mean()
                )

            current_volume_ratio = float(vol_recent_mean / volma_recent_mean) if volma_recent_mean else np.nan

            # 추세 판정 (데이터 길이에 맞춰 자동 축소)
            rsi_tw = min(self.cfg.rsi_trend_window, max(1, len(rsi) - 1))
            obv_tw = min(self.cfg.obv_trend_window, max(1, len(obv) - 1))

            rsi_trend = "불충분"
            obv_trend = "불충분"

            if len(rsi) > rsi_tw:
                rsi_trend = "상승" if rsi.iloc[-1] > rsi.iloc[-1 - rsi_tw] else "하락"
            if len(obv) > obv_tw:
                obv_trend = "상승" if obv.iloc[-1] > obv.iloc[-1 - obv_tw] else "하락"

            macd_crossover = self._detect_crossover(macd, signal_line)
            macd_zero_cross = self._detect_zero_cross(macd)
            rsi_50_cross = self._level_crossover(rsi, 50)

            # -------- 신호 스코어링 --------
            signal_strength = 0
            signals: List[str] = []
            cfg = self.cfg

            # RSI 신호
            if not np.isnan(current_rsi):
                if current_rsi <= cfg.rsi_oversold:
                    signal_strength += 3
                    signals.append(f"🟢 RSI 과매도 구간 ({current_rsi:.1f}) - 강력한 매수신호")
                elif current_rsi <= 40:
                    signal_strength += 2
                    signals.append(f"🟡 RSI 매수 관심 구간 ({current_rsi:.1f})")
                elif current_rsi >= cfg.rsi_overbought:
                    signal_strength -= 2
                    signals.append(f"🔴 RSI 과매수 구간 ({current_rsi:.1f}) - 매수 자제")

                if rsi_50_cross == "상향돌파":
                    signal_strength += 1
                    signals.append("🔵 RSI 50선 상향 돌파 - 중기 모멘텀 개선")
                elif rsi_50_cross == "하향돌파":
                    signal_strength -= 1
                    signals.append("🟠 RSI 50선 하향 돌파 - 모멘텀 약화")

            # MACD 신호
            if macd_crossover == "골든크로스":
                if not np.isnan(current_macd) and current_macd > 0:
                    signal_strength += 4
                    signals.append("🟢 MACD 0선 상단에서 골든크로스 - 강력한 상승신호")
                else:
                    signal_strength += 3
                    signals.append("🟡 MACD 골든크로스 발생")
            elif macd_crossover == "데드크로스":
                signal_strength -= 3
                signals.append("🔴 MACD 데드크로스 - 주의 필요")
            elif not np.isnan(current_macd) and not np.isnan(current_signal) and current_macd > current_signal:
                signal_strength += 1
                signals.append("🔵 MACD 상승 추세 지속")

            # MACD 0선 돌파 보너스/패널티
            if macd_zero_cross == "상향돌파":
                signal_strength += 1
                signals.append("🔵 MACD 0선 상향 돌파 - 추세 개선")
            elif macd_zero_cross == "하향돌파":
                signal_strength -= 1
                signals.append("🟠 MACD 0선 하향 돌파 - 추세 약화")

            # 거래량 신호
            if not np.isnan(current_volume_ratio):
                if current_volume_ratio >= 3.0:
                    signal_strength += 3
                    signals.append(f"🟢 거래량 폭증 ({current_volume_ratio:.1f}배)")
                elif current_volume_ratio >= 2.0:
                    signal_strength += 2
                    signals.append(f"🟡 거래량 급증 ({current_volume_ratio:.1f}배)")
                elif current_volume_ratio >= cfg.volume_threshold_high:
                    signal_strength += 1
                    signals.append(f"🔵 거래량 증가 ({current_volume_ratio:.1f}배)")
                elif current_volume_ratio < cfg.volume_threshold_low:
                    signal_strength -= 1
                    signals.append(f"⚪ 거래량 부족 ({current_volume_ratio:.1f}배)")

            # OBV 추가 분석
            if obv_trend == "상승" and (not np.isnan(current_volume_ratio)) and current_volume_ratio > 1.0:
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

            # 데이터 품질/경고
            warnings_list: List[str] = []
            if len(close) < max(30, self.cfg.volume_ma_window + 5):
                warnings_list.append("분석 기간이 짧아 거래량/추세 신뢰도가 낮을 수 있습니다.")
            if np.isnan(current_volume_ratio):
                warnings_list.append("거래량 비율을 안정적으로 계산하지 못해 일부 신호가 약화되었습니다.")

            result = {
                "ticker": ticker,
                "current_price": current_price,
                "recommendation": recommendation,
                "action": action,
                "signal_strength": int(signal_strength),
                "technical_indicators": {
                    "RSI": None if np.isnan(current_rsi) else round(current_rsi, 2),
                    "RSI_trend": rsi_trend,
                    "RSI_50_cross": rsi_50_cross,
                    "MACD": None if np.isnan(current_macd) else round(current_macd, 4),
                    "MACD_Signal": None if np.isnan(current_signal) else round(current_signal, 4),
                    "MACD_crossover": macd_crossover,
                    "MACD_zero_cross": macd_zero_cross,
                    "Volume_ratio": None if np.isnan(current_volume_ratio) else round(current_volume_ratio, 2),
                    "OBV_trend": obv_trend,
                },
                "signals": signals,
                "analysis_date": pd.Timestamp.now(tz=self.cfg.timezone).strftime("%Y-%m-%d %H:%M:%S %Z"),
                "data_quality": {
                    "bars": int(len(close)),
                    "period": period,
                },
                "warnings": warnings_list,
            }
            return result

        except Exception as e:
            return {"error": f"Error analyzing {ticker}: {str(e)}", "ticker": ticker}

    # ---------- 출력/일괄분석 ----------

    @staticmethod
    def print_analysis(result: Dict[str, Any]) -> None:
        """분석 결과 출력(사람 친화형)"""
        if "error" in result:
            print(f"❌ {result.get('error')}")
            return

        print("=" * 60)
        print(f"📊 {result['ticker']} 기술적 분석 결과")
        print("=" * 60)
        print(f"💰 현재 가격: ${result['current_price']:.2f}")
        print(f"📈 최종 판단: {result['recommendation']}")
        print(f"🎯 액션: {result['action']}")
        print(f"🔥 신호 강도: {result['signal_strength']}/10")
        print(f"📅 분석 시점: {result['analysis_date']}")

        print("\n📊 기술적 지표 현황:")
        ti = result["technical_indicators"]
        rsi_val = "N/A" if ti["RSI"] is None else f"{ti['RSI']:.1f}"
        macd_val = "N/A" if ti["MACD"] is None else f"{ti['MACD']:.4f}"
        macd_sig = "N/A" if ti["MACD_Signal"] is None else f"{ti['MACD_Signal']:.4f}"
        vol_ratio = "N/A" if ti["Volume_ratio"] is None else f"{ti['Volume_ratio']:.1f}배"

        print(f"  • RSI: {rsi_val} ({ti['RSI_trend']} / 50선 {ti['RSI_50_cross']})")
        print(f"  • MACD: {macd_val} (Signal: {macd_sig})")
        print(f"  • MACD 교차: {ti['MACD_crossover']} / 0선 {ti['MACD_zero_cross']}")
        print(f"  • 거래량 비율: {vol_ratio}")
        print(f"  • OBV 추세: {ti['OBV_trend']}")

        if result["signals"]:
            print("\n🚨 주요 신호:")
            for i, s in enumerate(result["signals"], 1):
                print(f"  {i}. {s}")

        if result.get("warnings"):
            print("\n⚠️ 경고:")
            for w in result["warnings"]:
                print(f"  - {w}")

        print("\n" + "=" * 60)

    def batch_analysis(self, tickers: List[str], save_csv: bool = True, filename: str = "stock_analysis_v2.csv"):
        """여러 종목 일괄 분석 + CSV 저장"""
        results = []
        for ticker in tickers:
            print(f"🔍 {ticker} 분석 중...")
            res = self.analyze_signals(ticker)
            self.print_analysis(res)
            if "error" not in res:
                results.append(res)
            print("\n" + "-" * 40 + "\n")

        if save_csv and results:
            rows = []
            for r in results:
                ti = r["technical_indicators"]
                rows.append({
                    "Ticker": r["ticker"],
                    "Current_Price": r["current_price"],
                    "Recommendation": r["recommendation"],
                    "Action": r["action"],
                    "Signal_Strength": r["signal_strength"],
                    "RSI": ti["RSI"],
                    "RSI_Trend": ti["RSI_trend"],
                    "RSI_50_Cross": ti["RSI_50_cross"],
                    "MACD": ti["MACD"],
                    "MACD_Signal": ti["MACD_Signal"],
                    "MACD_Crossover": ti["MACD_crossover"],
                    "MACD_Zero_Cross": ti["MACD_zero_cross"],
                    "Volume_Ratio": ti["Volume_ratio"],
                    "OBV_Trend": ti["OBV_trend"],
                    "Analysis_Date": r["analysis_date"],
                    "Bars": r["data_quality"]["bars"],
                    "Period": r["data_quality"]["period"],
                })
            df = pd.DataFrame(rows)
            df.to_csv(filename, index=False, encoding="utf-8-sig")
            print(f"✅ 분석 결과가 {filename}에 저장되었습니다.")
            return df

        return results


# 사용 예시
if __name__ == "__main__":
    analyzer = StockTechnicalAnalyzerV2()

    print("🚀 Tempus AI (TEM) 분석:")
    tem = analyzer.analyze_signals("TEM")
    analyzer.print_analysis(tem)

    biotech = ["TEM", "GLUE", "RXRX"]
    print("\n📊 바이오테크 포트폴리오 일괄 분석:")
    analyzer.batch_analysis(biotech, save_csv=True, filename="biotech_portfolio_analysis_v2.csv")
