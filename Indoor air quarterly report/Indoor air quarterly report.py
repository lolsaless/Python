import pandas as pd

# Step 1: Load data
data_df = pd.read_csv('data.csv')
result_df = pd.read_csv('result.csv')

# Step 2: Merge data on '접수번호'
merged_df = pd.merge(data_df, result_df, on='접수번호', how='inner')

# Step 3: Filter for '실내공기질' in '검체유형_x'
filtered_df = merged_df[merged_df['검체유형_x'].str.contains('실내공기질', na=False)].copy()

# Step 4: Add '시설군' column derived from '검체유형_x'
filtered_df['시설군'] = filtered_df['검체유형_x'].str.split('/').str[2]

# Step 5: Select required columns
selected_columns = [
    '의뢰기관', '시설군', '배출시설', '시설명', '채취장소_x', '시료명_x',
    'PM10', 'PM2.5', 'CO2', '폼알데하이드', '부유세균', '라돈', '라돈(밀폐)', '벤젠', '톨루엔', '에틸벤젠', '자일렌', '스틸렌', '부적합항목', '확인일', '접수번호'
]
extracted_df = filtered_df[selected_columns].copy()

# Step 6: Rename columns
rename_columns = {
    '의뢰기관': '시군명',
    '배출시설': '세부시설군',
    '채취장소_x': '주소',
    'PM10': '미세먼지(PM10)',
    'PM2.5': '초미세먼지(PM2.5)',
    'CO2': '이산화탄소',
    '부유세균': '총부유세균'
}
extracted_df.rename(columns=rename_columns, inplace=True)

# Step 7: Create '접수번호_10자리' and '채취지점'
extracted_df['접수번호_10자리'] = extracted_df['접수번호'].str[:10]
extracted_df['채취지점'] = extracted_df.groupby('시설명')['시료명_x'].transform(lambda x: ', '.join(x.unique()))

# Step 8: Calculate the mean of numeric columns grouped by '시설명' and '접수번호_10자리'
numeric_columns = ['미세먼지(PM10)', '초미세먼지(PM2.5)', '이산화탄소', '폼알데하이드', '총부유세균', '라돈']
data_avg = extracted_df.groupby(['시설명', '접수번호_10자리']).agg({col: 'mean' for col in numeric_columns}).reset_index()

# Step 9: Merge the average data with non-numeric data
data_final = data_avg.merge(
    extracted_df.drop(columns=numeric_columns).drop_duplicates(['시설명', '접수번호_10자리']),
    on=['시설명', '접수번호_10자리']
)

# Step 10: Drop unnecessary columns and sort the data
data_final.drop(columns='시료명_x', inplace=True)
data_sorted = data_final.sort_values(
    by=['시군명', '시설군', '세부시설군', '시설명', '주소', '채취지점', '미세먼지(PM10)', '초미세먼지(PM2.5)', '이산화탄소', '폼알데하이드', '총부유세균', '라돈']
)

# Step 11: Save the final report
output_path = 'report_data.csv'
data_sorted.to_csv(output_path, index=False)

print(f"Report has been saved to {output_path}")
