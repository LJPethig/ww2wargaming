from django.shortcuts import render

from .models import Vehicle, Nationality, VehicleType


TYPE_GROUPS = {
    "tank": ("Tank", [VehicleType.TANK]),
    "tank_destroyer": ("Tank Destroyer", [VehicleType.TANK_DESTROYER]),
    "sp_gun": ("SP Gun", [VehicleType.SP_GUN]),
    "armoured_car": ("Armoured Car", [VehicleType.ARMOURED_CAR]),
    "armoured_half_track": ("Armoured Half Track", [VehicleType.ARMOURED_HALF_TRACK]),
    "transport": ("Transport", [VehicleType.TRUCK, VehicleType.PRIME_MOVER]),
    "utility": ("Utility", [VehicleType.JEEP, VehicleType.MOTORCYCLE, VehicleType.CARRIER]),
}


def menu_view(request):
    return render(request, "vehicles/menu.html")


def nationality_list_view(request):
    nationalities = Nationality.choices
    return render(request, "vehicles/nationality_list.html", {
        "nationalities": nationalities,
    })

def type_list_view(request, nationality):
    return render(request, "vehicles/type_list.html", {
        "type_groups": TYPE_GROUPS,
        "nationality": nationality,
    })

def vehicle_list_view(request, nationality, type_group):
    label, type_values = TYPE_GROUPS[type_group]
    vehicles = Vehicle.objects.filter(nationality=nationality, type__in=type_values)
    return render(request, "vehicles/vehicle_list.html", {
        "vehicles": vehicles,
        "nationality": nationality,
        "type_group_label": label,
    })