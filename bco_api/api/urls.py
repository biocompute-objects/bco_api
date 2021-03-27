from django.urls import path
from .views import BcoPostObject, BcoGetObject

# We only allow the 4 stand Create, Read, Update, and Delete (CRUD) commands + the BCO ID resolver to
# view an object directly.

urlpatterns = [
    path('bco/objects/create/', BcoPostObject.as_view()),
    path('bco/objects/read/', BcoPostObject.as_view()),
    path('api/description/permissions/', BcoPostObject.as_view()),
    path('api/description/validations/schema/', BcoGetObject.as_view()),
    path('<str:object_id_root>/<str:object_id_version>', BcoGetObject.as_view())
]

# Future URLs:  account/services -> which services are available for your account?
# split bco/objects/create into multiple URLs?
# api/description/databases -> describe the available databases
# api/description/validations/schema -> what are the available templates for this API?
