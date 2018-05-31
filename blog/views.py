from django.shortcuts import render
from .forms import BlogForm


def index(request):
    submitbutton = request.POST.get("submit")

    title = ''
    message = ''

    form = BlogForm(request.POST or None)
    if form.is_valid():
        title = form.cleaned_data.get("title")
        message = form.cleaned_data.get("message")

    context = {'form': form, 'title': title, 'message': message,
               'submitbutton': submitbutton}

    return render(request, 'index.html', context)
