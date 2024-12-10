from django.contrib import admin
from User_Management.models import (
    User,
    AdminOrStaff,
    Supplier,
    Member,
    MusicContentInformation,
    Artist,
)

admin.site.register(User)
admin.site.register(Member)
admin.site.register(Artist)
admin.site.register(Supplier)
admin.site.register(AdminOrStaff)
admin.site.register(MusicContentInformation)
