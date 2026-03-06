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
    path('exams',API_v0.listExams,name="listExams"),
    path('exams/download',API_v0.download,name="download"),
    path('classes',API_v0.listclassRooms,name="listclassRooms"),
    path('classes/join',API_v0.listclassRooms,name="listclassRooms"),
    path('classes/create',API_v0.createClassRoom,name="createClassRoom"),
    path('classes/get/attachments',API_v0.listAttachment,name="listAttachment"),
    path('classes/upload/attachments',API_v0.uploadAttachment,name="uploadAttachment"),
    path('classes/assign/exam',API_v0.assignExamToClassRoom,name="assignExamToClassRoom"),
    path('classes/committe/create',API_v0.createCommitte,name="createCommitte"),
    path('committe/create',API_v0.assignExamToClassRoom,name="assignExamToClassRoom"),
    path('committe/join',API_v0.joinCommitte,name="joinCommitte"),
    path('committe/start',API_v0.startCommitte,name="startCommitte"),
    path('committe/exam/show',API_v0.showExam,name="showExam"),
    path('committe/exam/solve',API_v0.solveExam,name="solveExam"),
    path('store/<slug:username>',API_v0.store,name="store")
]