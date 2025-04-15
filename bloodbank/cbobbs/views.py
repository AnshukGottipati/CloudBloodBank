from django.shortcuts import render

# Create your views here.
def home(request):
    return render(request, "index.html")
    
def find_bloodbanks(request):
    return render(request, "find-bloodbanks.html")

def login(request):
    return render(request, "login.html")