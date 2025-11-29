from django.urls import path, include
from django.contrib.auth import views as authViews
from core.controllers import API, home



urlpatterns = [
    path('login',home.userLogin,name="API_login"),
    path('user/create',home.createUser,name="API_createUser"),
    path('logout/',authViews.LogoutView.as_view(),name='API_logout'),
    path('terms',API.showTerms, name="showTerms"),
    path('terms/create',API.createTerm,name="API_createTerm"),
    path('years',API.showYears,name="API_showYears"),
    path('years/create',API.createYear,name="API_createYear"),
    path('subjects/create',API.createSubject,name="API_createSubject"),
    path('subjects',API.showSubjects,name="API_showSubjects"),
    path('lectures',API.showLectures,name="API_showSubjects"),
    path('lectures/create',API.createLectures,name="API_showSubjects"),
    path('questions',API.showQuestions,name="API_showQuestions"),
    path('question/create',API.createQuestion,name="API_createQuestion"),
    path('questions/create',API.createQuestions,name="API_createQuestions"),
]