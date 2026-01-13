document.addEventListener('DOMContentLoaded', function() {
    // Элементы
    const userInfo = document.getElementById('userInfo');
    const creditsDisplay = document.getElementById('creditsDisplay');
    const apiKeyDisplay = document.getElementById('apiKey');
    const copyApiKeyBtn = document.getElementById('copyApiKeyBtn');
    const registerBtn = document.getElementById('registerBtn');
    const buyCreditsBtn = document.getElementById('buyCreditsBtn');
    const saveSettingsBtn = document.getElementById('saveSettingsBtn');
    const resetBtn = document.getElementById('resetBtn');
    const viewHistoryBtn = document.getElementById('viewHistoryBtn');
    const apiEndpointInput = document.getElementById('apiEndpoint');
    const defaultStyleSelect = document.getElementById('defaultStyle');
    const plans = document.querySelectorAll('.plan');
    // Текущий выбранный план
    let selectedPlan = null;
    // Загружаем настройки
    loadSettings();
    loadUserInfo();
    loadStyles();
    // Обработчики планов
    plans.forEach(plan => {
        plan.addEventListener('click', function() {
            plans.forEach(p => p.classList.remove('selected'));
            this.classList.add('selected');
            selectedPlan = {
                credits: parseInt(this.dataset.credits),
                price: parseFloat(this.dataset.price)
            };
            buyCreditsBtn.disabled = false;
            buyCreditsBtn.textContent = \`Купить (\${selectedPlan.price > 0 ? '$' + selectedPlan.price : 'Бесплатно'})\`;
        });
    });
    // Копирование API ключа
    copyApiKeyBtn.addEventListener('click', function() {
        const apiKey = apiKeyDisplay.textContent;
        if (apiKey && apiKey !== 'Не зарегистрирован') {
            navigator.clipboard.writeText(apiKey).then(() => {
                const originalText = this.textContent;
                this.textContent = '✅ Скопировано!';
                setTimeout(() => {
                    this.textContent = originalText;
                }, 2000);
            });
        }
    });
    // Регистрация
    registerBtn.addEventListener('click', async function() {
        const email = prompt('Введите ваш email:');
        if (!email) return;
        const name = prompt('Введите ваше имя:') || 'Пользователь';
        try {
            const response = await fetch(\`\${getApiEndpoint()}/register\`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ email, name })
            });
            const data = await response.json();
            if (data.api_key) {
                // Сохраняем данные
                chrome.storage.local.set({
                    userApiKey: data.api_key,
                    userEmail: email,
                    userName: name,
                    userCredits: data.credits,
                    userId: data.user_id
                });
                // Обновляем UI
                loadUserInfo();
                alert('✅ Регистрация успешна! Ваш API ключ сохранен.');
            }
        } catch (error) {
            console.error('Ошибка регистрации:', error);
            alert('❌ Ошибка регистрации: ' + error.message);
        }
    });
    // Покупка кредитов
    buyCreditsBtn.addEventListener('click', function() {
        if (!selectedPlan) {
            alert('Выберите пакет кредитов');
            return;
        }
        if (selectedPlan.price > 0) {
            alert(\`В демо-версии покупка кредитов не реализована. В реальной версии здесь будет переход к оплате.\`);
        } else {
            // Бесплатные кредиты
            addCredits(selectedPlan.credits);
            alert(\`🎁 Вам начислено \${selectedPlan.credits} бесплатных кредитов!\`);
        }
    });
    // Сохранение настроек
    saveSettingsBtn.addEventListener('click', function() {
        const settings = {
            apiEndpoint: apiEndpointInput.value,
            defaultStyle: defaultStyleSelect.value
        };
        chrome.storage.local.set({ settings }, () => {
            const originalText = this.textContent;
            this.textContent = '✅ Сохранено!';
            setTimeout(() => {
                this.textContent = originalText;
            }, 2000);
        });
    });
    // Сброс
    resetBtn.addEventListener('click', function() {
        if (confirm('Вы уверены? Это удалит все ваши настройки и историю.')) {
            chrome.storage.local.clear(() => {
                alert('Настройки сброшены');
                location.reload();
            });
        }
    });
    // Просмотр истории
    viewHistoryBtn.addEventListener('click', function() {
        alert('В демо-версии история не реализована. В реальной версии здесь будет отображение истории генераций.');
    });
    // Функции
    function getApiEndpoint() {
        return apiEndpointInput.value || 'http://127.0.0.1:8000';
    }
    async function loadUserInfo() {
        chrome.storage.local.get(['userApiKey', 'userEmail', 'userName', 'userCredits'], async (data) => {
            if (data.userApiKey) {
                apiKeyDisplay.textContent = data.userApiKey;
                userInfo.innerHTML = \`
                    <p><strong>Email:</strong> \${data.userEmail || 'Не указан'}</p>
                    <p><strong>Имя:</strong> \${data.userName || 'Не указано'}</p>
                \`;
                // Загружаем актуальные кредиты с сервера
                try {
                    const response = await fetch(\`\${getApiEndpoint()}/credits/\${data.userApiKey}\`);
                    if (response.ok) {
                        const creditsData = await response.json();
                        creditsDisplay.textContent = \`\${creditsData.credits} кредитов\`;
                        // Обновляем локальное хранилище
                        chrome.storage.local.set({ userCredits: creditsData.credits });
                    }
                } catch (error) {
                    console.error('Ошибка загрузки кредитов:', error);
                    creditsDisplay.textContent = \`\${data.userCredits || 0} кредитов (офлайн)\`;
                }
            } else {
                userInfo.innerHTML = '<p>Вы не зарегистрированы</p>';
                creditsDisplay.textContent = '0 кредитов';
                apiKeyDisplay.textContent = 'Не зарегистрирован';
            }
        });
    }
    function loadSettings() {
        chrome.storage.local.get(['settings'], (data) => {
            if (data.settings) {
                apiEndpointInput.value = data.settings.apiEndpoint || 'http://127.0.0.1:8000';
                if (data.settings.defaultStyle && defaultStyleSelect.options.length > 0) {
                    defaultStyleSelect.value = data.settings.defaultStyle;
                }
            }
        });
    }
    async function loadStyles() {
        try {
            const response = await fetch(\`\${getApiEndpoint()}/styles\`);
            const data = await response.json();
            defaultStyleSelect.innerHTML = '';
            data.styles.forEach(style => {
                const option = document.createElement('option');
                option.value = style.id;
                option.textContent = \`\${style.name} (\${style.credits_cost} кредит\${style.credits_cost > 1 ? 'а' : ''})\`;
                defaultStyleSelect.appendChild(option);
            });
            // Устанавливаем сохраненный стиль
            chrome.storage.local.get(['settings'], (storage) => {
                if (storage.settings?.defaultStyle) {
                    defaultStyleSelect.value = storage.settings.defaultStyle;
                }
            });
        } catch (error) {
            console.error('Ошибка загрузки стилей:', error);
            defaultStyleSelect.innerHTML = '<option value="creative">Креативный (1 кредит)</option>';
        }
    }
    async function addCredits(amount) {
        chrome.storage.local.get(['userApiKey', 'userCredits'], async (data) => {
            if (data.userApiKey) {
                // В реальной версии здесь будет запрос к серверу
                const newCredits = (data.userCredits || 0) + amount;
                chrome.storage.local.set({ userCredits: newCredits }, () => {
                    creditsDisplay.textContent = \`\${newCredits} кредитов\`;
                });
            }
        });
    }
    // Обновляем кредиты каждые 30 секунд
    setInterval(loadUserInfo, 30000);
});
