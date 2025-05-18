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

    // 最後に使用したパラメータを保存する変数
    let lastEmailContent = "";
    let lastSelectedLanguage = "";
    let lastSelectedPurpose = "";

    // メール生成関数
    async function generateEmail(isRegenerate = false) {
        const emailContent = isRegenerate ? lastEmailContent : inputEmail.value.trim();
        const selectedLanguage = isRegenerate ? lastSelectedLanguage : languageSelect.value;
        const selectedPurpose = isRegenerate ? lastSelectedPurpose : purposeSelect.value;

        // 再生成でない場合は、現在の値を保存
        if (!isRegenerate) {
            lastEmailContent = emailContent;
            lastSelectedLanguage = selectedLanguage;
            lastSelectedPurpose = selectedPurpose;
        }

        if (!emailContent) {
            alert("メール内容を入力してください！");
            return;
        }

        // メッセージ初期化
        responseText.textContent = isRegenerate ? "返信を再生成中..." : "返信を生成中...";
        errorBox.style.display = "none";
        generateBtn.disabled = true;
        retryBtn.disabled = true; // 再生成ボタンも無効化

        try {
            console.log("📤 発送データ:", {
                purpose: selectedPurpose,
                language: selectedLanguage,
                content: emailContent,
                isRegenerate: isRegenerate // 再生成フラグを追加
            });

            const response = await fetch("http://127.0.0.1:5000/generate", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({
                    purpose: selectedPurpose,
                    language: selectedLanguage,
                    content: emailContent,
                    isRegenerate: isRegenerate // 再生成フラグを追加
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
            retryBtn.disabled = false; // 再生成ボタンを再度有効化
        }
    }

    // 生成ボタンのイベントリスナー
    generateBtn.addEventListener("click", () => generateEmail(false));

    // 再生成ボタンのイベントリスナー
    retryBtn.addEventListener("click", function () {
        // 以前の生成結果がある場合のみ再生成を実行
        if (lastEmailContent) {
            generateEmail(true);
        } else {
            responseText.textContent = "生成された返信はここに表示されます";
            errorBox.style.display = "none";
        }
    });

    copyBtn.addEventListener("click", function () {
        navigator.clipboard.writeText(responseText.textContent)
            .then(() => alert("コピーしました！"))
            .catch(err => console.error("コピー失敗:", err));
    });
});