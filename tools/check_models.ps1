Write-Host "🌐 Checking installed Vosk language models..." -ForegroundColor Cyan

$models = @{
    "ru" = "vosk-model-ru-0.42"
    "uz" = "vosk-model-small-uz-0.22"
    "en" = "vosk-model-en-us-0.15"
    "ar" = "vosk-model-ar-0.22-linto-1.1.0"
    "cn" = "vosk-model-cn-0.22"
}

$root = "C:\ai_voice_assistant\models\stt"

foreach ($lang in $models.Keys) {
    $path = Join-Path $root $models[$lang]
    if (Test-Path $path) {
        Write-Host "✅ $lang — $($models[$lang]) найден" -ForegroundColor Green
    } else {
        Write-Host "⚠️ $lang — отсутствует ($($models[$lang]))" -ForegroundColor Yellow
        Write-Host "   🔗 Скачать: https://alphacephei.com/vosk/models"
    }
}

Write-Host "`n🧠 Помести скачанные модели в $root (каждая в отдельной папке)."
Write-Host "✅ Проверка завершена!" -ForegroundColor Cyan
