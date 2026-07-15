from django.contrib import admin, messages
from django.utils.safestring import mark_safe

from .models import (
    Ammo, AmmoBallistics, Weapon, HullWeaponMount,
    SuperstructureWeaponMount, CrewMember, HullArmour,
    SuperStructure, Vehicle, VehicleAmmoCapacity,
)


class AmmoBallisticsInline(admin.TabularInline):
    model = AmmoBallistics
    extra = 0
    max_num = 8
    can_delete = False
    fields = ("range_m", "penetration_mm_0deg", "penetration_mm_30deg", "hit_probability_direct_fire_pct")
    readonly_fields = ("range_m",)


@admin.register(Ammo)
class AmmoAdmin(admin.ModelAdmin):
    list_display = ("name", "ammo_type", "caliber_mm", "nationality")
    list_filter = ("ammo_type", "nationality", "caliber_mm")
    search_fields = ("name",)
    inlines = [AmmoBallisticsInline]

    def get_fieldsets(self, request, obj=None):
        fieldsets = [
            (None, {"fields": ("name", "ammo_type", "nationality", "caliber_mm")}),
            ("Blast data — HE rounds only (leave blank for AP / APCR / BALL)", {"fields": (
                "burst_radius_99pct_m", "burst_radius_66pct_m", "burst_radius_33pct_m",
                "blast_armour_penetration_mm", "blast_armour_penetration_range_m",
            )}),
        ]
        if obj is None:
            fieldsets.insert(1, (None, {"fields": ("ballistics_note",)}))
        return fieldsets

    def ballistics_note(self, obj=None):
        return mark_safe(
            "<strong>Note:</strong> the 8 ballistics range-band rows (100m&ndash;2400m) are "
            "created automatically once you save this record for the first time. "
            "Save now, then fill in the penetration and hit-probability data below."
        )
    ballistics_note.short_description = ""

    def get_readonly_fields(self, request, obj=None):
        readonly = super().get_readonly_fields(request, obj)
        if obj is None:
            readonly = (*readonly, "ballistics_note")
        return readonly

    def response_add(self, request, obj, post_url_continue=None):
        # Plain "Save" normally goes to the changelist, not the record —
        # force it to redirect to the change page instead, so the new
        # ballistics rows are visible without reopening the record.
        if "_continue" not in request.POST and "_addanother" not in request.POST and "_saveasnew" not in request.POST:
            # Make Django's own response_add think "Save and continue
            # editing" was clicked, so it computes the redirect correctly.
            request.POST = request.POST.copy()
            request.POST["_continue"] = True
        messages.info(
            request,
            f"'{obj}' saved. The 8 ballistics range rows are now ready below — fill them in and save again.",
        )
        return super().response_add(request, obj, post_url_continue=post_url_continue)

@admin.register(Weapon)
class WeaponAdmin(admin.ModelAdmin):
    list_display = ("name", "weapon_type", "caliber_mm", "nationality")
    list_filter = ("weapon_type", "nationality", "caliber_mm")
    search_fields = ("name",)
    filter_horizontal = ("ammo",)

class CrewMemberInline(admin.TabularInline):
    model = CrewMember
    extra = 1


class HullArmourInline(admin.StackedInline):
    model = HullArmour
    extra = 0
    max_num = 1 # OneToOne — at most one armour record per vehicle
    can_delete = True   # allows removing armour if a vehicle turns out to be unarmoured
    verbose_name = "Hull Armour — Only for armoured vehicles"
    fieldsets = (
        ("Armour Thickness (mm) - leave empty if plate doesn't exist", {
            "fields": (
                "armour_front_lower_mm", "armour_front_upper_mm",
                "armour_front_top_mm", "armour_mid_top_mm",
                "armour_lh_side_upper_mm", "armour_rh_side_upper_mm",
                "armour_lh_side_lower_mm", "armour_rh_side_lower_mm",
                "armour_rear_lower_mm", "armour_rear_upper_mm", "armour_rear_top_mm",
            ),
        }),
        ("Armour Slope (degrees) — 0° = plate is vertical or horizontal", {
            "fields": (
                "armour_front_lower_deg", "armour_front_upper_deg",
                "armour_front_top_deg", "armour_mid_top_deg",
                "armour_lh_side_upper_deg", "armour_rh_side_upper_deg",
                "armour_lh_side_lower_deg", "armour_rh_side_lower_deg",
                "armour_rear_lower_deg", "armour_rear_upper_deg", "armour_rear_top_deg",
            ),
        }),
        ("Applique Armour (mm) — if fitted; slope derived from the underlying plate", {
            "fields": (
                "armour_front_lower_applique_mm", "armour_front_upper_applique_mm",
                "armour_lh_side_upper_applique_mm", "armour_rh_side_upper_applique_mm",
                "armour_lh_side_lower_applique_mm", "armour_rh_side_lower_applique_mm",
            ),
        }),
        ("Spaced Armour (mm) — if fitted; slope is always 0°", {
            "fields": (
                "armour_front_upper_spaced_mm",
                "armour_lh_side_upper_spaced_mm", "armour_rh_side_upper_spaced_mm",
                "armour_lh_side_lower_spaced_mm", "armour_rh_side_lower_spaced_mm",
            ),
        }),
        (None, {"fields": ("armour_composition_hull",)}),
    )


