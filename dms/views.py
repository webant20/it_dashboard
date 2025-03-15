from django.shortcuts import render, redirect
from .forms import DocumentForm
from .models import Document
from django.contrib.contenttypes.models import ContentType

def upload_document(request):
    if request.method == 'POST':
        form = DocumentForm(request.POST, request.FILES)
        if form.is_valid():
            file = form.cleaned_data['file']
            model_type_id = form.cleaned_data['model_type']
            object_ids = form.cleaned_data['related_objects']
            content_type = ContentType.objects.get(id=model_type_id)

            for object_id in object_ids:
                document = Document(file=file, content_type=content_type, object_id=object_id)
                document.save()
            return redirect('success_url')
    else:
        form = DocumentForm()
    return render(request, 'dms/upload.html', {'form': form})
