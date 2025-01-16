from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.messages import constants
from django.contrib import auth
from django.core.files.storage import default_storage
import os
from deepface import DeepFace
from django.contrib.auth import authenticate, login
from .models import UserProfile

def cadastro(request):
    if request.method == "GET":
        return render(request, 'cadastro.html')
    elif request.method == "POST":
        username = request.POST.get('username')
        senha = request.POST.get('senha')
        confirmar_senha = request.POST.get('confirmar_senha')
        image = request.FILES.get('image')

        if not senha == confirmar_senha:
            print("As senhas não coincidem.")
            return redirect('/usuarios/cadastro')

        if len(senha) < 1:
            print("A senha deve ter pelo menos 6 caracteres.")
            return redirect('/usuarios/cadastro')

        users = User.objects.filter(username=username)
        if users.exists():
            print("O username já está em uso.")
            return redirect('/usuarios/cadastro')

        save_path = r"C:\\fotos"

        if image:
            if not os.path.exists(save_path):
                os.makedirs(save_path)
            image_name = os.path.join(save_path, f"{username}.jpg")
            with open(image_name, 'wb+') as f:
                for chunk in image.chunks():
                    f.write(chunk)
            print(f"Imagem salva em: {image_name}")
        else:
            print("Nenhuma imagem enviada.")
            return redirect('/usuarios/cadastro')

        user = User.objects.create_user(
            username=username,
            password=senha
        )

        UserProfile.objects.create(
            user=user,
            image_url=image_name
        )

        return redirect('/usuarios/logar')

def logar(request):
    if request.method == "POST":
        username = request.POST.get('username')
        image = request.FILES.get('image')

        if not username or not image:
            return render(request, 'login.html', {'error': 'Por favor, insira todos os campos.'})

        try:
            user_profile = UserProfile.objects.get(user__username=username)
        except UserProfile.DoesNotExist:
            return render(request, 'login.html', {'error': 'Usuário não encontrado.'})

        registered_image_path = user_profile.image_url
        temp_image_path = f"C:\\fotos/{image.name}"

        with open(temp_image_path, 'wb+') as f:
            for chunk in image.chunks():
                f.write(chunk)

        try:
            result = DeepFace.verify(img1_path=registered_image_path, img2_path=temp_image_path)

            if result['verified']:
                user = User.objects.get(username=username)
                login(request, user)
                return redirect('/usuarios/dashboard')
            else:
                return render(request, 'login.html', {'error': 'Rosto não reconhecido. Tente novamente.'})
        except Exception as e:
            return render(request, 'login.html', {'error': f'Ocorreu um erro: {str(e)}'})
        finally:
            if os.path.exists(temp_image_path):
                os.remove(temp_image_path)

    return render(request, 'login.html')
