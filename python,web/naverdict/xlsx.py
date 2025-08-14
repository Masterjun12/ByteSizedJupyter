import json
import pandas as pd

# JSON 파일 로드
with open("words.json", "r", encoding="utf-8") as f:
    words_data = json.load(f)

# JSON 데이터를 DataFrame으로 변환
df = pd.DataFrame(words_data)

# Excel 파일로 저장 (encoding 제거, engine 추가)
df.to_excel("words.xlsx", index=False, engine="openpyxl")

print("✅ 변환 완료! words.xlsx 파일이 생성되었습니다.")
