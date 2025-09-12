# 매수매도분석기.py

# 이전에 생성한 분석기 클래스를 불러옵니다.
from re import A
from stock_technical_analyzer_2 import StockTechnicalAnalyzerV2 as StockTechnicalAnalyzer

# --- 여기서부터 사용자가 원하는 코드를 실행합니다. ---

# 1. 분석기 초기화
analyzer = StockTechnicalAnalyzer()

# 2. 단일 종목 분석 (예: Apple)
print("🚀 단일 종목 분석:")
result = analyzer.analyze_signals("139480.KQ")  # KRX 코드 사용
analyzer.print_analysis(result)

# 3. 여러 종목 일괄 분석 및 CSV 저장
print("\n📊 주요 기술주 포트폴리오 일괄 분석:")
tickers = ["RXRX", "GLUE", "SDGR", "TEM", "INTC"]
analysis_results_df = analyzer.batch_analysis(
    tickers, 
    save_csv=True, 
    filename="tech_stock_analysis.csv"
)

# 최종 저장된 데이터프레임 확인
if analysis_results_df is not None:
    print("\n✅ 최종 분석 결과 요약 (tech_stock_analysis.csv):")
    print(analysis_results_df.to_string()) # type: ignore
