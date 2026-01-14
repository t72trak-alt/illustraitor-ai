// ==================== УПРАВЛЕНИЕ API КЛЮЧОМ ====================

// Загружаем сохранённый API ключ
async function loadApiKey() {
    const result = await chrome.storage.local.get(['openai_api_key']);
    if (result.openai_api_key) {
        const apiKeyInput = document.getElementById('api-key');
        const maskedKey = maskApiKey(result.openai_api_key);
        apiKeyInput.value = maskedKey;
        apiKeyInput.setAttribute('data-full-key', result.openai_api_key);
        updateStatus('✅ API ключ загружен');
    }
}

// Маскируем ключ для безопасности
function maskApiKey(apiKey) {
    if (!apiKey) return '';
    if (apiKey.length <= 8) return '•'.repeat(apiKey.length);
    
    // Показываем первые 3 и последние 4 символа
    const visibleStart = apiKey.substring(0, 3);
    const visibleEnd = apiKey.substring(apiKey.length - 4);
    const maskedLength = apiKey.length - 7;
    
    return visibleStart + '•'.repeat(maskedLength) + visibleEnd;
}

// Сохраняем API ключ
document.getElementById('save-key').addEventListener('click', async function() {
    const apiKeyInput = document.getElementById('api-key');
    let apiKey = apiKeyInput.value.trim();
    
    // Если поле содержит маскированный ключ, используем сохранённый
    if (apiKey.includes('•') && apiKeyInput.getAttribute('data-full-key')) {
        apiKey = apiKeyInput.getAttribute('data-full-key');
    }
    
    if (!apiKey) {
        updateStatus('⚠️ Введите API ключ');
        apiKeyInput.focus();
        return;
    }
    
    // Проверяем формат ключа
    if (!apiKey.startsWith('sk-') && !apiKey.startsWith('sk-proj-')) {
        updateStatus('❌ Неверный формат ключа. Должен начинаться с sk-');
        return;
    }
    
    await chrome.storage.local.set({ openai_api_key: apiKey });
    
    // Маскируем для отображения
    apiKeyInput.value = maskApiKey(apiKey);
    apiKeyInput.setAttribute('data-full-key', apiKey);
    
    updateStatus('✅ API ключ сохранён');
    
    // Показываем уведомление на 2 секунды
    const saveBtn = this;
    const originalText = saveBtn.textContent;
    saveBtn.textContent = '✅ Сохранено!';
    saveBtn.style.background = '#20c997';
    
    setTimeout(() => {
        saveBtn.textContent = originalText;
        saveBtn.style.background = '#28a745';
    }, 2000);
});

// Удаляем API ключ
document.getElementById('clear-key').addEventListener('click', async function() {
    await chrome.storage.local.remove(['openai_api_key']);
    document.getElementById('api-key').value = '';
    document.getElementById('api-key').removeAttribute('data-full-key');
    updateStatus('🗑️ API ключ удалён');
    
    // Показываем уведомление
    const clearBtn = this;
    const originalText = clearBtn.textContent;
    clearBtn.textContent = '✅ Удалено!';
    
    setTimeout(() => {
        clearBtn.textContent = originalText;
    }, 2000);
});

// Показываем полный ключ при фокусе
document.getElementById('api-key').addEventListener('focus', function() {
    const fullKey = this.getAttribute('data-full-key');
    if (fullKey && this.value.includes('•')) {
        this.value = fullKey;
    }
});

// Маскируем ключ при потере фокуса
document.getElementById('api-key').addEventListener('blur', function() {
    const fullKey = this.getAttribute('data-full-key');
    if (fullKey && !this.value.includes('•')) {
        this.value = maskApiKey(fullKey);
    }
});

// ==================== МОДИФИЦИРОВАННАЯ ФУНКЦИЯ ГЕНЕРАЦИИ ====================

async function generateImage() {
    const prompt = document.getElementById('prompt').value.trim();
    const style = document.getElementById('style').value;
    
    if (!prompt) {
        updateStatus('⚠️ Введите описание изображения');
        document.getElementById('prompt').focus();
        return;
    }
    
    updateStatus('⏳ Генерирую изображение...');
    
    // Получаем API ключ пользователя
    const result = await chrome.storage.local.get(['openai_api_key']);
    let userApiKey = result.openai_api_key || null;
    
    // Если ключ замаскирован, используем сохранённый
    const apiKeyInput = document.getElementById('api-key');
    if (apiKeyInput.getAttribute('data-full-key') && !userApiKey) {
        userApiKey = apiKeyInput.getAttribute('data-full-key');
    }
    
    const requestBody = {
        text: prompt,
        style: style,
        api_key: userApiKey  // Отправляем ключ пользователя или null
    };
    
    try {
                const response = await fetch('https://illustraitor-ai-v2.onrender.com/generate', {
            method: 'POST',
            mode: 'cors',
            headers: {
                'Content-Type': 'application/json',
                'Accept': 'application/json'
            },
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(requestBody)
        });
        
        if (!response.ok) {
            throw new Error(`Ошибка сервера: ${response.status}`);
        }
        
        const data = await response.json();
        
        if (data.status === 'success') {
            // Показываем изображение
            const resultImage = document.getElementById('result-image');
            resultImage.src = data.image_url;
            resultImage.style.display = 'block';
            
            // Обновляем статус с информацией о режиме
            const modeText = data.mode === 'openai' 
                ? 'AI-генерация (DALL-E 3)' 
                : 'Демо-режим (стоковые изображения)';
            
            const keySource = data.uses_user_key 
                ? 'ваш API ключ' 
                : 'серверный ключ';
            
            updateStatus(`✅ Изображение сгенерировано в стиле "${data.style_name}" (${modeText}, ${keySource})`);
            
            // Кнопка скачивания
            document.getElementById('download-btn').onclick = function() {
                chrome.downloads.download({
                    url: data.image_url,
                    filename: `illustraitor_${Date.now()}.png`
                });
            };
            document.getElementById('download-btn').style.display = 'block';
            
        } else {
            updateStatus(`❌ Ошибка сервера: ${data.message}`);
        }
        
    } catch (error) {
        console.error('Ошибка генерации:', error);
        updateStatus(`❌ Ошибка подключения к серверу Render`);
    }
}

// ==================== ИНИЦИАЛИЗАЦИЯ ====================

// Загружаем API ключ при открытии попапа
document.addEventListener('DOMContentLoaded', function() {
    loadApiKey();
    document.getElementById('generate-btn').addEventListener('click', generateImage);
    
    // Добавляем хоткей Ctrl+Enter для генерации
    document.getElementById('prompt').addEventListener('keydown', function(e) {
        if (e.ctrlKey && e.key === 'Enter') {
            generateImage();
        }
    });
});




