import os

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "ai_shop.settings.local")

import django  # noqa: E402

django.setup()

from django_dramatiq import get_broker  # noqa: E402

broker = get_broker()
