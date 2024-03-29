from django.shortcuts import get_object_or_404, redirect
from django.shortcuts import render, redirect, reverse
from .models import Entry, Comment
from django.http import HttpResponse, HttpResponseRedirect
from django.contrib.auth.decorators import login_required
from . import forms
from .forms import CommentForm, UpdateEntry, WriteEntry
from django.views import generic
from django.contrib import messages
from django.views.generic import ListView, DetailView, CreateView, UpdateView
from django.urls import reverse_lazy
from django.contrib.messages.views import SuccessMessageMixin
from django.contrib.auth.mixins import LoginRequiredMixin
# Create your views here.

def entry_list(request):
    entries = Entry.objects.all().order_by('-created_on')
    return render(request, 'entry_list.html', {'entries': entries})

#from https://www.youtube.com/watch?v=-s7e_Fy6NRU  its class-based alternative to functions

# class EntryListView(ListView):
#     model = Entry
#     template_name = "entry_list_template.html"
#     context_object_name = "entries"


@login_required(login_url="/accounts/login")
def entry_detail(request, slug):
    entry = get_object_or_404(Entry, slug=slug)
    comments = entry.comments.all().order_by("-created_on")
    comment_count = entry.comments.filter(approved=True).count() 

    if request.method == "POST":
        comment_form = CommentForm(data=request.POST)
        if comment_form.is_valid():
            comment = comment_form.save(commit=False)
            comment.author = request.user
            comment.entry = entry
            comment.save()
            messages.add_message(
        request, messages.SUCCESS,
        'Comment submitted and awaiting approval'
    )

    comment_form = CommentForm()

    return render(request, 'entry_detail.html', 
{
    "entry": entry,
        "comments": comments,
        "comment_count": comment_count,
        "comment_form": comment_form,
    },
)

@login_required(login_url="/accounts/login")
def entry_write (request):
    if request.method == 'POST':
        form = forms.WriteEntry(request.POST, request.FILES)
        if form.is_valid():
            instance = form.save(commit = False)
            instance.author = request.user
            instance.save()
            messages.success(request, "Tale successfully published")
            return redirect('entries:list')
    else:
        form = forms.WriteEntry()
    return render(request, "entry_write.html", {'form': form})


def like_entry(request, slug):
     entry = get_object_or_404(Entry, slug=slug)
     entry.likes += 1
     entry.save()
    
     return redirect('entries:entry_detail', slug=entry.slug)



def delete_entry(request, slug):
    entry = get_object_or_404(Entry, slug=slug)
    if request.user == entry.author:
        entry.delete()
        messages.success(request, "Tale successfully deleted")
        return redirect(reverse('entries:list'))
    else:
        messages.error(request, "You don't have permission to delete this entry")
    return redirect(reverse('entries:list'))



 
class EditEntry(LoginRequiredMixin, SuccessMessageMixin, UpdateView):
    model = Entry
    form_class = WriteEntry
    template_name = 'entry_edit.html'
    success_url = reverse_lazy('entries:list')
    success_message = "Tale successfully edited"
 


   

   
