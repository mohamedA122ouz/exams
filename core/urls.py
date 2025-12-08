from django.urls import path, include
from django.contrib.auth import views as authViews
from core.controllers import View, home



urlpatterns = [
    path('pages/login',home.userloginPage,name="userloginPage"),
    path('login',home.userLogin,name="login"),
    path('pages/users/create',home.signup,name="signup"),
    path('users/create',home.createUser,name="createUser"),
    path('logout/',authViews.LogoutView.as_view(),name='logout'),
    path('terms',View.showTerms, name="showTerms"),
    path('terms/create',View.createTerm,name="createTerm"),
    path('years',View.showYears,name="showYears"),
    path('years/create',View.createYear,name="createYear"),
    path('subjects/create',View.createSubject,name="createSubject"),
    path('subjects',View.showSubjects,name="showSubjects"),
    path('lectures',View.showLectures,name="showSubjects"),
    path('lectures/create',View.createLectures,name="showSubjects"),
    path('questions',View.showQuestions,name="showQuestions"),
    path('question/create',View.createQuestion,name="createQuestion"),
    path('questions/create',View.createQuestions,name="createQuestions"),
    
    path('test',View.test,name="test"),
]