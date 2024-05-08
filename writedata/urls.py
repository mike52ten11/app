from . import views

from django.urls import path,re_path

urlpatterns = [
    # path('<int:id>/', views.UsersView.as_view()),
    # re_path(r'^',views.EnergyListCreate.as_view()),
    path('energy/',views.EnergyListCreate.as_view()),
    path('login/', views.login, name = "login"),
    path('register/', views.register, name = "register"),
    path('register_device/', views.register_device, name = "register_device"),
    path('update_device/', views.update_device, name = "update_device"),
    path('Unbind_device/', views.Unbind_device, name = "Unbind_device"),
]
