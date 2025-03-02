from rest_framework.response import Response
from rest_framework.decorators import api_view


@api_view(["GET"])
def home(request):
    port = request.META['SERVER_PORT']
    
    # Print the port number to the console for verification
    print(f"Port number: {port}")
    return Response({"Message":"Welcome the home page"})

@api_view(["GET","POST"])
def error(request):
    port = request.META['SERVER_PORT']
    
    # Print the port number to the console for verification
    print(f"Port number: {port}")
    return Response({"Message":"no such path"})