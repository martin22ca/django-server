from django.urls import path
from gsalud.views.feedback_views import register_feedback, get_feeback, update_feedback,remove_feedback

urlpatterns = [
    path('', get_feeback),
    path('register', register_feedback),
    path('remove', remove_feedback),
    path('update',update_feedback )
]
