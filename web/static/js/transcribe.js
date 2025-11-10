// 文字起こしページのスクリプト

let uploadedFile = null;
let uploadedFilePath = null;

// DOM要素
const uploadArea = document.getElementById('uploadArea');
const fileInput = document.getElementById('fileInput');
const fileInfo = document.getElementById('fileInfo');
const optionsCard = document.getElementById('optionsCard');
const transcribeCard = document.getElementById('transcribeCard');
const progressCard = document.getElementById('progressCard');
const resultCard = document.getElementById('resultCard');
const errorCard = document.getElementById('errorCard');

const transcribeBtn = document.getElementById('transcribeBtn');
const downloadBtn = document.getElementById('downloadBtn');
const newTranscriptionBtn = document.getElementById('newTranscriptionBtn');
const retryBtn = document.getElementById('retryBtn');

const usePreprocessing = document.getElementById('usePreprocessing');
const preprocessingOptions = document.getElementById('preprocessingOptions');

let outputFilename = null;

// イベントリスナー
uploadArea.addEventListener('click', () => fileInput.click());
uploadArea.addEventListener('dragover', handleDragOver);
uploadArea.addEventListener('dragleave', handleDragLeave);
uploadArea.addEventListener('drop', handleDrop);
fileInput.addEventListener('change', handleFileSelect);

transcribeBtn.addEventListener('click', startTranscription);
downloadBtn.addEventListener('click', downloadResult);
newTranscriptionBtn.addEventListener('click', resetForm);
retryBtn.addEventListener('click', resetError);

usePreprocessing.addEventListener('change', function() {
    preprocessingOptions.style.display = this.checked ? 'block' : 'none';
});

// ドラッグ&ドロップ処理
function handleDragOver(e) {
    e.preventDefault();
    uploadArea.classList.add('drag-over');
}

function handleDragLeave(e) {
    e.preventDefault();
    uploadArea.classList.remove('drag-over');
}

function handleDrop(e) {
    e.preventDefault();
    uploadArea.classList.remove('drag-over');

    const files = e.dataTransfer.files;
    if (files.length > 0) {
        uploadFile(files[0]);
    }
}

function handleFileSelect(e) {
    const files = e.target.files;
    if (files.length > 0) {
        uploadFile(files[0]);
    }
}

// ファイルアップロード
async function uploadFile(file) {
    uploadedFile = file;

    const formData = new FormData();
    formData.append('file', file);

    try {
        hideElement('errorCard');
        uploadArea.style.opacity = '0.5';

        const result = await apiRequest('/api/upload', 'POST', formData);

        if (result.success) {
            uploadedFilePath = result.filepath;
            displayFileInfo(result.audio_info, file.name);
            showElement('optionsCard');
            showElement('transcribeCard');
        }
    } catch (error) {
        showError(error.message);
    } finally {
        uploadArea.style.opacity = '1';
    }
}

function displayFileInfo(audioInfo, filename) {
    document.getElementById('fileName').textContent = filename;
    document.getElementById('duration').textContent = formatDuration(audioInfo.duration_seconds);
    document.getElementById('sampleRate').textContent = audioInfo.frame_rate + ' Hz';
    document.getElementById('fileSize').textContent = formatFileSize(audioInfo.file_size_mb * 1024 * 1024);

    showElement('fileInfo');
}

// 文字起こし実行
async function startTranscription() {
    if (!uploadedFilePath) {
        alert('ファイルをアップロードしてください');
        return;
    }

    // オプションの取得
    const options = {
        filepath: uploadedFilePath,
        language: document.getElementById('language').value || null,
        format: document.getElementById('format').value,
        use_preprocessing: document.getElementById('usePreprocessing').checked,
        use_noise_reduction: document.getElementById('useNoiseReduction').checked,
        use_normalization: document.getElementById('useNormalization').checked,
        context: document.getElementById('context').value || null,
        terminology: document.getElementById('terminology').value || null,
        speaker: document.getElementById('speaker').value || null
    };

    try {
        // UI更新
        hideElement('transcribeCard');
        hideElement('errorCard');
        hideElement('resultCard');
        showElement('progressCard');

        // APIリクエスト
        const result = await apiRequest('/api/transcribe', 'POST', options);

        if (result.success) {
            outputFilename = result.output_filename;
            displayResult(result.preview);
        }
    } catch (error) {
        showError(error.message);
    } finally {
        hideElement('progressCard');
    }
}

function displayResult(preview) {
    if (preview) {
        document.getElementById('previewText').textContent = preview;
        document.getElementById('previewSection').style.display = 'block';
    } else {
        document.getElementById('previewSection').style.display = 'none';
    }

    showElement('resultCard');
}

// 結果のダウンロード
function downloadResult() {
    if (outputFilename) {
        window.location.href = `/api/download/${outputFilename}`;
    }
}

// フォームのリセット
async function resetForm() {
    // アップロードファイルのクリーンアップ
    if (uploadedFilePath) {
        try {
            await apiRequest('/api/cleanup', 'POST', { filepath: uploadedFilePath });
        } catch (error) {
            console.error('クリーンアップエラー:', error);
        }
    }

    // 変数のリセット
    uploadedFile = null;
    uploadedFilePath = null;
    outputFilename = null;

    // フォームのリセット
    fileInput.value = '';
    document.getElementById('language').value = 'ja';
    document.getElementById('format').value = 'txt';
    document.getElementById('usePreprocessing').checked = true;
    document.getElementById('useNoiseReduction').checked = true;
    document.getElementById('useNormalization').checked = true;
    document.getElementById('context').value = '';
    document.getElementById('terminology').value = '';
    document.getElementById('speaker').value = '';

    // UI更新
    hideElement('fileInfo');
    hideElement('optionsCard');
    hideElement('transcribeCard');
    hideElement('resultCard');
    hideElement('errorCard');
}

function resetError() {
    hideElement('errorCard');
    showElement('transcribeCard');
}

function showError(message) {
    document.getElementById('errorText').textContent = message;
    showElement('errorCard');
    hideElement('progressCard');
}
