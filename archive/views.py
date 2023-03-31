from django.urls import reverse_lazy
from django.shortcuts import render
from django.views.generic import ListView, DetailView
from django.views.generic.edit import CreateView, DeleteView, UpdateView
from django.shortcuts import get_object_or_404
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.utils.translation import gettext as _
from django.http import HttpResponseRedirect, HttpResponseNotAllowed, HttpResponseBadRequest
from django.db.models import Q
from django.contrib.auth.decorators import permission_required, login_required

from archive.models import RecordCategory, Collection, Record, RecordFile, RecordTag
from archive.forms import RecordFileForm, RecordTagForm
from archive.upload_helper import get_content_type
from archive.filters import RecordFilter
from archive.tasks import generate_preview


class CategoryListView(LoginRequiredMixin, ListView):
    model = RecordCategory
    template_name = 'archive/category_list.html'
    context_object_name = 'category_list'


class CategoryDetailView(LoginRequiredMixin, DetailView):
    model = RecordCategory
    template_name = 'archive/category_detail.html'
    context_object_name = 'category'


class CategoryCreateView(PermissionRequiredMixin, CreateView):
    model = RecordCategory
    fields = ['name']
    template_name = 'generic_form.html'
    permission_required = 'archive.add_recordcategory'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['heading'] = _('Create Category')
        return context


class CategoryUpdateView(PermissionRequiredMixin, UpdateView):
    model = RecordCategory
    fields = ['name']
    template_name = 'generic_form.html'
    permission_required = 'archive.change_recordcategory'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['heading'] = _('Edit Category')
        return context


class CategoryDeleteView(PermissionRequiredMixin, DeleteView):
    model = RecordCategory
    template_name = 'generic_confirm_delete.html'
    success_url = reverse_lazy('category-list')
    permission_required = 'archive.delete_recordcategory'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['object_type'] = _('Category')
        return context


class CollectionListView(ListView):
    model = Collection

    def get_queryset(self):
        if not self.request.user or not self.request.user.is_authenticated:
            return Collection.objects.filter(public=True)
        return Collection.objects.all()


class CollectionDetailView(DetailView):
    model = Collection

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        if self.request.user.is_authenticated:
            queryset = Record.objects.filter(collection=context['collection'])
        else:
            queryset = Record.objects.filter(collection=context['collection'], public=True)

        context['record_filter'] = RecordFilter(self.request.GET,
                                                queryset=queryset)
        return context

    def get_queryset(self):
        if not self.request.user or not self.request.user.is_authenticated:
            return Collection.objects.filter(public=True)
        return Collection.objects.all()


class CollectionCreateView(LoginRequiredMixin, PermissionRequiredMixin, CreateView):
    model = Collection
    fields = ['name', 'description', 'public']
    template_name = 'generic_form.html'
    permission_required = 'archive.add_collection'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['heading'] = _('Create Collection')
        return context


class CollectionUpdateView(LoginRequiredMixin, PermissionRequiredMixin, UpdateView):
    model = Collection
    fields = ['name', 'description', 'public']
    template_name = 'generic_form.html'
    permission_required = 'archive.change_collection'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['heading'] = _('Edit Collection')
        return context


class CollectionDeleteView(LoginRequiredMixin, PermissionRequiredMixin, DeleteView):
    model = Collection
    template_name = 'generic_confirm_delete.html'
    success_url = reverse_lazy('collection-list')
    permission_required = 'archive.delete_collection'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['object_type'] = _('Collection')
        return context


class RecordDetailView(DetailView):
    model = Record

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['file_form'] = RecordFileForm()
        context['tag_form'] = RecordTagForm()
        return context

    def get_queryset(self):
        if not self.request.user or not self.request.user.is_authenticated:
            return Record.objects.filter(collection_id=self.kwargs['collection_id'], collection__public=True,
                                         public=True)
        return Record.objects.filter(collection_id=self.kwargs['collection_id'])


class RecordCreateView(LoginRequiredMixin, PermissionRequiredMixin, CreateView):
    model = Record
    fields = ['title', 'category', 'description', 'physical_location', 'physical_signature', 'origin_date', 'public']
    template_name = 'generic_form.html'
    permission_required = 'archive.add_record'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['heading'] = _('Create Record')
        return context

    def form_valid(self, form):
        collection = get_object_or_404(Collection, pk=self.kwargs['collection_id'])
        form.instance.collection = collection
        return super().form_valid(form)


class RecordUpdateView(LoginRequiredMixin, PermissionRequiredMixin, UpdateView):
    model = Record
    fields = ['title', 'category', 'description', 'physical_location', 'physical_signature', 'origin_date', 'public']
    template_name = 'generic_form.html'
    permission_required = 'archive.change_record'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['heading'] = _('Edit Record')
        return context


class RecordDeleteView(LoginRequiredMixin, PermissionRequiredMixin, DeleteView):
    model = Record
    template_name = 'generic_confirm_delete.html'
    permission_required = 'archive.delete_record'

    def get_success_url(self):
        return reverse_lazy('collection-detail', kwargs={'pk': self.kwargs['collection_id']})

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['object_type'] = _('Record')
        return context


class RecordFileDeleteView(LoginRequiredMixin, PermissionRequiredMixin, DeleteView):
    model = RecordFile
    template_name = 'generic_confirm_delete.html'
    permission_required = 'archive.delete_recordfile'

    def get_success_url(self):
        return reverse_lazy('record-detail', kwargs={'collection_id': self.kwargs['collection_id'],
                                                     'pk': self.kwargs['record_id']})

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['object_type'] = _('Record File')
        return context


class RecordTagCreateView(LoginRequiredMixin, CreateView):
    model = RecordTag
    template_name = 'generic_form.html'
    fields = ['name']

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['heading'] = _('Create Tag')
        return context


def search_view(request):
    q = request.GET.get('q')

    if not q:
        return render(request, 'archive/search.html', {'error': _('Search query is required')})

    queryset = Record.objects.filter(Q(title__icontains=q) | Q(description__icontains=q))

    if not request.user or not request.user.is_authenticated:
        queryset = queryset.filter(public=True, collection__public=True)

    return render(request, 'archive/search.html', {'records': queryset, 'q': q})


def add_tag_view(request, collection_id, pk):
    if request.method != 'POST':
        return HttpResponseNotAllowed(['POST'])
    record = get_object_or_404(Record, pk=pk, collection_id=collection_id)
    form = RecordTagForm(request.POST)
    if form.is_valid():
        tag = form.cleaned_data['tag']
        record.tags.add(tag)
        record.save()
        return HttpResponseRedirect(record.get_absolute_url())
    return HttpResponseBadRequest()


@login_required
@permission_required('archive.add_recordfile', raise_exception=True)
def upload_record_file(request, collection_id, record_id):
    if request.method == 'POST':
        form = RecordFileForm(request.POST, request.FILES)
        record = get_object_or_404(Record, pk=record_id)
        if form.is_valid():
            file = form.cleaned_data['file']
            form.instance.content_type = get_content_type(file)
            form.instance.record = record
            form.save()
            generate_preview.delay(form.instance.pk)
            return HttpResponseRedirect(record.get_absolute_url())
