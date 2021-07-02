import django_filters
from django.forms.widgets import TextInput
from .models import CreateJob

class JobSearchFilter(django_filters.FilterSet):
	title = django_filters.CharFilter(lookup_expr='icontains', widget=TextInput(attrs={'placeholder':'Title', 'title':'Search job by title, keywords...'}))
	description = django_filters.CharFilter(lookup_expr='icontains', widget=TextInput(attrs={'placeholder':'Description', 'title':'Search job by description keywords...'}))

	class Meta:
		model = CreateJob
		fields = ['title', 'description']