from flask import Flask, request, jsonify
from flask_cors import CORS  # ✅ `pip install flask-cors` がインストールされていることを確認
import openai
import os
from dotenv import load_dotenv

# ✅ .env ファイルを読み込む
load_dotenv()

app = Flask(__name__)

# ✅ CORS を許可（Chrome拡張機能が Flask API にアクセスできるようにする）
CORS(app, resources={r"/*": {"origins": "*"}})  # すべてのオリジンからの API アクセスを許可

# ✅ OpenAI API キーが正しく読み込まれていることを確認
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
if not OPENAI_API_KEY:
    raise ValueError("❌ 環境変数 OPENAI_API_KEY が設定されていません！.env ファイルが存在し、正しく設定されているか確認してください！")
openai.api_key = OPENAI_API_KEY  

@app.route('/generate', methods=['POST'])
def generate_reply():
    try:
        data = request.json
        print(f"📥 リクエスト受信: {data}")  # ✅ デバッグ用にリクエスト内容を記録

        email_text = data.get("content", "").strip()
        language = data.get("language", "ja")
        purpose = data.get("purpose", "Business")
        tone = data.get("tone", "formal")

        if not email_text:
            return jsonify({"error": "メールの内容が空です"}), 400

        prompt = f"{language}で、{tone}な口調で、以下のメール内容に返信を作成してください：{email_text}"

        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[{"role": "system", "content": "あなたはプロフェッショナルなメールアシスタントです。"},
                      {"role": "user", "content": prompt}],
            max_tokens=500,
            temperature=0.7
        )

        reply_text = response.choices[0].message.content.strip()
        return jsonify({"email": reply_text})

    except Exception as e:
        print(f"❌ エラー: {str(e)}")  # ✅ デバッグ用にエラーを記録
        return jsonify({"error": f"サーバーエラー: {str(e)}"}), 500

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000, debug=True)
