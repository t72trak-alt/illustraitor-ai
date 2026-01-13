# Создаем простые иконки с помощью PowerShell (если есть .NET)
Add-Type -AssemblyName System.Drawing
# Создаем функцию для создания иконки
function Create-Icon {
    param(, )
     = New-Object System.Drawing.Bitmap , 
     = [System.Drawing.Graphics]::FromImage()
    # Заливаем фон
    .Clear([System.Drawing.Color]::FromArgb(74, 144, 226))
    # Рисуем палитру
     = New-Object System.Drawing.SolidBrush ([System.Drawing.Color]::White)
     = New-Object System.Drawing.Font "Arial", (/3), [System.Drawing.FontStyle]::Bold
    .DrawString("🎨", , , (/4), (/4))
    .Save(\, [System.Drawing.Imaging.ImageFormat]::Png)
    \.Dispose()
    \.Dispose()
}
# Создаем иконки разных размеров
try {
    Create-Icon -size 16 -filename "icon16.png"
    Create-Icon -size 48 -filename "icon48.png"
    Create-Icon -size 128 -filename "icon128.png"
    Write-Host "✅ Иконки созданы!" -ForegroundColor Green
} catch {
    Write-Host "⚠️ Не удалось создать иконки через .NET. Создайте вручную." -ForegroundColor Yellow
    Write-Host "📋 См. файл ICONS_README.txt для инструкций" -ForegroundColor Yellow
}
