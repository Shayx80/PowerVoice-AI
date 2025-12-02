import os
from llama_cpp import Llama


class NlpProcessor:
    """
    Модуль локального NLP (офлайн без API).
    Поддерживает:
    - Mistral, LLaMA и другие GGUF модели
    - автоматический выбор и резервное переключение
    """

    def __init__(self, config: dict):
        self.config = config
        self.models_root = os.path.join("models", "llm")

        # Кандидаты в порядке приоритета
        candidates = [
            config.get("llm_primary"),
            config.get("llm_secondary"),
            config.get("llm_model"),
            "mistral-7b-instruct-v0.3.Q4_K_M.gguf",
            "meta-llama-3-8b-instruct.Q4_K_M.gguf",
        ]
        self.candidates = [x for x in candidates if x]

        # Текущая активная модель
        self.active_model = None
        self.llm = None

        self._load_first_available_model()

    def _load_first_available_model(self):
        """Загружает первую доступную модель."""
        tried = []

        for name in self.candidates:
            path = os.path.join(self.models_root, name)
            tried.append(path)
            if os.path.exists(path):
                try:
                    print(f"🧠 Загружаю LLM модель: {path}")
                    self.llm = Llama(model_path=path, n_ctx=2048, n_threads=8, verbose=False)
                    self.active_model = path
                    return
                except Exception as e:
                    print(f"⚠️ Ошибка при загрузке {name}: {e}")

        raise FileNotFoundError(
            "❌ Не удалось загрузить ни одну модель.\n"
            "Проверенные пути:\n  " + "\n  ".join(tried)
        )

    def _switch_to_backup_model(self):
        """Автоматически переключается на следующую модель, если активная дала сбой."""
        if not self.active_model:
            return False

        current_index = None
        for i, name in enumerate(self.candidates):
            if name.lower() in self.active_model.lower():
                current_index = i
                break

        if current_index is not None and current_index + 1 < len(self.candidates):
            backup_name = self.candidates[current_index + 1]
            backup_path = os.path.join(self.models_root, backup_name)
            if os.path.exists(backup_path):
                print(f"🔁 Переключение на резервную модель: {backup_name}")
                self.llm = Llama(model_path=backup_path, n_ctx=2048, n_threads=8, verbose=False)
                self.active_model = backup_path
                return True

        return False

    def generate_response(self, text: str) -> str:
        """Создание ответа с автоматическим fallback при ошибке."""
        if not text.strip():
            return "Я ничего не услышал."

        model_name = os.path.basename(self.active_model or "").lower()

        try:
            # Mistral — особый формат
            if "mistral" in model_name:
                prompt = f"[INST] {text.strip()} [/INST]"
                result = self.llm(
                    prompt,
                    max_tokens=256,
                    temperature=0.7,
                    top_p=0.95,
                )
                return result["choices"][0]["text"].strip()

            # LLaMA — стандартный чат формат
            elif "llama" in model_name:
                messages = [
                    {
                        "role": "system",
                        "content": (
                            "Ты локальный мультиязычный голосовой ассистент. "
                            "Отвечай естественно, кратко и понятно. "
                            "Поддерживаешь русский, узбекский, английский и арабский языки."
                        ),
                    },
                    {"role": "user", "content": text.strip()},
                ]
                result = self.llm.create_chat_completion(
                    messages=messages,
                    max_tokens=256,
                    temperature=0.7,
                )
                return result["choices"][0]["message"]["content"].strip()

            # fallback для любых других GGUF
            else:
                result = self.llm(
                    text.strip(),
                    max_tokens=256,
                    temperature=0.7,
                )
                return result["choices"][0]["text"].strip()

        except Exception as e:
            print(f"⚠️ Ошибка модели ({model_name}): {e}")
            if self._switch_to_backup_model():
                return self.generate_response(text)
            return f"Ошибка LLM: {e}"
