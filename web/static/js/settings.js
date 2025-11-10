// 設定ページのスクリプト

const apiKeyInput = document.getElementById('apiKey');
const saveApiKeyBtn = document.getElementById('saveApiKeyBtn');
const saveSuccess = document.getElementById('saveSuccess');
const saveError = document.getElementById('saveError');
const saveErrorText = document.getElementById('saveErrorText');

// イベントリスナー
saveApiKeyBtn.addEventListener('click', saveApiKey);

// APIキー保存
async function saveApiKey() {
    const apiKey = apiKeyInput.value.trim();

    if (!apiKey) {
        showSaveError('APIキーを入力してください');
        return;
    }

    if (!apiKey.startsWith('sk-')) {
        showSaveError('有効なAPIキーを入力してください（sk-で始まる必要があります）');
        return;
    }

    try {
        saveApiKeyBtn.disabled = true;
        saveApiKeyBtn.textContent = '保存中...';

        hideElement('saveSuccess');
        hideElement('saveError');

        const result = await apiRequest('/api/save-api-key', 'POST', { api_key: apiKey });

        if (result.success) {
            showElement('saveSuccess');
            apiKeyInput.value = '';

            // 3秒後にメインページへリダイレクト
            setTimeout(() => {
                window.location.href = '/';
            }, 2000);
        }
    } catch (error) {
        showSaveError(error.message);
    } finally {
        saveApiKeyBtn.disabled = false;
        saveApiKeyBtn.textContent = 'APIキーを保存';
    }
}

function showSaveError(message) {
    saveErrorText.textContent = message;
    showElement('saveError');
    hideElement('saveSuccess');
}
