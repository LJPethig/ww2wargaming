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


def browse_view(request):
    counts = {
        nat_value: {
            key: Vehicle.objects.filter(nationality=nat_value, type__in=types).count()
            for key, (label, types) in TYPE_GROUPS.items()
        }
        for nat_value, _ in Nationality.choices
    }

    return render(request, "vehicles/browse.html", {
        "nationalities": Nationality.choices,
        "type_groups": TYPE_GROUPS,
        "counts": counts,
    })


def vehicle_grid_view(request):
    nationality = request.GET.get("nationality")
    type_group = request.GET.get("type_group")

    if not nationality or type_group not in TYPE_GROUPS:
        return render(request, "vehicles/_vehicle_grid.html", {"vehicles": None})

    label, types = TYPE_GROUPS[type_group]
    vehicles = Vehicle.objects.filter(nationality=nationality, type__in=types)
    vehicles = list(vehicles) * 20  # TEMP: repeat for scroll testing, remove after
    
    return render(request, "vehicles/_vehicle_grid.html", {
        "vehicles": vehicles,
        "type_group_label": label,
        "nationality": nationality,
    })