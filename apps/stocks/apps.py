from django.apps import AppConfig

class StocksConfig(AppConfig):
    name = 'apps.stocks'

    def ready(self):
        import apps.stocks.signals
