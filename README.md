# KillProcess

Утилита для быстрого завершения активного окна или процесса по горячей клавише.

---

## Функционал

- Завершение активного процесса (окна), даже если он не отвечает.
- Настраиваемый хоткей для вызова функции.
- Запуск в системном трее с иконкой.
- Возможность включения автозапуска в Windows.
- Графический интерфейс для смены хоткея.

---

## Требования

- Windows
- Python 3.6+
- Библиотеки из `requirements.txt`:
  - psutil
  - pywin32
  - keyboard
  - pystray
  - Pillow
  - tkinter (обычно в комплекте с Python)

---

## Установка

1. Склонируйте репозиторий:
   ```bash
   git clone https://github.com/w99zzl1/KillProcess.git
   cd KillProcess
   
2. Установите зависимости:
  ```bash
  pip install -r requirements.txt
```

## Использование
Запустите скрипт:

```bash
python KillProcess.py
