// Generate Reply
document.addEventListener("DOMContentLoaded", function () {
    const generateBtn = document.getElementById("generateBtn");
    const responseText = document.getElementById("responseText");
    const inputEmail = document.getElementById("inputEmail");
    const languageSelect = document.getElementById("language");
    const purposeSelect = document.getElementById("purpose");
    const copyBtn = document.getElementById("copyBtn");
    const retryBtn = document.getElementById("retryBtn");
    const errorBox = document.getElementById("errorBox");
    const errorText = document.getElementById("errorText");

    generateBtn.addEventListener("click", async () => {
        const emailContent = inputEmail.value.trim();
        const selectedLanguage = languageSelect.value;
        const selectedPurpose = purposeSelect.value;

        if (!emailContent) {
            alert("メール内容を入力してください！");
            return;
        }

        // メッセージ初期化
        responseText.textContent = "返信を生成中...";
        errorBox.style.display = "none";
        generateBtn.disabled = true;

        try {
            console.log("📤 発送データ:", {
                purpose: selectedPurpose,
                language: selectedLanguage,
                content: emailContent
            });

            const response = await fetch("http://127.0.0.1:5000/generate", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({
                    purpose: selectedPurpose,
                    language: selectedLanguage,
                    content: emailContent,
                }),
            });

            console.log("🔄 サーバー応答:", response);

            if (!response.ok) {
                const errorData = await response.json();
                errorText.textContent = errorData.error || "生成に失敗しました。";
                errorBox.style.display = "block";
                throw new Error(errorText.textContent);
            }

            const responseData = await response.json();
            console.log("✅ 受信内容:", responseData);

            responseText.textContent = responseData.email || "エラーが発生しました。";
        } catch (error) {
            console.error("❌ Fetch エラー:", error);
            errorText.textContent = "エラー：" + error.message;
            errorBox.style.display = "block";
        } finally {
            generateBtn.disabled = false;
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
