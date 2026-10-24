from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from .models import Topic, Reply
from .forms import TopicForm, ReplyForm
import csv
from django.http import HttpResponse
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib import messages
from django.contrib.auth import get_user_model
from django.contrib.auth.models import User

User = get_user_model()


@staff_member_required
def topics_export_csv(request):
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="topics.csv"'

    writer = csv.writer(response, quoting=csv.QUOTE_ALL)
    writer.writerow(['title', 'content', 'author', 'created_at'])

    for topic in Topic.objects.all():
        writer.writerow([
            topic.title,
            topic.content,
            topic.author.username,
            topic.created_at,
        ])

    return response

@staff_member_required
def topics_import_csv(request):
    if request.method == "POST" and request.FILES.get("csv_file"):
        csv_file = request.FILES["csv_file"]
        decoded_file = TextIOWrapper(csv_file.file, encoding="utf-8-sig")
        reader = csv.DictReader(decoded_file)

        created_count = 0
        skipped_count = 0

        default_author = User.objects.filter(is_staff=True).first()  # или None

        for row in reader:
            title = (row.get("title") or "").strip()
            content = (row.get("content") or "").strip()
            author_value = (row.get("author") or "").strip()

            if not title:
                skipped_count += 1
                continue

            author = None

            # 1) пробуем найти автора по username
            if author_value:
                author = User.objects.filter(username=author_value).first()

            # 2) если не нашли — берём дефолтного
            if not author:
                author = default_author

            # 3) если автора всё равно нет — пропускаем строку
            if not author:
                skipped_count += 1
                continue

            Topic.objects.create(
                title=title,
                content=content,
                author=author,
            )
            created_count += 1

        messages.success(
            request,
            f"Импорт завершён: добавлено {created_count}, пропущено {skipped_count}."
        )
        return redirect("forum:topic_list")   # <-- исправь namespace

    return render(request, "forum/import_csv.html")




@staff_member_required
def topics_export_csv(request):
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="topics.csv"'

    writer = csv.writer(response)
    writer.writerow(['title', 'content', 'author', 'created_at'])

    for topic in Topic.objects.all():
        writer.writerow([
            topic.title,
            topic.content,
            topic.author.username if topic.author else '',
            topic.created_at.strftime('%Y-%m-%d %H:%M:%S'),
        ])

    return response


@staff_member_required
def topics_import_csv(request):
    if request.method == 'POST' and request.FILES.get('csv_file'):
        csv_file = request.FILES['csv_file']
        data = csv_file.read().decode('utf-8').splitlines()
        reader = csv.reader(data)
        next(reader, None)  # пропустить заголовок

        for row in reader:
            if len(row) < 2:
                continue
            title = row[0]
            content = row[1]
            Topic.objects.create(title=title, content=content)

        messages.success(request, 'Темы успешно импортированы')
        return redirect('topic_list')

    return render(request, 'forum/topic_import.html')


@login_required
def topic_list(request):
    topics = Topic.objects.all().order_by('-created_at')
    return render(request, 'forum/topic_list.html', {'topics': topics})


@login_required
def topic_create(request):
    if request.method == 'POST':
        form = TopicForm(request.POST)
        if form.is_valid():
            topic = form.save(commit=False)
            topic.author = request.user
            topic.save()
            return redirect('forum_topic_list')
    else:
        form = TopicForm()
    return render(request, 'forum/topic_form.html', {'form': form})


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


@login_required
def topic_delete(request, pk):
    topic = get_object_or_404(Topic, pk=pk, author=request.user)
    if request.method == 'POST':
        topic.delete()
        return redirect('forum_topic_list')
    return render(request, 'forum/topic_confirm_delete.html', {'topic': topic})
