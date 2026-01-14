Write-Host "=== ПОЛНАЯ ОЧИСТКА URL ===" -ForegroundColor Red
# 1. Исправляем ВСЕ файлы
$files = Get-ChildItem -Path "extension" -Recurse -File -Include *.js, *.html, *.json
foreach ($file in $files) {
    $content = Get-Content $file.FullName -Raw
    $old = $content
    $content = $content -replace 'http://127\.0\.0\.1:8000', 'https://illustraitor-ai-v2.onrender.com'
    $content = $content -replace 'http://localhost:8000', 'https://illustraitor-ai-v2.onrender.com' 
    $content = $content -replace 'localhost:8000', 'illustraitor-ai-v2.onrender.com'
    $content = $content -replace '127\.0\.0\.1:8000', 'illustraitor-ai-v2.onrender.com'
    $content = $content -replace '"http://127.0.0.1:8000"', '"https://illustraitor-ai-v2.onrender.com"'
    $content = $content -replace "'http://127.0.0.1:8000'", "'https://illustraitor-ai-v2.onrender.com'"
    if ($content -ne $old) {
        Set-Content -Path $file.FullName -Value $content -Encoding UTF8
        Write-Host "✅ Исправлен: $($file.Name)" -ForegroundColor Green
    }
}
# 2. Проверка
Write-Host "`n=== ПРОВЕРКА ===" -ForegroundColor Cyan
$badFiles = Get-ChildItem -Path "extension" -Recurse -File | Where-Object {
    Select-String -Path $_.FullName -Pattern "127\.0\.0\.1|localhost:8000" -Quiet
}
if ($badFiles) {
    Write-Host "❌ Остались проблемы:" -ForegroundColor Red
    $badFiles | ForEach-Object { Write-Host "  - $($_.Name)" -ForegroundColor Yellow }
} else {
    Write-Host "✅ Все файлы чистые!" -ForegroundColor Green
}
Write-Host "`n=== ДЕЙСТВИЯ ===" -ForegroundColor Yellow
Write-Host "1. Удалите старое расширение" -ForegroundColor White
Write-Host "2. Установите заново из папки extension" -ForegroundColor White
Write-Host "3. Если ошибка - покажите Console (F12)" -ForegroundColor White
