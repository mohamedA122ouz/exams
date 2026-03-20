from django.urls import path, include
from django.contrib.auth import views as authViews
from core.controllers import API_v0, home



urlpatterns = [
    path('login',home.userLogin,name="v0_login"),
    path('user/create',home.createUser,name="v0_createUser"),
    path('logout/',authViews.LogoutView.as_view(),name='v0_logout'),
    path('terms',API_v0.showTerms, name="v0_showTerms"),
    path('terms/create',API_v0.createTerm,name="v0_createTerm"),
    path('years',API_v0.showYears,name="v0_showYears"),
    path('years/create',API_v0.createYear,name="v0_createYear"),
    path('subjects/create',API_v0.createSubject,name="v0_createSubject"),
    path('subjects',API_v0.showSubjects,name="v0_showSubjects"),
    path('lectures',API_v0.showLectures,name="v0_showLectures"),
    path('lectures/create',API_v0.createLectures,name="v0_createLectures"),
    path('questions',API_v0.showQuestions,name="v0_showQuestions"),
    path('question/create',API_v0.createQuestion,name="v0_createQuestion"),
    path('questions/create',API_v0.createQuestions,name="v0_createQuestions"),
    path('exams/create',API_v0.createExam,name="v0_createExam"),
    path('exams',API_v0.listExams,name="v0_listExams"),
    path('exam/show',API_v0.showExamOutOfCommit,name="v0_showExamOutOfCommit"),
    path('exams/download',API_v0.download,name="v0_download"),
    path('classes',API_v0.listclassRooms,name="v0_listclassRooms"),
    path('classes/join',API_v0.listclassRooms,name="v0_listclassRooms"),
    path('classes/create',API_v0.createClassRoom,name="v0_createClassRoom"),
    path('classes/get/attachments',API_v0.listAttachment,name="v0_listAttachment"),
    path('classes/upload/attachments',API_v0.uploadAttachment,name="v0_uploadAttachment"),
    path('classes/assign/exam',API_v0.assignExamToClassRoom,name="v0_assignExamToClassRoom"),
    path('classes/committe/create',API_v0.createCommitte,name="v0_createCommitte"),
    path('committe/create',API_v0.assignExamToClassRoom,name="v0_assignExamToClassRoom"),
    path('committe/join',API_v0.joinCommitte,name="v0_joinCommitte"),
    path('committe/start',API_v0.startCommitte,name="v0_startCommitte"),
    path('committe/exam/show',API_v0.showExam,name="v0_showExam"),
    path('committe/exam/solve',API_v0.solveExam,name="v0_solveExam"),
]