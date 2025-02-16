from django.shortcuts import render
from django.http import JsonResponse
# Create your views here.
def upload_file_page(request):
    return render(request, 'AssetApp/upload_file.html')

def parse_file(request):
    if request.method == 'POST' and request.FILES.get('file'):
        # Example logic to handle uploaded files server-side if needed
        return JsonResponse({'message': 'File uploaded successfully'})
    return JsonResponse({'error': 'No file uploaded'}, status=400)
