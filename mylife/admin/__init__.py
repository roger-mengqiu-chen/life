from .account_admin import *  # noqa
from .other_admin import *  # noqa
from .transaction_admin import *  # noqa

from django.contrib.auth.models import User
from django.contrib.auth.models import Group


admin.site.unregister(User)  # noqa
admin.site.unregister(Group)  # noqa
