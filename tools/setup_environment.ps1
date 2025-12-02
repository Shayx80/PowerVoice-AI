# ⚙️ Настройка окружения AI Voice Assistant
Write-Host "Setting up Python virtual environment and dependencies..."

$root = "C:\ai_voice_assistant"
$venvPath = "$root\venv"

# Создание виртуального окружения
if (!(Test-Path $venvPath)) {
    python -m venv $venvPath
    Write-Host "✅ Virtual environment created at $venvPath"
} else {
    Write-Host "✅ Virtual environment already exists."
}

# Активация окружения
& "$venvPath\Scripts\activate.ps1"

# Установка зависимостей
Write-Host "📦 Installing required packages..."
& "$venvPath\Scripts\python.exe" -m pip install --upgrade pip
& "$venvPath\Scripts\pip.exe" install -r "$root\requirements.txt"

# Проверка установки
Write-Host "`n🔍 Checking installation..."
& "$venvPath\Scripts\python.exe" -m pip list

Write-Host "`n✅ Environment setup complete!"
Write-Host "To start the assistant, run the following commands:"
Write-Host "   cd C:\ai_voice_assistant"
Write-Host "   venv\Scripts\activate"
Write-Host "   python main.py"
