from django.http.response import HttpResponseNotAllowed, HttpResponseBadRequest, JsonResponse

from archive.models import RecordTag


def tag_autocomplete(request):
    if request.method != 'GET':
        return HttpResponseNotAllowed(['GET'])

    q = request.GET.get('q')
    if not q:
        return HttpResponseBadRequest()

    tags = RecordTag.objects.filter(name__istartswith=q)
    data = [{'name': tag.name} for tag in tags]
    return JsonResponse(data, status=200, safe=False)
