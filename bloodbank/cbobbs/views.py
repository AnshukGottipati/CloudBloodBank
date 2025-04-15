from django.shortcuts import render

# Create your views here.
def home(request):
    return render(request, "index.html")
    
def find_centers(request):
    return render(request, "find-centers.html")