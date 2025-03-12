from flask import Flask, request, jsonify
from flask_cors import CORS  # ✅ 確保已安裝 `pip install flask-cors`
import openai
import os
from dotenv import load_dotenv

# ✅ 加載 .env 文件
load_dotenv()

app = Flask(__name__)

# ✅ 允許 CORS（讓 Chrome 擴充功能可以訪問 Flask API）
CORS(app, resources={r"/*": {"origins": "*"}})  # 允許所有來源訪問 API

# ✅ 確保 OpenAI API 金鑰加載成功
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
if not OPENAI_API_KEY:
    raise ValueError("❌ 環境變數 OPENAI_API_KEY 未設置！請確認 .env 文件是否存在並設置正確！")
openai.api_key = OPENAI_API_KEY  

@app.route('/generate', methods=['POST'])
def generate_reply():
    try:
        data = request.json
        print(f"📥 收到請求: {data}")  # ✅ Debug 記錄請求內容

        email_text = data.get("content", "").strip()
        language = data.get("language", "ja")
        purpose = data.get("purpose", "Business")
        tone = data.get("tone", "formal")

        if not email_text:
            return jsonify({"error": "メールの内容が空です"}), 400

        prompt = f"請用{language}，用{tone}的語氣，為以下郵件內容生成回信：{email_text}"

        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[{"role": "system", "content": "你是一個專業的郵件助手。"},
                      {"role": "user", "content": prompt}],
            max_tokens=500,
            temperature=0.7
        )

        reply_text = response.choices[0].message.content.strip()
        return jsonify({"email": reply_text})

    except Exception as e:
        print(f"❌ 錯誤: {str(e)}")  # ✅ Debug 記錄錯誤
        return jsonify({"error": f"伺服器錯誤: {str(e)}"}), 500

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000, debug=True)
