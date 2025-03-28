from django.shortcuts import redirect, render
from django.views.generic import TemplateView
from django.core.mail import EmailMessage
from django.template.loader import render_to_string
from django.conf import settings
from django.contrib import messages

class indexView(TemplateView):
    template_name = 'inicio.html'

def contact(request):
    if request.method == 'POST':
        name = request.POST['name']
        sender_email = request.POST['email']
        subject = request.POST['subject']
        msg = request.POST['msg']
        
        print(f"Name: {name}, Email: {sender_email}, Subject: {subject}, Message: {msg}")
        
        template = render_to_string('email_template.html', {
            'name': name,
            'email': sender_email,
            'subject': subject,
            'msg': msg
        })
        
        email = EmailMessage(
            subject,
            template,
            settings.EMAIL_HOST_USER,
            ['asuan.adso@gmail.com']
        )
        
        email.fail_silently = False
        email.send()
        
        messages.success(request, 'Correo enviado.')
        return redirect('index')
