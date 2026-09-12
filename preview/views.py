from django.shortcuts import render
from .hris_parser import parse_hris_csv


def upload_csv(request):
    context = {}

    if request.method == "POST" and request.FILES.get("csv_file"):
        uploaded_file = request.FILES["csv_file"]
        try:
            result = parse_hris_csv(uploaded_file)
            context["result"] = result
        except Exception as e:
            context["fatal_error"] = str(e)

    return render(request, "preview/upload.html", context)