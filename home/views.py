from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render

@login_required
def index(request):
    if(request.user.is_staff):
        return render(request, "portfolio/staff.html")
    else:
        return redirect('dashboard')
    
def demo(request):
    return render(request, "home/demo.html")