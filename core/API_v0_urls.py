from django.urls import path, include
from django.contrib.auth import views as authViews
from core.controllers import API_v0, home



urlpatterns = [
    path('login',home.userLogin,name="API_v0_login"),
    path('user/create',home.createUser,name="API_v0_createUser"),
    path('logout/',authViews.LogoutView.as_view(),name='API_v0_logout'),
    path('terms',API_v0.showTerms, name="showTerms"),
    path('terms/create',API_v0.createTerm,name="API_v0_createTerm"),
    path('years',API_v0.showYears,name="API_v0_showYears"),
    path('years/create',API_v0.createYear,name="API_v0_createYear"),
    path('subjects/create',API_v0.createSubject,name="API_v0_createSubject"),
    path('subjects',API_v0.showSubjects,name="API_v0_showSubjects"),
    path('lectures',API_v0.showLectures,name="API_v0_showSubjects"),
    path('lectures/create',API_v0.createLectures,name="API_v0_showSubjects"),
    path('questions',API_v0.showQuestions,name="API_v0_showQuestions"),
    path('question/create',API_v0.createQuestion,name="API_v0_createQuestion"),
    path('exams/create',API_v0.createExam,name="createExam"),
    path('exams/create/auto',API_v0.createQuestions,name="createQuestions"),
    path('exams',API_v0.listExams,name="listExams"),
    path('exams/show',API_v0.showExam,name="showExam")
    
]