from flask import Flask, request, jsonify
from flask_cors import CORS  
import openai
import os
from dotenv import load_dotenv


load_dotenv()

app = Flask(__name__)


CORS(app, resources={r"/*": {"origins": "*"}})  


OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
if not OPENAI_API_KEY:
    raise ValueError("❌ 環境変数 OPENAI_API_KEY が設定されていません！.envファイルが存在し、正しく設定されているか確認してください！")
openai.api_key = OPENAI_API_KEY  


def get_language_name(lang_code):
    language_map = {
        "ja": "日本語",
        "zh-CN": "中国語（簡体字）",
        "zh-TW": "中国語（繁体字）",
        "en": "英語",
        "ko": "韓国語"
    }
    return language_map.get(lang_code, "日本語")  

def get_tone_description(purpose, language_code):
    if language_code == "ja":
        return "ビジネス向けの丁寧な" if purpose == "Business" else "カジュアルな"
    elif language_code.startswith("zh"):
        return "商务正式" if purpose == "Business" else "轻松随意"
    elif language_code == "en":
        return "professional and formal" if purpose == "Business" else "casual and friendly"
    elif language_code == "ko":
        return "비즈니스 및 공식적인" if purpose == "Business" else "캐주얼하고 친근한"
    else:
        return "ビジネス向けの丁寧な" if purpose == "Business" else "カジュアルな"

@app.route('/generate', methods=['POST'])
def generate_reply():
    try:
        data = request.json
        print(f"📥 リクエスト受信: {data}")  

        email_text = data.get("content", "").strip()
        language_code = data.get("language", "ja")
        purpose = data.get("purpose", "Business") 

        if not email_text:
            return jsonify({"error": "メールの内容が空です"}), 400

        language_name = get_language_name(language_code)
        tone_description = get_tone_description(purpose, language_code)
        
        # システムプロンプトと言語指定を設定
        if language_code == "ja":
            system_prompt = "あなたは専門的なメール返信アシスタントです。必ず日本語で返信を作成してください。"
            user_prompt = f"以下のメールに対して、{tone_description}口調で日本語の返信を作成してください：\n\n{email_text}"
        elif language_code == "zh-CN":
            system_prompt = "你是一位专业的邮件回复助手。请务必使用简体中文创建回复。"
            user_prompt = f"请使用{tone_description}的语气，用简体中文为以下邮件内容生成回信：\n\n{email_text}"
        elif language_code == "zh-TW":
            system_prompt = "你是一位專業的郵件回覆助手。請務必使用繁體中文創建回覆。"
            user_prompt = f"請使用{tone_description}的語氣，用繁體中文為以下郵件內容生成回信：\n\n{email_text}"
        elif language_code == "en":
            system_prompt = "You are a professional email reply assistant. You must create your reply in English only."
            user_prompt = f"Please create a {purpose.lower()} tone reply in English for the following email:\n\n{email_text}"
        elif language_code == "ko":
            system_prompt = "당신은 전문적인 이메일 회신 도우미입니다. 반드시 한국어로만 답장을 작성해 주세요."
            user_prompt = f"다음 이메일에 대해 {purpose.lower()} 톤으로 한국어 답장을 작성해 주세요:\n\n{email_text}"
        else:
            # デフォルトは日本語
            system_prompt = "あなたは専門的なメール返信アシスタントです。必ず日本語で返信を作成してください。"
            user_prompt = f"以下のメールに対して、{tone_description}口調で日本語の返信を作成してください：\n\n{email_text}"

        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            max_tokens=500,
            temperature=0.7
        )

        reply_text = response.choices[0].message.content.strip()
        return jsonify({"email": reply_text})

    except Exception as e:
        print(f"❌ エラー: {str(e)}")  
        return jsonify({"error": f"サーバーエラー: {str(e)}"}), 500

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000, debug=True)  