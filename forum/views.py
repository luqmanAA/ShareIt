from django.shortcuts import render
from django.views import View
# Create your views here.


class FeedView(View):

    def get(self, request):
        return render(request, 'forum/index.html')