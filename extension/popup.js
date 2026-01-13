import CONFIG from './config.js';
document.addEventListener('DOMContentLoaded', async () => {
    const API_URL = CONFIG.API_URL;
    // Элементы интерфейса
    const promptInput = document.getElementById('prompt');
    const styleSelect = document.getElementById('style');
    const generateBtn = document.getElementById('generate');
    const statusDiv = document.getElementById('status');
    const resultDiv = document.getElementById('result');
    const imageResult = document.getElementById('imageResult');
    const downloadLink = document.getElementById('downloadLink');
    // Функция для выполнения fetch с таймаутом
    async function fetchWithTimeout(url, options = {}) {
        const timeout = CONFIG.TIMEOUT;
        const controller = new AbortController();
        const timeoutId = setTimeout(() => controller.abort(), timeout);
        try {
            const response = await fetch(url, {
                ...options,
                signal: controller.signal
            });
            clearTimeout(timeoutId);
            return response;
        } catch (error) {
            clearTimeout(timeoutId);
            throw error;
        }
    }
    // Загружаем стили
    async function loadStyles() {
        try {
            statusDiv.textContent = 'Загружаю стили...';
            statusDiv.style.color = 'blue';
            const response = await fetchWithTimeout(\\\\);
            if (!response.ok) {
                throw new Error(\Ошибка загрузки стилей: \\);
            }
            const data = await response.json();
            // Очищаем select
            styleSelect.innerHTML = '<option value="">Выберите стиль</option>';
            // Добавляем стили
            data.styles.forEach(style => {
                const option = document.createElement('option');
                option.value = style.id;
                option.textContent = \\\;
                option.title = style.description; // подсказка при наведении
                styleSelect.appendChild(option);
            });
            statusDiv.textContent = \Загружено \ стилей\;
            statusDiv.style.color = 'green';
        } catch (error) {
            if (error.name === 'AbortError') {
                statusDiv.textContent = 'Таймаут загрузки стилей. Попробуйте снова.';
            } else {
                statusDiv.textContent = \Ошибка: \\;
            }
            statusDiv.style.color = 'red';
            console.error('Ошибка загрузки стилей:', error);
        }
    }
    // Генерация изображения
    async function generateImage() {
        const prompt = promptInput.value.trim();
        const style = styleSelect.value;
        if (!prompt) {
            statusDiv.textContent = 'Введите описание изображения';
            statusDiv.style.color = 'red';
            return;
        }
        if (!style) {
            statusDiv.textContent = 'Выберите стиль';
            statusDiv.style.color = 'red';
            return;
        }
        try {
            statusDiv.textContent = 'Генерирую изображение...';
            statusDiv.style.color = 'blue';
            generateBtn.disabled = true;
            const response = await fetchWithTimeout(\\\\, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    text: prompt,
                    style: style
                })
            });
            if (!response.ok) {
                throw new Error(\Ошибка генерации: \\);
            }
            const data = await response.json();
            // Обновляем статус
            if (data.mode === 'demo') {
                statusDiv.textContent = \Демо-режим: \\;
                statusDiv.style.color = 'orange';
            } else if (data.mode === 'openai') {
                statusDiv.textContent = 'Изображение сгенерировано AI!';
                statusDiv.style.color = 'green';
            } else {
                statusDiv.textContent = 'Изображение сгенерировано!';
                statusDiv.style.color = 'green';
            }
            // Показываем результат
            resultDiv.style.display = 'block';
            if (data.image_url) {
                imageResult.src = data.image_url;
                imageResult.style.display = 'block';
                // Добавляем ссылку для скачивания
                downloadLink.href = data.image_url;
                downloadLink.style.display = 'inline-block';
            }
            // Показываем сообщение если есть
            if (data.message) {
                const messageDiv = document.createElement('div');
                messageDiv.textContent = data.message;
                messageDiv.style.marginTop = '10px';
                messageDiv.style.fontStyle = 'italic';
                messageDiv.style.color = '#666';
                resultDiv.appendChild(messageDiv);
            }
        } catch (error) {
            if (error.name === 'AbortError') {
                statusDiv.textContent = 'Таймаут генерации. Сервер может быть в спящем режиме.';
            } else {
                statusDiv.textContent = \Ошибка: \\;
            }
            statusDiv.style.color = 'red';
            console.error('Ошибка генерации:', error);
        } finally {
            generateBtn.disabled = false;
        }
    }
    // Инициализация
    await loadStyles();
    // Обработчики событий
    generateBtn.addEventListener('click', generateImage);
    // Enter для генерации
    promptInput.addEventListener('keypress', (e) => {
        if (e.key === 'Enter') {
            generateImage();
        }
    });
    // Сброс результата при изменении промпта
    promptInput.addEventListener('input', () => {
        resultDiv.style.display = 'none';
        imageResult.style.display = 'none';
        downloadLink.style.display = 'none';
    });
    // Сброс результата при изменении стиля
    styleSelect.addEventListener('change', () => {
        resultDiv.style.display = 'none';
        imageResult.style.display = 'none';
        downloadLink.style.display = 'none';
    });
});
