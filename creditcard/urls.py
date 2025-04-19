"""
URL configuration for creditcard project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from fraud import views
urlpatterns = [
    path('admin/', admin.site.urls),
    path('home/',views.home,name='home'),
    path('signout/',views.signout,name='signout'),
    path('',views.signin,name='signin'),
    path('transaction/',views.transactions,name='transaction'),
    path('fraud/',views.fraud_view,name='fraud'),
    path('dashboard/',views.dashboard,name='dashboard'),
    path('cards/',views.cards,name='cards'),
path('active-cards/',views.active_cards,name='cards'),
    path('get_chart_data/<str:chart_type>/', views.get_chart_data, name='get_chart_data'),
    path("upload_csv/", views.upload_csv, name="upload_csv"),
]
