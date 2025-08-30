class Product:
    def __init__(self, name, price):
        self.name = name
        self.price = price

class Feature:
    def __init__(self, title, description):
        self.title = title
        self.description = description

# Список продуктов
products = [
    Product("30 дней", "300₽"),
    Product("Навсегда", "500₽"),
    Product("Скоро...", "1337")
]

# Общие характеристики
general_features = [
    Feature(
        "Обходы",
        "Наш клиент использует продвинутые методы обхода серверов FunTime, SpookyTime, HolyWorld и других серверов. Все функции работают максимально незаметно и безопасно для вашего аккаунта."
    ),
    Feature(
        "Визуалы",
        "Мы дадим вам красивейшие визуалы в нашем клиенте, TargetESP, Animations и т. д."
    ),
    Feature(
        "Поддержка",
        "Наша поддержка клиента отвечает менее чем за 2-10 минут, мы вам поможем убрать все возникающие ошибки клиента."
    ),
    Feature(
        "Красивый интерфейс",
        "Красивое ClickGui, красивый Hud, и полная ихняя кастомизация."
    )
]