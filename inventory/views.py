from django.http import HttpResponse

# Stub views — will be implemented fully later
def inventory_list(request):
    return HttpResponse('inventory_list stub')

def inventory_detail(request, user_pk):
    return HttpResponse('inventory_detail stub')

def inventory_allocate(request, user_pk):
    return HttpResponse('inventory_allocate stub')

def my_inventory(request):
    return HttpResponse('my_inventory stub')

def my_inventory_checkout(request):
    return HttpResponse('my_inventory_checkout stub')
