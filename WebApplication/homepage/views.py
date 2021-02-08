from django.shortcuts import render, redirect

# Create your views here.
def home(request):
        if request.method == 'POST':
                return redirect('/home/test')
        return render(request,"home.html")


def test(request):
        return render(request,"login.html")