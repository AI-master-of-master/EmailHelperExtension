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

def create_email_reply_prompt(language_code, purpose, email_text):
    """より具体的なメール返信のプロンプトを作成する関数"""
    
    if language_code == "ja":
        system_prompt = """あなたは専門的なメール返信アシスタントです。以下のガイドラインに従って返信を作成してください：
1. 必ず日本語で返信を作成する
2. 元のメールの内容を確認し、適切に応答する
3. 返信メールには適切な挨拶で始め、締めくくりにもビジネスマナーに合った表現を使う
4. メールの本文は、元のメールの内容に対する応答を明確にし、必要な情報を過不足なく含める
5. 返信全体の構造を整える（挨拶→本文→締めの挨拶）"""
        
        user_prompt = f"""以下のメールに対して、{get_tone_description(purpose, language_code)}口調で日本語の返信を作成してください。

【元のメール】
{email_text}

【返信メールの作成ガイドライン】
- 敬称や挨拶などの適切なビジネスマナーを含めてください
- 元のメールの要点に対して過不足なく回答してください
- 日本語として自然な文章になるようにしてください
- 返信メールの形式（件名不要、本文のみ）で作成してください"""

    elif language_code == "zh-CN":
        system_prompt = """你是一位专业的邮件回复助手。请按照以下指南创建回复：
1. 务必使用简体中文创建回复
2. 确认原始邮件内容并给予适当回应
3. 回复邮件应以合适的问候语开始，并以符合商务礼仪的表达结束
4. 邮件正文应明确回应原始邮件内容，并包含必要的信息
5. 整体回复结构应规范（开头问候→正文→结束语）"""
        
        user_prompt = f"""请使用{get_tone_description(purpose, language_code)}的语气，用简体中文为以下邮件内容生成回信：

【原始邮件】
{email_text}

【回复邮件创建指南】
- 请包含适当的称呼和问候语
- 对原始邮件的要点进行完整回应
- 确保回复内容自然流畅
- 仅创建邮件正文内容（无需主题行）"""

    elif language_code == "zh-TW":
        system_prompt = """你是一位專業的郵件回覆助手。請按照以下指南創建回覆：
1. 務必使用繁體中文創建回覆
2. 確認原始郵件內容並給予適當回應
3. 回覆郵件應以合適的問候語開始，並以符合商務禮儀的表達結束
4. 郵件正文應明確回應原始郵件內容，並包含必要的資訊
5. 整體回覆結構應規範（開頭問候→正文→結束語）"""
        
        user_prompt = f"""請使用{get_tone_description(purpose, language_code)}的語氣，用繁體中文為以下郵件內容生成回信：

【原始郵件】
{email_text}

【回覆郵件創建指南】
- 請包含適當的稱呼和問候語
- 對原始郵件的要點進行完整回應
- 確保回覆內容自然流暢
- 僅創建郵件正文內容（無需主題行）"""

    elif language_code == "en":
        system_prompt = """You are a professional email reply assistant. Please follow these guidelines to create your reply:
1. Create your reply in English only
2. Review the original email content and respond appropriately
3. Start the reply with an appropriate greeting and end with a suitable closing
4. The body of the email should clearly address the content of the original email and include all necessary information
5. Structure the overall reply properly (greeting → body → closing)"""
        
        user_prompt = f"""Please create a {get_tone_description(purpose, language_code)} reply in English for the following email:

[ORIGINAL EMAIL]
{email_text}

[REPLY EMAIL GUIDELINES]
- Include appropriate salutations and greetings
- Address all key points from the original email
- Ensure the response sounds natural and fluent
- Create only the email body (no subject line needed)"""

    elif language_code == "ko":
        system_prompt = """당신은 전문적인 이메일 회신 도우미입니다. 다음 지침에 따라 회신을 작성해 주세요:
1. 반드시 한국어로만 답장을 작성하세요
2. 원본 이메일 내용을 검토하고 적절히 응답하세요
3. 적절한 인사말로 시작하고 적합한 맺음말로 끝내세요
4. 이메일 본문은 원본 이메일 내용을 명확히 다루고 필요한 모든 정보를 포함해야 합니다
5. 전체 답장 구조를 적절히 구성하세요 (인사말 → 본문 → 맺음말)"""
        
        user_prompt = f"""다음 이메일에 대해 {get_tone_description(purpose, language_code)} 톤으로 한국어 답장을 작성해 주세요:

[원본 이메일]
{email_text}

[답장 이메일 작성 지침]
- 적절한 호칭과 인사말을 포함하세요
- 원본 이메일의 모든 주요 사항에 답변하세요
- 응답이 자연스럽고 유창하게 들리도록 하세요
- 이메일 본문만 작성하세요 (제목줄 불필요)"""

    else:
        # デフォルトは日本語
        return create_email_reply_prompt("ja", purpose, email_text)
    
    return system_prompt, user_prompt

@app.route('/generate', methods=['POST'])
def generate_reply():
    try:
        data = request.json
        print(f"📥 リクエスト受信: {data}")  

        email_text = data.get("content", "").strip()
        language_code = data.get("language", "ja")
        purpose = data.get("purpose", "Business") 
        is_regenerate = data.get("isRegenerate", False)  # 再生成フラグを取得

        if not email_text:
            return jsonify({"error": "メールの内容が空です"}), 400

        language_name = get_language_name(language_code)
        
        # 改良された詳細なプロンプトを使用
        system_prompt, user_prompt = create_email_reply_prompt(language_code, purpose, email_text)

        # 再生成の場合、プロンプトに再生成の指示を追加
        if is_regenerate:
            if language_code == "ja":
                user_prompt += "\n\n【再生成の指示】\n前回と異なる表現や構成で新しい返信を作成してください。"
            elif language_code.startswith("zh-CN"):
                user_prompt += "\n\n【重新生成指示】\n请使用与之前不同的表达方式和结构创建一个新的回复。"
            elif language_code.startswith("zh-TW"):
                user_prompt += "\n\n【重新生成指示】\n請使用與之前不同的表達方式和結構創建一個新的回覆。"
            elif language_code == "en":
                user_prompt += "\n\n[REGENERATION INSTRUCTION]\nPlease create a new reply with different expressions and structure from the previous one."
            elif language_code == "ko":
                user_prompt += "\n\n[재생성 지시]\n이전과 다른 표현과 구조로 새로운 답장을 작성해 주세요."
            else:
                user_prompt += "\n\n【再生成の指示】\n前回と異なる表現や構成で新しい返信を作成してください。"
            
            # 温度を少し上げて多様性を確保
            temperature = 0.9
        else:
            temperature = 0.7

        # より新しいモデルを使用してより良い結果を得る
        try:
            # OpenAI APIの新しいクライアントスタイルを試す
            from openai import OpenAI
            client = OpenAI(api_key=OPENAI_API_KEY)
            response = client.chat.completions.create(
                model="gpt-4o",  # より新しいモデルを使用
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                max_tokens=800,  # より長い返信を可能に
                temperature=temperature  # 再生成の場合は温度を上げる
            )
            reply_text = response.choices[0].message.content.strip()
        except ImportError:
            # 従来のスタイルでフォールバック
            response = openai.ChatCompletion.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                max_tokens=800,
                temperature=temperature  # 再生成の場合は温度を上げる
            )
            reply_text = response.choices[0].message.content.strip()

        return jsonify({"email": reply_text})

    except Exception as e:
        print(f"❌ エラー: {str(e)}")  
        return jsonify({"error": f"サーバーエラー: {str(e)}"}), 500

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000, debug=True)