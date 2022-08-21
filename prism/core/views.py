from django.shortcuts import render


def page_not_found_view(request, exception):
    context = {
        "status_code": 404,
        "error_msg": "Page not found"
    }
    return render(request, "errors/error.html", context, status=404)

def server_error_view(request, exception=None):
    context = {
        "status_code": 500,
        "error_msg": "Server error"
    }
    return render(request, "errors/error.html", context, status=500)

def permission_denied_view(request, exception=None):
    context = {
        "status_code": 403,
        "error_msg": "Permission denied"
    }
    return render(request, "errors/error.html", context, status=403)

def bad_request_view(request, exception=None):
    context = {
        "status_code": 400,
        "error_msg": "Bad request"
    }
    return render(request, "errors/error.html", context, status=400)