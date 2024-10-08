ballanswers = [
  # Положительные
  "Бесспорно",
  "Предрешено",
  "Никаких сомнений",
  "Определённо да",
  "Можешь быть уверен в этом",

  # Нерешительно положительные
  "Мне кажется — «да»",
  "Вероятнее всего",
  "Хорошие перспективы",
  "Знаки говорят — «да»",
  "Да",

  # Нейтральные
  "Пока не ясно, попробуй снова",
  "Спроси позже",
  "Лучше не рассказывать",
  "Сейчас нельзя предсказать",
  "Сконцентрируйся и спроси опять",

  # Отрицательные
  "Даже не думай",
  "Мой ответ — «нет»",
  "По моим данным — «нет»",
  "Перспективы не очень хорошие",
  "Весьма сомнительно"
]

from dotenv import load_dotenv
import os

load_dotenv()

DATABASES_FOLDER = os.environ.get("DATABASES_FOLDER",'dbs')

howrutexts=["Сойдет","Отлично","Нормально"]

hellotexts=["Здарова","Привет","Привет, как дела?","Здрасте",
        "Hello",
        "Ahoj",
        "Halo",
        "Cześć",
        "Hej",
        "Merhaba",
        "Yassas",
        "Ciao",
        "Olá",
        "Hallå",
        "Bonjour",
        "Aloha",
        "Kon’nichiwa",
        "Zdrastĭ",
        "Namaste",
        "Sawubona",
        "Hola",
        "Nĭ Hăo",
        "Xin chào",
        "Annyeonghaseyo",
        "Sveiki",
        "Kaixo",
        "Hallo",
        "Hei",
        "Hujambo"]

botcolour = 16734003
botname = "Зверя нет сильней китайца, Стая блох, соси нам яйца"
logo = "https://i.pinimg.com/originals/f2/5f/3d/f25f3d95d5f15a1f28b89564ee8ad109.gif"

