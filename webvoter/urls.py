"""webvoter URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.1/topics/http/urls/
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
import vote.views

urlpatterns = [
    path('admin/', admin.site.urls),
    # path('', vote.views.create_election, name='create-election'),
    path('', vote.views.CreateElectionView.as_view(), name='create-election'),
    
    path('<int:election_id>/', vote.views.create_ballot, name='create-ballot'),
    path('<int:election_id>/results/<str:etype>/', vote.views.ResultsView.as_view(), name='view-results-etype'),
    # path('<int:election_id>/results/', vote.views.view_results, name='view-results'),
    path('<int:election_id>/results/', vote.views.ResultsView.as_view(), name='view-results'),

    path('view/', vote.views.ElectionListView.as_view(), name='view'),
    path('test/', vote.views.test_crispy, name='test-crispy'),
]
