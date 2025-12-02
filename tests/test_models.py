from llama_cpp import Llama
import os

base_path = r"C:\ai_voice_assistant\models\llm"

models = [
    "mistral-7b-instruct-v0.3.Q4_K_M.gguf",
    "meta-llama-3-8b-instruct.Q4_K_M.gguf"
]

for model_name in models:
    path = os.path.join(base_path, model_name)
    print(f"\n🔹 Проверка модели: {model_name}")
    if not os.path.exists(path):
        print("❌ Файл не найден:", path)
        continue
    try:
        llm = Llama(model_path=path, n_ctx=1024, n_threads=8)
        print("✅ Модель успешно загружена!")
        del llm  # освобождаем память после проверки
    except Exception as e:
        print("⚠️ Ошибка при загрузке:", e)
