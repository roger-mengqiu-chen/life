from .account_admin import *
from .other_admin import *
from .transaction_admin import *

from django.contrib.auth.models import User
from django.contrib.auth.models import Group


admin.site.unregister(User)
admin.site.unregister(Group)
