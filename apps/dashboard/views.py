from django.shortcuts import render

def orchestra_view(request):
    return render(request, 'dashboard/orchestra.html', {})