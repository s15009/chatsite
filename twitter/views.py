from django.shortcuts import render, render_to_response, reverse
from django.template import RequestContext
from django.contrib.auth.decorators import login_required
from django.http import Http404, HttpResponseRedirect
from django.contrib.auth import login, authenticate

from .forms import MyRegistrationForm
from chatsite.backend import LoginBackend


@login_required
def home(request):
    context = RequestContext(request,{'request': request,'user': request.user})
    #social = request.user.social_auth.get(provider='twitter')
    #twitter_token = social.extra_data['access_token']
    return render_to_response('twitter/home.html')

def new(request):	
    form = MyRegistrationForm()
    return render(request, 'twitter/new.html', {'form': form,})

def create(request):
    if request.method == 'POST':
        form = MyRegistrationForm(request.POST)
        if form.is_valid():
            twitter = form.save()
            login(request, twitter, backend='Loginbackend')
            return HttpResponseRedirect(reverse('chats:index'))
        return render(request, 'twitter/new.html', {'form': form,})
    else:
        raise Http404
