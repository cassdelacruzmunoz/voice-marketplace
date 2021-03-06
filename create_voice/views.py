import random
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponse, HttpResponseBadRequest
from django.shortcuts import render
from django.utils import timezone
from django.views import generic
from .models import Recording
from .forms import RecordingForm


# Create your views here.
class IndexView(LoginRequiredMixin, generic.ListView):
    template_name = 'create_voice/index.html'
    context_object_name = 'list_of_recordings'

    def get_queryset(self):
        return Recording.objects.filter(user_value=self.request.user).order_by('-rec_date')


class DetailView(LoginRequiredMixin, generic.DetailView):
    model = Recording
    template_name = 'create_voice/detail.html'
    context_object_name = 'recording'

    def get_queryset(self):
        return Recording.objects.filter(user_value=self.request.user)


class RecordView(LoginRequiredMixin, generic.ListView):
    model = Recording
    text = random.choice(open('clips.csv').read().splitlines())
    template_name = 'create_voice/record.html'
    context_object_name = 'text'

    def get_queryset(self):
        return self.text


class PromptView(generic.ListView):
    template_name = 'create_voice/prompt.html'
    context_object_name = 'text'

    def get_queryset(self):
        return random.choice(open('clips.csv').read().splitlines())


class RecieveRecordingView(generic.ListView):
    model = Recording

    @staticmethod
    def post(request):
        form = RecordingForm(request.POST, request.FILES)
        if form.is_valid():
            recording = Recording()
            recording.text = form.cleaned_data['text']
            recording.rec_date = timezone.now()
            recording.user_value = request.user
            recording.save()
            recording.voice_record = form.files['audio_data']
            recording.save()
            return HttpResponse('Ok')
        return HttpResponseBadRequest('')


@login_required
def delete_recording(request, pk=None):
    object = Recording.objects.get(id=pk)
    object.delete()
    return render(request, 'create_voice/index.html')
