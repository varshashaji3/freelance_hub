from client.models import ClientProfile
from core.models import CustomUser, Register


def client_context(request):
    if request.user.is_authenticated and request.user.role == 'client':
        uid = request.user.id
        profile1 = CustomUser.objects.get(id=uid)
        profile2 = Register.objects.get(user_id=uid)
        try:
            client = ClientProfile.objects.get(user_id=uid)
        except ClientProfile.DoesNotExist:
            client = None  
        return {
            'profile1': profile1,
            'profile2': profile2,
            'client': client,
        }
    return {}
