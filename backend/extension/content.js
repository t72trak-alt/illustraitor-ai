console.log("Illustraitor AI loaded in Google Docs");

// Функция добавления кнопки
function addButtonToGoogleDocs() {
    // Ищем тулбар Google Docs
    const toolbar = document.querySelector(".docs-titlebar-buttons") || 
                   document.querySelector(".docs-toolbar");
    
    if (toolbar && !document.querySelector("#illustraitor-btn")) {
        const button = document.createElement("button");
        button.id = "illustraitor-btn";
        button.textContent = "🎨 AI Illustrate";
        
        // Стили кнопки
        button.style.cssText = `
            margin-left: 10px;
            padding: 8px 16px;
            background: #667eea;
            color: white;
            border: none;
            border-radius: 4px;
            cursor: pointer;
            font-weight: bold;
        `;
        
        button.onclick = function() {
            const selectedText = window.getSelection().toString().trim();
            if (selectedText) {
                alert("Выделенный текст: " + selectedText.substring(0, 50));
                // Здесь будет вызов API
            } else {
                alert("Выделите текст для генерации иллюстрации");
            }
        };
        
        toolbar.appendChild(button);
        console.log("Кнопка добавлена в Google Docs");
    }
}

// Запускаем при загрузке
if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", addButtonToGoogleDocs);
} else {
    addButtonToGoogleDocs();
}

// Для динамических обновлений
const observer = new MutationObserver(addButtonToGoogleDocs);
observer.observe(document.body, { childList: true, subtree: true });
