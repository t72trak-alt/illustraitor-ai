// Illustraitor AI Pro - ВЕРСИЯ С УПРАВЛЕНИЕМ API КЛЮЧОМ
console.log("🚀 Illustraitor AI Pro запущен!");
// Хранилище для API ключа
let userApiKey = '';
let apiKeyValid = false;
let apiCredits = 0;
// Ждём загрузки страницы
window.onload = function() {
    console.log("✅ Страница загружена");
    initApp();
};
function initApp() {
    console.log("🔄 Инициализация...");
    // Находим элементы
    const generateBtn = document.getElementById('generateBtn');
    const promptInput = document.getElementById('prompt-input');
    const statusDiv = document.getElementById('status');
    const styleButtons = document.querySelectorAll('.style-btn');
    const batchBtn = document.getElementById('batchBtn');
    const apiKeyInput = document.getElementById('api-key-input');
    const testApiBtn = document.getElementById('testApiBtn');
    const apiKeyHeader = document.getElementById('apiKeyHeader');
    const apiKeyContent = document.getElementById('apiKeyContent');
    const apiStatus = document.getElementById('apiStatus');
    const collapsibleIcon = document.getElementById('collapsibleIcon');
    console.log("📋 Найдены элементы:", {
        generateBtn: generateBtn ? "✅" : "❌",
        promptInput: promptInput ? "✅" : "❌",
        apiKeyInput: apiKeyInput ? "✅" : "❌",
        testApiBtn: testApiBtn ? "✅" : "❌"
    });
    // Загружаем сохранённый API ключ из localStorage
    loadSavedApiKey();
    // Обработчики кнопок стилей
    styleButtons.forEach(btn => {
        btn.addEventListener('click', function() {
            styleButtons.forEach(b => b.classList.remove('active'));
            this.classList.add('active');
            console.log("🎨 Выбран стиль:", this.getAttribute('data-style'));
        });
    });
    // Сворачивание/разворачивание секции API ключа
    apiKeyHeader.addEventListener('click', function() {
        const isHidden = apiKeyContent.style.display === 'none';
        apiKeyContent.style.display = isHidden ? 'block' : 'none';
        collapsibleIcon.classList.toggle('rotated', isHidden);
        if (isHidden) {
            apiKeyInput.focus();
        }
    });
    // Сохранение API ключа при изменении
    apiKeyInput.addEventListener('input', function() {
        userApiKey = this.value.trim();
        saveApiKey();
        updateApiStatus('unknown');
    });
    // Кнопка проверки API ключа
    testApiBtn.addEventListener('click', testApiKey);
    // Пакетная генерация
    if (batchBtn) {
        batchBtn.addEventListener('click', function() {
            const isActive = this.classList.toggle('active');
            this.textContent = isActive 
                ? "Пакетная генерация (ВКЛ)" 
                : "Пакетная генерация (ВЫКЛ)";
            console.log("📦 Пакетный режим:", isActive ? "ВКЛ" : "ВЫКЛ");
        });
    }
    // ОСНОВНОЙ ОБРАБОТЧИК ГЕНЕРАЦИИ
    generateBtn.addEventListener('click', function() {
        console.log("========================================");
        console.log("🟡 КНОПКА 'СГЕНЕРИРОВАТЬ' НАЖАТА!");
        // Получаем данные
        const promptText = promptInput.value.trim();
        const activeStyle = document.querySelector('.style-btn.active');
        const selectedStyle = activeStyle ? activeStyle.getAttribute('data-style') : 'creative';
        console.log("📝 Промпт:", promptText);
        console.log("🎨 Стиль:", selectedStyle);
        console.log("🔑 API ключ:", userApiKey ? "установлен" : "отсутствует");
        if (!promptText) {
            statusDiv.textContent = "❌ Введите описание изображения";
            statusDiv.className = "error";
            return;
        }
        // Меняем состояние
        this.disabled = true;
        this.textContent = "Генерация...";
        statusDiv.textContent = userApiKey 
            ? "🔄 Используем ваш API ключ..." 
            : "🔄 Используем демо-режим (Unsplash)...";
        statusDiv.className = "loading";
        // Подготавливаем данные для отправки
        const requestData = {
            text: promptText,
            style: selectedStyle
        };
        // Добавляем API ключ если есть
        if (userApiKey) {
            requestData.api_key = userApiKey;
        }
        // Отправляем запрос
        fetch("http://127.0.0.1:8000/generate", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify(requestData)
        })
        .then(response => {
            console.log("📥 Ответ сервера, статус:", response.status);
            if (!response.ok) {
                return response.json().then(data => {
                    throw new Error(data.detail || `HTTP ошибка: ${response.status}`);
                });
            }
            return response.json();
        })
        .then(data => {
            console.log("✅ Данные от сервера:", data);
            // Определяем режим
            const mode = data.mode || (userApiKey ? "openai" : "mock");
            const modeText = mode === "openai" ? "OpenAI DALL-E" : 
                            mode.includes("mock") ? "Демо-режим" : mode;
            // Очищаем статус
            statusDiv.innerHTML = "";
            statusDiv.className = "success";
            // Создаём сообщение об успехе
            const successMsg = document.createElement('div');
            successMsg.innerHTML = `
                <strong>✅ Изображение создано!</strong>
                <span class="mode-badge mode-${mode === 'openai' ? 'openai' : 'mock'}">${modeText}</span>
            `;
            successMsg.style.cssText = "margin-bottom: 10px;";
            statusDiv.appendChild(successMsg);
            // Если сервер вернул URL изображения
            if (data.image_url) {
                console.log("🖼️ URL изображения:", data.image_url);
                // Создаём изображение
                const img = document.createElement('img');
                img.src = data.image_url;
                img.alt = "AI иллюстрация";
                img.style.maxWidth = "100%";
                img.style.borderRadius = "8px";
                img.style.marginTop = "10px";
                img.style.border = "2px solid #ddd";
                // Ссылка для открытия
                const link = document.createElement('a');
                link.href = data.image_url;
                link.target = "_blank";
                link.textContent = "🔗 Открыть в новой вкладке";
                link.style.display = "block";
                link.style.marginTop = "10px";
                link.style.color = "#667eea";
                link.style.textDecoration = "none";
                link.style.fontWeight = "bold";
                // Информация о генерации
                const infoDiv = document.createElement('div');
                infoDiv.style.fontSize = "12px";
                infoDiv.style.color = "#666";
                infoDiv.style.marginTop = "10px";
                infoDiv.innerHTML = `
                    <div><strong>Промпт:</strong> ${data.text}</div>
                    <div><strong>Стиль:</strong> ${data.style_name || data.style}</div>
                    ${data.credits_used ? `<div><strong>Кредиты:</strong> ${data.credits_used} использовано</div>` : ''}
                `;
                statusDiv.appendChild(img);
                statusDiv.appendChild(link);
                statusDiv.appendChild(infoDiv);
            } else {
                // Нет изображения в ответе
                const errorMsg = document.createElement('div');
                errorMsg.textContent = "⚠️ Сервер не вернул изображение";
                errorMsg.style.color = "orange";
                statusDiv.appendChild(errorMsg);
            }
        })
        .catch(error => {
            console.error("❌ Ошибка:", error);
            statusDiv.textContent = "❌ Ошибка: " + error.message;
            statusDiv.className = "error";
            if (error.message.includes("Failed to fetch")) {
                statusDiv.textContent = "❌ Не могу подключиться к серверу. Убедитесь, что сервер запущен на http://127.0.0.1:8000";
            } else if (error.message.includes("Недостаточно кредитов")) {
                statusDiv.innerHTML = "❌ Недостаточно кредитов. <a href='#' id='checkCreditsLink'>Проверить баланс</a>";
                const checkLink = document.getElementById('checkCreditsLink');
                if (checkLink) {
                    checkLink.addEventListener('click', function(e) {
                        e.preventDefault();
                        checkCredits();
                    });
                }
            }
        })
        .finally(() => {
            // Восстанавливаем кнопку
            this.disabled = false;
            this.textContent = "Сгенерировать иллюстрацию";
            console.log("🔄 Кнопка восстановлена");
        });
    });
    console.log("🎯 Приложение инициализировано! Готово к работе.");
}
// Функция проверки API ключа
function testApiKey() {
    const apiKeyInput = document.getElementById('api-key-input');
    const testApiBtn = document.getElementById('testApiBtn');
    const apiKey = apiKeyInput.value.trim();
    if (!apiKey) {
        updateApiStatus('unknown', 'Введите API ключ');
        return;
    }
    testApiBtn.disabled = true;
    testApiBtn.textContent = "Проверяем...";
    updateApiStatus('unknown', 'Проверка...');
    fetch(`http://127.0.0.1:8000/credits/${apiKey}`)
        .then(response => {
            if (!response.ok) {
                throw new Error('Неверный API ключ');
            }
            return response.json();
        })
        .then(data => {
            apiKeyValid = true;
            apiCredits = data.credits;
            updateApiStatus('valid', `✅ Ключ активен (${data.credits} кредитов)`);
            console.log("✅ API ключ проверен, кредиты:", data.credits);
        })
        .catch(error => {
            apiKeyValid = false;
            updateApiStatus('invalid', '❌ Неверный API ключ');
            console.error("❌ Ошибка проверки API ключа:", error);
        })
        .finally(() => {
            testApiBtn.disabled = false;
            testApiBtn.textContent = "🔍 Проверить ключ";
        });
}
// Функция проверки баланса кредитов
function checkCredits() {
    if (!userApiKey) {
        alert("Введите API ключ для проверки баланса");
        return;
    }
    fetch(`http://127.0.0.1:8000/credits/${userApiKey}`)
        .then(response => {
            if (!response.ok) throw new Error('Ошибка проверки баланса');
            return response.json();
        })
        .then(data => {
            alert(`Баланс: ${data.credits} кредитов\nПользователь: ${data.name}`);
        })
        .catch(error => {
            alert("Не удалось проверить баланс: " + error.message);
        });
}
// Обновление статуса API ключа
function updateApiStatus(status, message = '') {
    const apiStatus = document.getElementById('apiStatus');
    const apiKeyLabel = document.getElementById('apiKeyLabel');
    apiStatus.className = 'api-status ' + status;
    if (message) {
        apiKeyLabel.textContent = message;
    } else {
        switch(status) {
            case 'valid':
                apiKeyLabel.textContent = `API ключ активен (${apiCredits} кредитов)`;
                break;
            case 'invalid':
                apiKeyLabel.textContent = 'API ключ неверный';
                break;
            default:
                apiKeyLabel.textContent = userApiKey 
                    ? 'API ключ установлен (не проверен)' 
                    : 'API ключ не установлен (демо-режим)';
        }
    }
}
// Сохранение API ключа в localStorage
function saveApiKey() {
    try {
        localStorage.setItem('illustraitor_api_key', userApiKey);
        console.log("💾 API ключ сохранён в localStorage");
    } catch (e) {
        console.error("❌ Ошибка сохранения API ключа:", e);
    }
}
// Загрузка API ключа из localStorage
function loadSavedApiKey() {
    try {
        const savedKey = localStorage.getItem('illustraitor_api_key');
        if (savedKey) {
            userApiKey = savedKey;
            const apiKeyInput = document.getElementById('api-key-input');
            if (apiKeyInput) {
                apiKeyInput.value = savedKey;
            }
            console.log("📂 API ключ загружен из localStorage");
            updateApiStatus('unknown');
            // Автоматически проверяем ключ если он похож на валидный
            if (savedKey.startsWith('ilust_') || savedKey.startsWith('sk-')) {
                setTimeout(testApiKey, 1000);
            }
        }
    } catch (e) {
        console.error("❌ Ошибка загрузки API ключа:", e);
    }
}
