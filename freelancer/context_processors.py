from freelancer.models import FreelancerProfile
from core.models import CustomUser, Register

def freelancer_context(request):
    if request.user.is_authenticated and request.user.role == 'freelancer':
        uid = request.user.id
        profile1 = CustomUser.objects.get(id=uid)
        profile2 = Register.objects.get(user_id=uid)
        freelancer = FreelancerProfile.objects.get(user_id=uid)
        return {
            'profile1': profile1,
            'profile2': profile2,
            'freelancer': freelancer,
        }
    return {}