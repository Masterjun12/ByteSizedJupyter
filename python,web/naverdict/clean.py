import json
import pandas as pd

with open("words.json", "r", encoding="utf-8") as f:
    words_data = json.load(f)

cleaned_words = [word.replace("·", "") for word in words_data]

with open("words.json", "w", encoding="utf-8") as f:
    json.dump(cleaned_words, f, ensure_ascii=False, indent=4)

print("✅ 중간 점(·) 제거 완료! words.json 파일이 업데이트되었습니다.")

# JSON 데이터를 DataFrame으로 변환
df = pd.DataFrame(words_data)

# Excel 파일로 저장 (encoding 제거, engine 추가)
df.to_excel("words.xlsx", index=False, engine="openpyxl")

print("✅ 변환 완료! words.xlsx 파일이 생성되었습니다.")
