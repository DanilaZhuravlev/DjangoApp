from random import random
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required,permission_required,user_passes_test
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.contrib.auth.views import LogoutView
from django.contrib import messages
from django.http import HttpResponse, HttpRequest, JsonResponse, HttpResponseForbidden
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse, reverse_lazy
from .models import Profile
from django.views import View
from .forms import AvatarForm
from django.views.generic import TemplateView, CreateView
from django.utils.translation import gettext_lazy as _, ngettext
from django.views.decorators.cache import cache_page




class HelloView(View):
    welcome_message = _('Welcome hello world!')
    def get(self, request):
        items_str = request.GET.get('items') or 0
        items = int(items_str)
        products_line = ngettext(
            'one product',
            '{count} products',
            items,
        )
        products_line =  products_line.format(count=items)
        return HttpResponse(
            f"<h1>{self.welcome_message}</h1>"
            f"\n<h2>{products_line}</h2>"

        )

class AboutMeView(TemplateView):
    template_name = 'myauth/about-me.html'

class RegisterView(CreateView):
    form_class = UserCreationForm
    template_name = 'myauth/register.html'
    success_url = reverse_lazy('myauth:about-me')

    def form_valid(self, form):
        username = form.cleaned_data.get('username')
        password = form.cleaned_data.get('password1')
        response = super().form_valid(form)
        Profile.objects.create(user=self.object)
        user = authenticate(self.request, username=username, password=password,)
        login(self.request, user)
        return response


def login_view(request:HttpRequest):
    if request.method == "GET":
        if request.user.is_authenticated:
            return redirect('/admin')

        return render(request, 'myauth/login.html')

    username = request.POST['username']
    password = request.POST['password']

    user = authenticate(request, username=username, password=password)
    if user is not None:
        login(request, user)
        return redirect('/admin')

    return render(request, 'myauth/login.html', {'error': 'Invalid username or password'})

# @user_passes_test(lambda u: u.is_superuser)
def set_cookie_view(request:HttpRequest):
    response = HttpResponse("Cookies set")
    response.set_cookie('fizz','buzz', max_age=3600)
    return response
@cache_page(60 * 2)
def get_cookie_view(request:HttpRequest):
    value = request.COOKIES.get('fizz', 'default value')
    return HttpResponse(f'Cookie value: {value!r} + {random()}')
@permission_required('myauth.view_profile', raise_exception=True)
def set_session_view(request:HttpRequest):
    request.session['foobar'] = 'spameggs'
    return HttpResponse('Session set')

@login_required
def get_session_view(request:HttpRequest):
    value = request.session.get('foobar', 'default value')
    return HttpResponse(f'Session value: {value!r}')

def logout_view(request:HttpRequest):
    logout(request)
    return redirect(reverse('myauth:login'))

# class MyLogoutView(LogoutView):
#     next_page = reverse_lazy('myauth:login')
#
#     def get(self, request, *args, **kwargs):
#         return self.post(request, *args, **kwargs)


class FooBarView(View):
    def get(self, request: HttpRequest) -> JsonResponse:
        return JsonResponse({'foo':'bar', 'spam':'eggs'})


@login_required
def edit_avatar_view(request, pk):
    profile = get_object_or_404(Profile, pk=pk)
    if request.user != profile.user and not request.user.is_staff:
        return HttpResponseForbidden("You are not allowed to edit this profile.")
    if request.method == 'POST':
        form = AvatarForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            form.save()
            messages.success(request, 'Avatar updated successfully!')
            return redirect('myauth:user-detail', pk=profile.user.pk)
    else:
        form = AvatarForm(instance=profile)

    return render(request, 'myauth/edit_avatar.html', {'form': form})


def user_list_view(request):
    users = User.objects.all()
    return render(request, 'myauth/user_list.html', {'users': users})

def user_detail_view(request, pk):
    user = get_object_or_404(User, pk=pk)
    return render(request, 'myauth/user_detail.html', {'user': user})
