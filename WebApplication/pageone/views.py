from django.shortcuts import render, redirect
from django.http import HttpResponse
# Create your views here.
def login(request):
    if request.method=='POST':
        username = request.POST['username']
        password = request.POST['password']
        return redirect('/home')
    else:
        return render(request,"login.html")