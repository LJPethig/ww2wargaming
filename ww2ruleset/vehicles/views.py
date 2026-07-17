from django.shortcuts import render

from .models import Vehicle, Nationality, VehicleType


def menu_view(request):
    return render(request, "vehicles/menu.html")


def nationality_list_view(request):
    nationalities = Nationality.choices
    return render(request, "vehicles/nationality_list.html", {
        "nationalities": nationalities,
    })


def type_list_view(request, nationality):
    vehicle_types = VehicleType.choices
    return render(request, "vehicles/type_list.html", {
        "vehicle_types": vehicle_types,
        "nationality": nationality,
    })


def vehicle_list_view(request, nationality, vehicle_type):
    vehicles = Vehicle.objects.filter(nationality=nationality, type=vehicle_type)
    return render(request, "vehicles/vehicle_list.html", {
        "vehicles": vehicles,
        "nationality": nationality,
        "vehicle_type": vehicle_type,
    })