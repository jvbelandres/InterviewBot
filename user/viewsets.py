from rest_framework import viewsets
from .models import Account
from .serializers import AccountRegisterSerializer

class AccountViewset(viewsets.ModelViewSet):
    queryset = Account.objects.all()
    serializer_class = AccountRegisterSerializer