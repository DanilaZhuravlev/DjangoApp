from django.urls import path
from .views import (login_view,
                    get_cookie_view,
                    set_cookie_view,
                    set_session_view,
                    get_session_view,
                    logout_view,
                    AboutMeView,
                    RegisterView,
                    FooBarView,
                    edit_avatar_view,
                    user_list_view,
                    user_detail_view,
                    HelloView,
                    )
from django.contrib.auth.views import LoginView, LogoutView


app_name = 'myauth'


urlpatterns = [
    path('login/', LoginView.as_view(
        template_name='myauth/login.html', redirect_authenticated_user=True
    ),
         name='login'),
    path('hello/', HelloView.as_view(), name='hello'),
    path('cookie/get', get_cookie_view, name='cookie-get'),
    path('cookie/set', set_cookie_view, name='cookie-set'),
    path('session/set', set_session_view, name='session-set'),
    path('session/get', get_session_view, name='session-get'),
    path('logout/', logout_view, name='logout'),
    path('about-me/', AboutMeView.as_view(), name='about-me'),
    path('about-me/edit-avatar/<int:pk>/', edit_avatar_view, name='edit-avatar'),
    path('register/', RegisterView.as_view(), name='register'),
    path('foo-bar/', FooBarView.as_view(), name='foo-bar'),
    path('users/', user_list_view, name='user-list'),
    path('users/<int:pk>/', user_detail_view, name='user-detail'),


]
