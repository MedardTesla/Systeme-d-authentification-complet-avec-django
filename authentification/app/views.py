from email import message
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
from django.utils.encoding import force_bytes, force_text
from django.template.loader import render_to_string
from django.contrib.sites.shortcuts import get_current_site
from authentification import settings
from http.client import HTTPResponse
from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib.auth.models import User, auth
from django.contrib import messages
#from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.core.mail import send_mail, EmailMessage
from .token import generatorToken
# Create your views here.


def home(request):
    return render(request, 'app/index.html')





def signup(request):
    if request.method == 'POST':
        username = request.POST['username']   
        email = request.POST['email']
        password = request.POST['password']
        password1 = request.POST['password1']
        
        # Verifications
        if password == password1:
            if User.objects.filter(email=email).exists():
                messages.error(request, 'Ce email est déja utilisé')
                return redirect('signup')        

            if not username.isalnum():
                messages.info(request, 'Le nom doit etre alpha numeric')
                return redirect('signup')
            
            elif User.objects.filter(username=username).exists():
                messages.info(request, "Ce nom d'utilisateur est déja utilisé")
                return redirect('signup')
            
            else:
                nouveau_utilisateur = User.objects.create_user(username=username, email=email, password=password)
                nouveau_utilisateur.save()
                messages.success(request, "Votre compte a été crée avec success ")
                
                # Envoi de message de bienvenu par email


                subject = "Bienvenu sur medart Tesla"
                message = "Bienvenue "+nouveau_utilisateur.username+"\n Heureux parmi nous"
                from_email = settings.EMAIL_HOST_USER
                to_list = [nouveau_utilisateur.email]
                send_mail(subject, message, from_email, to_list, fail_silently=False)
                
                # envoi du email de confirmation
                current_site = get_current_site(request)
                email_subject = "Confirmation de l'address email sur medard tesla"
                messageconfirm = render_to_string("emailconfirm.html", {
                    "name": nouveau_utilisateur.username,
                    "domain":current_site.domain,
                    "uid":urlsafe_base64_encode(force_bytes(nouveau_utilisateur.pk)),
                    "token": generatorToken.make_token(nouveau_utilisateur)
                })
                
                email = EmailMessage(
                    email_subject,
                    messageconfirm,
                    settings.EMAIL_HOST_USER,
                    [nouveau_utilisateur.email]
                )
        
                email.fail_silently = False
                email.send()
                
                # identification de l'utisateur et connexion
                user_login = auth.authenticate(username=username, password=password)
                auth.login(request, user_login)
                return redirect('/')
        
        else:
            messages.info(request, "Les deux mots de pass ne coincide pas")
            return redirect('signup')
    
    else:        
            
        return render(request, 'app/signup.html')



def signin(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        
        user = auth.authenticate(username=username, password=password)
        if user is not None:
            auth.login(request, user)
            my_user = User.objects.get(username=username)
            firstname = my_user.username
            return render(request, 'app/index.html', {'firstname': firstname})
    
        else:
            messages.error(request, "Mauvaise authentification")
            return redirect('signin')
    return render(request, 'app/signin.html')







def logout(request):
    auth.logout(request)
    messages.success(request, "Vous vous etes decoonecté")
    return redirect('home')







def activate(request, uidb64, token):
    try:
        uid = force_text(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except(TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None
    if user is not None and generatorToken.check_token(user, token):
        user.is_active = True
        user.save()
        messages.success(request, "Votre Compte a été bien activé felicitation ")
        return redirect('login')
    else:
        messages.error(request, 'Activation echouer')
        return redirect('home')

