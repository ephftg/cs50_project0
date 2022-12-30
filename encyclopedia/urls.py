from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    # add link to each entry page 
    path("wiki/<str:input_title>", views.entry_page, name='entry_page'),
    # link when clicking on random page that will redirect to randomly chosen available page 
    path("random_page", views.random_page, name='random_page'),
    # link after user key in input in search bar
    path("search_result", views.search_result, name='search_result'),
    # link to a page to allow user to create add new entry
    path("create_new", views.create_new, name='create_new'),
    # link from page to allow user to edit markdown content of page
    path("edit_page/<str:current_title>", views.edit_page, name='edit_page')
]
