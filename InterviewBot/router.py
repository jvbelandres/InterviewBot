from user.viewsets import AccountViewset
from rest_framework import routers

router = routers.DefaultRouter()
router.register('user-registration', AccountViewset)