class SuperStructureInline(admin.StackedInline):
    model = SuperStructure
    extra = 0
    max_num = 1 # OneToOne — at most one armour record per vehicle
    can_delete = True # allows removing armour if a vehicle turns out to be unarmoured
    verbose_name = "Superstructure — for turret, casemate, fighting compartment, or a raised gun shield/mantlet"
    fieldsets = (
        ("Armour Thickness (mm) - leave empty if plate doesn't exist", {
            "fields": (
                "armour_front_mm", "armour_lh_side_mm", "armour_rh_side_mm",
                "armour_rear_mm", "armour_top_mm", "armour_mantlet_mm",
            ),
        }),
        ("Armour Slope (degrees) — 0° = plate is vertical or horizontal", {
            "fields": (
                "armour_front_deg", "armour_lh_side_deg", "armour_rh_side_deg",
                "armour_rear_deg", "armour_top_deg", "armour_mantlet_deg",
            ),
        }),
        ("Applique Armour (mm) — if fitted; slope derived from the underlying plate", {
            "fields": (
                "armour_mantlet_applique_mm", "armour_front_applique_mm",
                "armour_lh_side_applique_mm", "armour_rh_side_applique_mm",
            ),
        }),
        ("Spaced Armour (mm) — if fitted; slope is always 0°", {
            "fields": (
                "armour_mantlet_spaced_mm", "armour_front_spaced_mm",
                "armour_lh_side_spaced_mm", "armour_rh_side_spaced_mm", "armour_rear_spaced_mm",
            ),
        }),
        (None, {
            "fields": (
                "armour_composition_superstructure", "armour_composition_mantlet",
                "does_rotate", "superstructure_proportion_percent",
            ),
        }),
    )

class HullWeaponMountInline(admin.TabularInline):
    model = HullWeaponMount
    extra = 1
    autocomplete_fields = ["weapon"]


class SuperstructureWeaponMountInline(admin.TabularInline):
    model = SuperstructureWeaponMount
    extra = 1
    autocomplete_fields = ["weapon"]


class VehicleAmmoCapacityInline(admin.TabularInline):
    model = VehicleAmmoCapacity
    extra = 1


@admin.register(Vehicle)
class VehicleAdmin(admin.ModelAdmin):
    list_display = ("name", "type", "nationality", "available_from_year")
    list_filter = ("type", "nationality")
    search_fields = ("name",)

    fieldsets = (
        ("Basic Info", {
            "fields": ("name", "type", "nationality", "available_from_year",
                       "available_from_month", "general_info", "image"),
        }),
        ("Performance & Dimensions", {
            "fields": ("speed_road_kph", "speed_cc_kph", "range_road_km", "range_cc_km",
                       "weight_tonne", "height_m", "length_m", "width_m",
                       "has_radio", "fuel_type", "suspension_type"),
        }),
        ("Internal Layout", {
            "fields": ("engine_position", "final_drive_position",
                       "transmission_position", "fuel_tank_position", "troop_capacity"),
        }),
    )

    inlines = [
        CrewMemberInline,
        HullArmourInline,
        SuperStructureInline,
        HullWeaponMountInline,
        SuperstructureWeaponMountInline,
        VehicleAmmoCapacityInline,
    ]
