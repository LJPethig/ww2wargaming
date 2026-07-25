from django.shortcuts import render

from .models import Vehicle, Nationality, VehicleType, WeaponRole


TYPE_GROUPS = {
    "tank": ("Tank", [VehicleType.TANK]),
    "tank_destroyer": ("Tank Destroyer", [VehicleType.TANK_DESTROYER]),
    "sp_gun": ("SP Gun", [VehicleType.SP_GUN]),
    "armoured_car": ("Armoured Car", [VehicleType.ARMOURED_CAR]),
    "armoured_half_track": ("Armoured Half Track", [VehicleType.ARMOURED_HALF_TRACK]),
    "transport": ("Transport", [VehicleType.TRUCK, VehicleType.PRIME_MOVER]),
    "utility": ("Utility", [VehicleType.JEEP, VehicleType.MOTORCYCLE, VehicleType.CARRIER]),
}

WEAPON_ROLE_ORDER = [
    WeaponRole.MAIN_ARMAMENT,
    WeaponRole.SECONDARY_ARMAMENT,
    WeaponRole.COAXIAL_MACHINE_GUN,
    WeaponRole.BOW_MACHINE_GUN,
    WeaponRole.PINTLE_MACHINE_GUN,
]

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

    return render(request, "vehicles/_vehicle_grid.html", {
        "vehicles": vehicles,
        "type_group_label": label,
        "nationality": nationality,
    })

def vehicle_detail_view(request, pk):
    vehicle = Vehicle.objects.get(pk=pk)

    capacity_by_caliber = {
        ac.caliber_mm: ac.capacity for ac in vehicle.ammo_capacity.all()
    }

    mounts = list(
        vehicle.hull_weapon_mounts.select_related("weapon").prefetch_related("weapon__ammo__ballistics")
    ) + list(
        vehicle.superstructure_weapon_mounts.select_related("weapon").prefetch_related("weapon__ammo__ballistics")
    )
    mounts.sort(key=lambda m: WEAPON_ROLE_ORDER.index(m.role))

    ammo_ballistics = {}
    for mount in mounts:
        mount.ammo_capacity = capacity_by_caliber.get(mount.weapon.caliber_mm)
        for ammo in mount.weapon.ammo.all():
            if ammo.pk not in ammo_ballistics:
                ammo_ballistics[ammo.pk] = [
                    {
                        "range_m": b.range_m,
                        "pen_0": b.penetration_mm_0deg,
                        "pen_30": b.penetration_mm_30deg,
                        "hit_pct": b.hit_probability_direct_fire_pct,
                    }
                    for b in ammo.ballistics.all()
                ]

    return render(request, "vehicles/vehicle_detail.html", {
        "vehicle": vehicle,
        "weapon_mounts": mounts,
        "ammo_ballistics": ammo_ballistics,
    })