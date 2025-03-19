// 返信を生成
document.addEventListener("DOMContentLoaded", function () {
    const generateBtn = document.getElementById("generateBtn");
    const responseText = document.getElementById("responseText");
    const inputEmail = document.getElementById("inputEmail");
    const languageSelect = document.getElementById("language");
    const purposeSelect = document.getElementById("purpose");
    const toneSelect = document.getElementById("tone");
    const copyBtn = document.getElementById("copyBtn");
    const retryBtn = document.getElementById("retryBtn");
    const errorBox = document.getElementById("errorBox");
    const errorText = document.getElementById("errorText");

    generateBtn.addEventListener("click", async () => {
        const emailContent = inputEmail.value.trim();
        const selectedLanguage = languageSelect.value;
        const selectedPurpose = purposeSelect.value;
        const selectedTone = toneSelect.value;

        if (!emailContent) {
            alert("メール内容を入力してください！");
            return;
        }

        // エラーや成功メッセージをクリア
        responseText.textContent = "返信を生成中...";
        errorBox.style.display = "none"; 
        generateBtn.disabled = true; // 複数回のクリックを防止

        try {
            console.log("📤 リクエスト送信:", {
                purpose: selectedPurpose,
                tone: selectedTone,
                language: selectedLanguage,
                content: emailContent
            });

            const response = await fetch("http://127.0.0.1:5000/generate", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({
                    purpose: selectedPurpose,
                    tone: selectedTone,
                    language: selectedLanguage,
                    content: emailContent,
                }),
            });

            console.log("🔄 サーバーの応答:", response);

            if (!response.ok) {
                const errorData = await response.json();
                errorText.textContent = errorData.error || "生成に失敗しました。";
                errorBox.style.display = "block";
                throw new Error(errorText.textContent);
            }

            // JSONの解析が成功しているか確認
            const responseData = await response.json();
            console.log("✅ 解析後のレスポンス:", responseData);

            responseText.textContent = responseData.email || "エラーが発生しました。";
        } catch (error) {
            console.error("❌ Fetch エラー:", error);
            errorText.textContent = "エラー：" + error.message;
            errorBox.style.display = "block";
        } finally {
            generateBtn.disabled = false; // ボタンを再度有効化
        }
    });

    copyBtn.addEventListener("click", function () {
        navigator.clipboard.writeText(responseText.textContent)
            .then(() => alert("コピーしました！"))
            .catch(err => console.error("コピー失敗:", err));
    });

    retryBtn.addEventListener("click", function () {
        responseText.textContent = "生成された返信はここに表示されます";
        errorBox.style.display = "none";
    });
});
