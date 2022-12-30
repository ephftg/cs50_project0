from django.shortcuts import render

from . import util
from django.http import HttpResponse, HttpResponseRedirect
from django.urls import reverse


def index(request):
    return render(request, "encyclopedia/index.html", {
        "entries": util.list_entries()
    })

# import markdown2 that convert markdown language to html format
import markdown2
# function to display each entry page depending on input_title 
def entry_page(request, input_title):
    if input_title in util.list_entries():
        content = util.get_entry(input_title) # get Markdown content
        html = markdown2.markdown(content) # convert Markdown content to html format
        # render in the html format into the html template, by adding {{Title|safe}} and {{content|safe}}
        # wihtin in the block, the |safe ensures that the html string will be outputted
        return render(request, "encyclopedia/entry_page.html", {"Title" : input_title, "content":html})
    else:
        return render(request,"encyclopedia/errorpage.html")

# import random package to generate random number 
import random
# function to randomly show a page among all entries when clicking on random page link
def random_page(request):
    allentries = util.list_entries()
    n = len(allentries) # get the total number of entries
    x = random.randrange(n) # get an integer from 0 to n-1
    # redirect to any random entry page with the input as the randomly chosen title using kwargs=
    return HttpResponseRedirect(reverse('entry_page',  kwargs={'input_title': allentries[x]}))


# function to search if input is among names of entries list, else suggest entries where search term 
# is contained within substring or else return no matches found
def search_result(request):
    # get the query them using the name of the query 
    query = request.GET['q'].lower()
    allentries = util.list_entries()
    # turn all to small letter first so that all upper/lower case does not affect search result
    # turn to dictonary to keep original to link back to saved entry
    entries_lower = [x.lower() for x in allentries]
    # allentries will be value, entries_lower is keys
    entries_dict = dict(zip(entries_lower, allentries))

    # search input is a get request with name of variable as q, if exist then redirect to exisitng page
    #query = gotquery.lower()  # turn to lower case first
    if query in entries_dict.keys():
        return HttpResponseRedirect(reverse('entry_page',  kwargs={'input_title': entries_dict[query]}))
    else:  # if search input is not among existing page, look for substring
        # generate all substring for each entry 
        substrings_list = [[e[i: j] for i in range(
            len(e)) for j in range(i+1, len(e)+1)] for e in entries_lower]
        substring_dict = dict(zip(allentries, substrings_list))
        # collect all eligible entries and put in html
        got_substring = []
        for k, v in substring_dict.items():
            if query in v:
                got_substring.append(k)

        return render(request, "encyclopedia/search_page.html", {"got_substring": got_substring})


from django import forms
from django.utils.safestring import mark_safe
# create a new class NewPageForm to allow user to input in details of new entry 
class NewPageForm(forms.Form):
    # user need to input title of new page
    # input_title is variable name for the title input
    input_title = forms.CharField(label="Title") # label will be the name beside the input box

    # this is a Textarea that has multi line box so allow user to fill in content of page 
    # provide user instruction to write content in Markdown language
    input_content = forms.CharField(label="Content", widget=forms.Textarea(attrs=
    {'placeholder':'Enter content of page in Markdown format'}))

# create new page function
def create_new(request):
    # if request is post, where user submit the new page entry
    if request.method == 'POST':
        
        # get input title and check if the page already exist 
        fill_form = NewPageForm(request.POST) 
        if fill_form.is_valid(): # check is user input are valid
            entry_title = fill_form.cleaned_data['input_title'] # select input_title 
            allentries = util.list_entries() # get all entries name
            allentries_lower = [x.lower() for x in allentries]
            # create dictionary 
            allentries_dict = dict(zip(allentries_lower,allentries))

            # if entry already exists 
            if entry_title.lower() in allentries_lower: # if entry already exists
                # return the filled up form back to user so that they can edit it
                return render(request, "encyclopedia/create_new.html", {
                    "newpageform": fill_form, "error": True, "entry_title": allentries_dict[entry_title.lower()]})
            
            else: # if entry does not exist, create a new entry page and redirect user to the new page created
                util.save_entry(title=entry_title, content=fill_form.cleaned_data['input_content'])
                return HttpResponseRedirect(reverse('entry_page',  kwargs={'input_title': entry_title}))


    return render(request, "encyclopedia/create_new.html", {"newpageform": NewPageForm()}) 


# page to allow user to edit markdown content of page
def edit_page(request, current_title):

    content = util.get_entry(current_title)

    if request.method == 'POST':
        updated = request.POST['updated_content']
        util.save_entry(title=current_title, content=updated)
        return HttpResponseRedirect(reverse('entry_page',  kwargs={'input_title': current_title}))

    return render(request,'encyclopedia/edit_page.html', {"title":current_title, "content":content})