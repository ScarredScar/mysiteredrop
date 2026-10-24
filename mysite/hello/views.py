from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required, user_passes_test
from django.http import FileResponse
from .forms import RegisterForm, MediaUploadForm
from .models import MediaFile
from django.contrib.auth import get_user_model, update_session_auth_hash
from django.contrib.auth.hashers import make_password

from django.contrib.auth import get_user_model
from django.contrib.auth.hashers import make_password
from django.contrib import messages
from django.shortcuts import render, redirect

User = get_user_model()

def password_reset_request(request):
    if request.method == "POST":
        username = request.POST.get("username")
        user = User.objects.filter(username=username).first()
        if user:
            request.session["reset_user_id"] = user.id
            return redirect("password_reset_confirm")
        messages.error(request, "Пользователь не найден")
    return render(request, "password_reset_form.html")


def password_reset_confirm(request):
    user_id = request.session.get("reset_user_id")
    if not user_id:
        return redirect("password_reset")

    user = User.objects.filter(id=user_id).first()
    if not user:
        return redirect("password_reset")

    if request.method == "POST":
        p1 = request.POST.get("password1")
        p2 = request.POST.get("password2")
        if p1 == p2:
            user.password = make_password(p1)
            user.save()
            del request.session["reset_user_id"]
            return redirect("login")
        messages.error(request, "Пароли не совпадают")

    return render(request, "password_reset_confirm.html")


@login_required
def topic_detail(request, pk):
    topic = get_object_or_404(Topic, pk=pk)
    replies = topic.replies.all().order_by('created_at')

    if request.method == 'POST':
        form = ReplyForm(request.POST)
        if form.is_valid():
            reply = form.save(commit=False)
            reply.topic = topic
            reply.author = request.user
            reply.save()
            return redirect('forum_topic_detail', pk=topic.pk)
    else:
        form = ReplyForm()

    return render(request, 'forum/topic_detail.html', {
        'topic': topic,
        'replies': replies,
        'form': form,
    })

def download_media_view(request, pk):
    media = get_object_or_404(MediaFile, pk=pk)
    return FileResponse(
        media.file.open("rb"),
        as_attachment=True,
        filename=media.file.name.split("/")[-1]
    )


def logout_view(request):
    logout(request)
    return redirect("home")


def register_view(request):
    if request.method == "POST":
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect("home")
    else:
        form = RegisterForm()
    return render(request, "register.html", {"form": form})


@login_required
def upload_media_view(request):
    if request.method == "POST":
        form = MediaUploadForm(request.POST, request.FILES)
        if form.is_valid():
            media = form.save(commit=False)
            media.uploaded_by = request.user
            media.save()
            return redirect("home")
    else:
        form = MediaUploadForm()
    return render(request, "upload.html", {"form": form})


@login_required
def home_view(request):
    files = MediaFile.objects.all().order_by("-created_at")
    return render(request, "home.html", {"files": files})


def is_admin(user):
    return user.is_staff


@user_passes_test(is_admin)
def delete_media_view(request, pk):
    media = get_object_or_404(MediaFile, pk=pk)
    media.delete()
    return redirect("home")