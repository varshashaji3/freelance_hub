web: python manage.py makemigrations && \
     python manage.py migrate && \
     python manage.py createsuperuser --noinput --email admin@gmail.com && \
     python -c "from django.contrib.auth import get_user_model; User = get_user_model(); user = User.objects.get(email='admin@gmail.com'); user.set_password('Admin@12'); user.role = 'admin'; user.save()" && \
     python -c "from django.contrib.sites.models import Site; Site.objects.update_or_create(id=1, defaults={'domain': 'https://freelancehub-production.up.railway.app/', 'name': 'FreelanceHub'})" && \
     python -c "from socialaccount.models import SocialApp; SocialApp.objects.update_or_create(provider='google', defaults={'name': 'GoogleLogin', 'client_id': os.environ['GOOGLE_CLIENT_ID'], 'secret': os.environ['GOOGLE_CLIENT_SECRET']})" && \
     python -c "from socialaccount.models import SocialAppSite; from django.contrib.sites.models import Site; SocialAppSite.objects.get_or_create(socialapp_id=1, site=Site.objects.get(id=1))" && \
     python manage.py collectstatic --noinput && \
     gunicorn freelancehub.wsgi:application --bind 0.0.0.0:$PORT
