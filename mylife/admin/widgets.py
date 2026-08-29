from datetime import datetime
from django.conf import settings
from import_export import widgets


class MultiFormatDateWidget(widgets.DateWidget):
    def clean(self, value, row=None, **kwargs):
        if not value:
            return None

        formats = settings.TRANSACTION_TIME_FORMAT

        for fmt in formats:
            try:
                return datetime.strptime(value.strip(), fmt).date()
            except (ValueError, TypeError):
                continue

        return super().clean(value, row, **kwargs)
