from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _

class LicensingConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'licensing'
    verbose_name = _('نظام التراخيص')

    def ready(self):
        import licensing.signals