from django.shortcuts import render
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from .smart_data_cleaner_v2 import SmartDataCleanerV2
import os

CLEANER = None
UPLOAD_PATH = ''

@csrf_exempt
def upload_dataset(request):
    global CLEANER, UPLOAD_PATH
    if request.method == 'POST' and request.FILES.get('dataset'):
        uploaded_file = request.FILES['dataset']
        os.makedirs("uploads", exist_ok=True)
        UPLOAD_PATH = f"uploads/{uploaded_file.name}"
        with open(UPLOAD_PATH, 'wb+') as dest:
            for chunk in uploaded_file.chunks():
                dest.write(chunk)
        CLEANER = SmartDataCleanerV2(UPLOAD_PATH)
        return HttpResponse("File uploaded and loaded successfully!")
    return HttpResponse("No file uploaded.", status=400)

def run_task(request, task):
    global CLEANER
    if not CLEANER:
        return HttpResponse("No dataset loaded.", status=400)
    try:
        if task == 'assess':
            summary = CLEANER.assess_data()
            return HttpResponse(summary.replace('\n', '<br>'))
        elif task == 'outliers':
            report = CLEANER.identify_outliers()
            return HttpResponse(report.replace('\n', '<br>'))
        elif task == 'clean':
            CLEANER.clean(normalize=True, standardize=False)
            return HttpResponse("Cleaning completed.")
        elif task == 'correlation':
            report = CLEANER.correlation_analysis()
            return HttpResponse(report.replace('\n', '<br>'))
        elif task == 'features':
            report = CLEANER.feature_extraction()
            return HttpResponse(report.replace('\n', '<br>'))
        elif task == 'summary':
            report = CLEANER.summary_statistics()
            return HttpResponse(report.replace('\n', '<br>'))
        elif task == 'export':
            out_path = CLEANER.export()
            with open(out_path, 'rb') as f:
                response = HttpResponse(
                    f.read(), 
                    content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
                )
                response['Content-Disposition'] = f'attachment; filename="{os.path.basename(out_path)}"'
                return response
        else:
            return HttpResponse("Invalid task", status=400)
    except Exception as e:
        return HttpResponse(f"Error: {str(e)}", status=500)
