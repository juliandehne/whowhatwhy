from django.contrib.messages.views import SuccessMessageMixin
from django.db.models import UniqueConstraint
from django.shortcuts import render, get_object_or_404
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib import messages
from django.contrib.auth.models import User
from django.views.generic import (
    ListView,
    DetailView,
    CreateView,
    UpdateView,
    DeleteView
)
from .models import Post, Institution


def home(request):
    context = {
        'posts': Post.objects.all(),
        'institutions': Institution.objects.all()
    }
    return render(request, 'blog/home.html', context)


class PostListView(ListView):
    model = Post
    template_name = 'blog/home.html'  # <app>/<model>_<viewtype>.html
    context_object_name = 'posts'
    ordering = ['-date_posted']
    paginate_by = 5

    def get_context_data(self, **kwargs):
        context = super(PostListView, self).get_context_data(**kwargs)
        context['institutions'] = Institution.objects.all()
        return context


class UserPostListView(ListView):
    model = Post
    template_name = 'blog/user_posts.html'  # <app>/<model>_<viewtype>.html
    context_object_name = 'posts'
    paginate_by = 5

    def get_queryset(self):
        user = get_object_or_404(User, username=self.kwargs.get('username'))
        return Post.objects.filter(author=user).order_by('-date_posted')


class PostDetailView(DetailView):
    model = Post


class InstitutionView(DetailView):
    model = Institution


class PostCreateView(LoginRequiredMixin, CreateView):
    model = Post
    fields = ['title', 'content', 'institution']

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)


class InstitutionCreateView(SuccessMessageMixin, LoginRequiredMixin, CreateView):
    model = Institution
    fields = ['title', 'description', 'image', 'country']

    success_message = "Institution %(title)s was created successfully"

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)


class PostUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Post
    fields = ['title', 'content']

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)

    def test_func(self):
        post = self.get_object()
        if self.request.user == post.author:
            return True
        return False


class PostDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Post
    success_url = '/'

    def test_func(self):
        post = self.get_object()
        if self.request.user == post.author:
            return True
        return False


def about(request):
    return render(request, 'blog/about.html', {'title': 'About'})


class InstitutionPostList(ListView):
    model = Post
    template_name = 'blog/institution_posts.html'  # <app>/<model>_<viewtype>.html
    context_object_name = 'posts'
    paginate_by = 5

    # fields = ['title', 'content', 'institution']

    def get_queryset(self):
        institution = get_object_or_404(Institution, id=self.request.resolver_match.kwargs['pk'])
        return Post.objects.filter(institution=institution).order_by('-date_posted')

    def get_context_data(self, **kwargs):
        context = super(InstitutionPostList, self).get_context_data(**kwargs)
        institution = get_object_or_404(Institution, id=self.request.resolver_match.kwargs['pk'])
        context['institution_title'] = institution.title
        context['institutions'] = Institution.objects.all()
        return context

