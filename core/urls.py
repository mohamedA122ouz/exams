from django.urls import path, include
from django.contrib.auth import views as authViews
from core.controllers import home,exam



urlpatterns = [
    path('login',home.userLogin,name="login"),
    path('user/create',home.createUser,name="createUser"),
    path('logout/',authViews.LogoutView.as_view(),name='logout'),
    path('terms',exam.showTerms, name="showTerms"),
    path('terms/create',exam.createTerm,name="createTerm"),
    path('years',exam.showYears,name="showYears"),
    path('years/create',exam.createYear,name="createYear"),
    path('subjects/create',exam.createSubject,name="createSubject"),
    path('subjects',exam.showSubjects,name="showSubjects")
]