from django.db import models


class Month(models.TextChoices):
    JANUARY = "1", "January"
    FEBRUARY = "2", "February"
    MARCH = "3", "March"
    APRIL = "4", "April"
    MAY = "5", "May"
    JUNE = "6", "June"
    JULY = "7", "July"
    AUGUST = "8", "August"
    SEPTEMBER = "9", "September"
    OCTOBER = "10", "October"
    NOVEMBER = "11", "November"
    DECEMBER = "12", "December"

class CrewRole(models.TextChoices):
    DRIVER = "driver", "Driver"
    BOW_GUNNER = "bow_gunner", "Bow Gunner"             # hull MG; usually combined with radio duty
    RADIO_OPERATOR = "radio_operator", "Radio Operator" # rare as a separate role from bow gunner
    COMMANDER = "commander", "Commander"
    GUNNER = "gunner", "Gunner"
    LOADER = "loader", "Loader"

class CrewCompartment(models.TextChoices):
    HULL = "hull", "Hull"
    SUPERSTRUCTURE = "superstructure", "Superstructure"

class SuperStructureType(models.TextChoices):
    SUPERSTRUCTURE = "superstructure", "Superstructure"
    TURRET = "turret", "Turret"
    CASEMATE = "casemate", "Casemate"
    FIGHTING_COMPARTMENT = "fighting_compartment", "Fighting Compartment"

class MantletType(models.TextChoices):
    MANTLET = "mantlet", "Mantlet"
    GUN_SHIELD = "gun_shield", "Gun Shield"


class Nationality(models.TextChoices):
    GERMAN = "German", "German"
    RUSSIAN = "Russian", "Russian"
    AMERICAN = "American", "American"
    BRITISH = "British", "British"
    FRENCH = "French", "French"

class AmmoType(models.TextChoices):
    AP = "ap", "AP - Armour Piercing"
    APCR = "apcr", "APCR - Armour Piercing, Composite Rigid (tungsten-cored)"
    HE = "he", "HE - High Explosive"
    BALL = "ball", "BALL - Standard small arms"

class WeaponType(models.TextChoices):
    MACHINE_GUN = "machine_gun", "Machine Gun"
    AUTO_CANNON = "auto_cannon", "Auto Cannon"
    CANNON = "cannon", "Cannon"
    HOWITZER = "howitzer", "Howitzer"
    FLAME_THROWER = "flame_thrower", "Flame Thrower"
    ROCKET_LAUNCHER = "rocket_launcher", "Rocket Launcher"

class WeaponRole(models.TextChoices):
    MAIN_ARMAMENT = "main_armament", "Main Armament"                # the vehicles's defining weapon
    SECONDARY_ARMAMENT = "secondary_armament", "Secondary Armament" # e.g. M3 Lee's 75mm sponson gun
    COAXIAL_MACHINE_GUN = "coaxial_machine_gun", "Coaxial Machine Gun"
    BOW_MACHINE_GUN = "bow_machine_gun", "Bow Machine Gun"
    PINTLE_MACHINE_GUN = "pintle_machine_gun", "Pintle Machine Gun"

class ArmourComposition(models.TextChoices):
    ROLLED = "rolled", "Rolled"
    CAST = "cast", "Cast"

class VehicleType(models.TextChoices):
    TANK = "Tank", "Tank"
    SP_GUN = "SP Gun", "SP Gun"
    TANK_DESTROYER = "Tank Destroyer", "Tank Destroyer"
    ARMOURED_HALF_TRACK = "Armoured Half-Track", "Armoured Half-Track"
    ARMOURED_CAR = "Armoured Car", "Armoured Car"
    CARRIER = "Carrier", "Carrier"
    PRIME_MOVER = "Prime Mover", "Prime Mover"
    TRUCK = "Truck", "Truck"
    JEEP = "Jeep", "Jeep"
    MOTORCYCLE = "Motorcycle", "Motorcycle"

class InternalComponentPosition(models.TextChoices):
    FRONT = "front", "Front"
    MID = "mid", "Mid"
    REAR = "rear", "Rear"

class FuelType(models.TextChoices):
    PETROL = "petrol", "Petrol"
    DIESEL = "diesel", "Diesel"

class SuspensionType(models.TextChoices):
    TRACK = "track", "Track"
    HALF_TRACK = "half_track", "Half-Track"
    FOUR_WHEEL = "four_wheel", "Four Wheel"
    SIX_WHEEL = "six_wheel", "Six Wheel"
    EIGHT_WHEEL = "eight_wheel", "Eight Wheel"
    MOTORCYCLE_TWO_WHEEL = "motorcycle_two_wheel", "Motorcycle (Two Wheel)"
    MOTORCYCLE_THREE_WHEEL = "motorcycle_three_wheel", "Motorcycle (Three Wheel)"
    MOTORCYCLE_HALF_TRACK = "motorcycle_half_track", "Motorcycle (Half-Track)"


class CrewMember(models.Model):
    vehicle = models.ForeignKey(
        "Vehicle",
        related_name="crew",
        on_delete=models.CASCADE,
    )
    role = models.CharField(max_length=20, choices=CrewRole.choices)
    compartment = models.CharField(max_length=20, choices=CrewCompartment.choices)

    def __str__(self):
        return f"{self.get_role_display()} ({self.get_compartment_display()})"

    class Meta:
        verbose_name = "Crew Member"
        verbose_name_plural = "Crew Members"

class Ammo(models.Model):
    # range in meters
    RANGE_BANDS_VS_VEHICLE_M = (100, 200, 400, 800, 1200, 1600, 2000, 2400)

    name = models.CharField(max_length=100)
    ammo_type = models.CharField(max_length=10, choices=AmmoType.choices)
    nationality = models.CharField(max_length=20, choices=Nationality.choices)
    caliber_mm = models.FloatField()  # matches Weapon.caliber_mm; enables caliber-filtered ammo selection

    # HE only — blast/fragmentation effects, None for armour piercing type rounds
    # Values are as sourced from wwiitanks.co.uk — precision is limited to
    # whole metres, with 0 being a genuine possible value (not a placeholder).
    # See template comment for how 0 is displayed to the user.
    burst_radius_99pct_m = models.FloatField(null=True, blank=True)
    burst_radius_66pct_m = models.FloatField(null=True, blank=True)
    burst_radius_33pct_m = models.FloatField(null=True, blank=True)
    blast_armour_penetration_mm = models.FloatField(null=True, blank=True)
    blast_armour_penetration_range_m = models.FloatField(null=True, blank=True)

    def save(self, *args, **kwargs):
        # auto-create all 8 fixed range-band rows on first save only,
        # so every Ammo record always has a full, consistent set of
        # range bands ready to display and edit
        is_new = self.pk is None
        super().save(*args, **kwargs)
        if is_new:
            AmmoBallistics.objects.bulk_create([
                AmmoBallistics(ammo=self, range_m=r)
                for r in self.RANGE_BANDS_VS_VEHICLE_M
            ])

    def __str__(self):
        return f"{self.name} ({self.caliber_mm}mm, {self.get_ammo_type_display()}, {self.get_nationality_display()})"

    class Meta:
        verbose_name = "Ammo"
        verbose_name_plural = "Ammo"
        ordering = ["caliber_mm", "nationality", "name"]

class AmmoBallistics(models.Model):
    ammo = models.ForeignKey(Ammo, related_name="ballistics", on_delete=models.CASCADE)
    range_m = models.PositiveIntegerField()

    penetration_mm_0deg = models.FloatField(null=True, blank=True)
    penetration_mm_30deg = models.FloatField(null=True, blank=True)
    # Direct fire hit probability is based on a static 2 x 2.4 metre vertical target at the range specified
    hit_probability_direct_fire_pct = models.FloatField(null=True, blank=True)

    class Meta:
        # prevents two rows for the same range band on the same ammo —
        # mirrors a dict only ever having one value per key
        unique_together = ("ammo", "range_m")
        ordering = ["range_m"]
        verbose_name = "Ammo Ballistics"
        verbose_name_plural = "Ammo Ballistics"

    def __str__(self):
        return f"{self.ammo.name} @ {self.range_m}m"


class Weapon(models.Model):
    name = models.CharField(max_length=100)
    weapon_type = models.CharField(max_length=20, choices=WeaponType.choices)
    nationality = models.CharField(max_length=20, choices=Nationality.choices)
    caliber_mm = models.FloatField()
    length_calibers = models.FloatField()  # the "L/40" style figure
    rate_of_fire_rpm = models.FloatField()  # practical rate of fire, not theoretical max
    ammo = models.ManyToManyField(Ammo, related_name="weapons")


    def __str__(self):
        return f"{self.name} ({self.caliber_mm}mm, {self.get_weapon_type_display()}, {self.get_nationality_display()})"

    class Meta:
        verbose_name = "Weapon"
        verbose_name_plural = "Weapons"
        ordering = ["caliber_mm", "nationality", "name"]

class VehicleAmmoCapacity(models.Model):
    # pools all ammo of this caliber for the entire vehicles, regardless of
    # nationality (simplification: assumes same-caliber = compatible)
    vehicle = models.ForeignKey("Vehicle", related_name="ammo_capacity", on_delete=models.CASCADE)
    caliber_mm = models.FloatField()
    capacity = models.PositiveIntegerField()

    class Meta:
        unique_together = ("vehicle", "caliber_mm")
        verbose_name = "Vehicle Ammo Capacity"
        verbose_name_plural = "Vehicle Ammo Capacities"

    def __str__(self):
        return f"{self.vehicle.name}: {self.caliber_mm}mm x{self.capacity}"

class HullWeaponMount(models.Model):
    # PROTECT, not CASCADE: Weapon is shared reference data used across
    # many vehicles — deleting a Weapon should never silently wipe out
    # every mount that uses it
    vehicle = models.ForeignKey("Vehicle", related_name="hull_weapon_mounts", on_delete=models.CASCADE)
    weapon = models.ForeignKey(Weapon, on_delete=models.PROTECT)
    role = models.CharField(max_length=20, choices=WeaponRole.choices)
    operated_by = models.CharField(max_length=20, choices=CrewRole.choices)

    def __str__(self):
        return f"{self.weapon.name} ({self.get_role_display()})"

    class Meta:
        verbose_name = "Hull Weapon Mount"
        verbose_name_plural = "Hull Weapon Mounts"


class SuperstructureWeaponMount(models.Model):
    # PROTECT, not CASCADE: Weapon is shared reference data used across
    # many vehicles — deleting a Weapon should never silently wipe out
    # every mount that uses it
    vehicle = models.ForeignKey("Vehicle", related_name="superstructure_weapon_mounts", on_delete=models.CASCADE)
    weapon = models.ForeignKey(Weapon, on_delete=models.PROTECT)
    role = models.CharField(max_length=20, choices=WeaponRole.choices)
    operated_by = models.CharField(max_length=20, choices=CrewRole.choices)

    def __str__(self):
        return f"{self.weapon.name} ({self.get_role_display()})"

    class Meta:
        verbose_name = "Superstructure Weapon Mount"
        verbose_name_plural = "Superstructure Weapon Mounts"

class HullArmour(models.Model):
    vehicle = models.OneToOneField("Vehicle", related_name="hull_armour", on_delete=models.CASCADE)
    # hull armour (mm)
    armour_front_lower_mm = models.PositiveSmallIntegerField()
    armour_front_upper_mm = models.PositiveSmallIntegerField()
    armour_front_top_mm = models.PositiveSmallIntegerField(null=True, blank=True)
    armour_mid_top_mm = models.PositiveSmallIntegerField(null=True, blank=True)
    armour_lh_side_upper_mm = models.PositiveSmallIntegerField()
    armour_rh_side_upper_mm = models.PositiveSmallIntegerField()
    armour_lh_side_lower_mm = models.PositiveSmallIntegerField()
    armour_rh_side_lower_mm = models.PositiveSmallIntegerField()
    armour_rear_lower_mm = models.PositiveSmallIntegerField()
    armour_rear_upper_mm = models.PositiveSmallIntegerField()
    armour_rear_top_mm = models.PositiveSmallIntegerField(null=True, blank=True)

    # hull armour slope, the construction angle of armour plate from vertical
    # or from horizontal for top plates, 0 (flat) to typically 60 (highly sloped) degrees
    armour_front_lower_deg = models.PositiveSmallIntegerField()
    armour_front_upper_deg = models.PositiveSmallIntegerField()
    armour_front_top_deg = models.PositiveSmallIntegerField(null=True, blank=True)
    armour_mid_top_deg = models.PositiveSmallIntegerField(null=True, blank=True)
    armour_lh_side_upper_deg = models.PositiveSmallIntegerField()
    armour_rh_side_upper_deg = models.PositiveSmallIntegerField()
    armour_lh_side_lower_deg = models.PositiveSmallIntegerField()
    armour_rh_side_lower_deg = models.PositiveSmallIntegerField()
    armour_rear_lower_deg = models.PositiveSmallIntegerField()
    armour_rear_upper_deg = models.PositiveSmallIntegerField()
    armour_rear_top_deg = models.PositiveSmallIntegerField(null=True, blank=True)

    # additional armour (applique) if fitted, slope angle is derived from the underlying armour plate
    armour_front_lower_applique_mm = models.PositiveSmallIntegerField(null=True, blank=True)
    armour_front_upper_applique_mm = models.PositiveSmallIntegerField(null=True, blank=True)
    armour_lh_side_upper_applique_mm = models.PositiveSmallIntegerField(null=True, blank=True)
    armour_rh_side_upper_applique_mm = models.PositiveSmallIntegerField(null=True, blank=True)
    armour_lh_side_lower_applique_mm = models.PositiveSmallIntegerField(null=True, blank=True)
    armour_rh_side_lower_applique_mm = models.PositiveSmallIntegerField(null=True, blank=True)

    # additional armour (spaced) if fitted, slope is always 0 degrees
    armour_front_upper_spaced_mm = models.PositiveSmallIntegerField(null=True, blank=True)
    armour_lh_side_upper_spaced_mm = models.PositiveSmallIntegerField(null=True, blank=True)
    armour_rh_side_upper_spaced_mm = models.PositiveSmallIntegerField(null=True, blank=True)
    armour_lh_side_lower_spaced_mm = models.PositiveSmallIntegerField(null=True, blank=True)
    armour_rh_side_lower_spaced_mm = models.PositiveSmallIntegerField(null=True, blank=True)

    armour_composition_hull = models.CharField(max_length=20, choices=ArmourComposition.choices)

    HIT_ZONES = {
        "front": ("front_lower", "front_upper"),
        "side_rh": ("rh_side_upper", "rh_side_lower"),
        "side_lh": ("lh_side_upper", "lh_side_lower"),
        "rear": ("rear_lower", "rear_upper"),
        "top": ("front_top", "mid_top", "rear_top"),
    }

    def __str__(self):
        return f"Hull armour ({self.get_armour_composition_hull_display()})"

    class Meta:
        verbose_name = "Hull Armour"
        verbose_name_plural = "Hull Armour"

class SuperStructure(models.Model):
    vehicle = models.OneToOneField("Vehicle", related_name="superstructure", on_delete=models.CASCADE, null=True,
                                   blank=True)
    superstructure_type_display = models.CharField(max_length=25, choices=SuperStructureType.choices)   # For UI display only
    mantlet_type_display = models.CharField(max_length=25, choices=MantletType.choices, null=True, blank=True)  # For UI display only

    # armour thickness (mm)
    armour_front_mm = models.PositiveSmallIntegerField(null=True, blank=True)
    armour_lh_side_mm = models.PositiveSmallIntegerField(null=True, blank=True)
    armour_rh_side_mm = models.PositiveSmallIntegerField(null=True, blank=True)
    armour_rear_mm = models.PositiveSmallIntegerField(null=True, blank=True)
    armour_top_mm = models.PositiveSmallIntegerField(null=True, blank=True)
    armour_mantlet_mm = models.PositiveSmallIntegerField(null=True, blank=True)

    # superstructure armour slope, the construction angle of armour plate from vertical
    # or from horizontal for top plates, 0 (flat) to typically 60 (highly sloped) degrees.
    armour_front_deg = models.PositiveSmallIntegerField(null=True, blank=True)
    armour_lh_side_deg = models.PositiveSmallIntegerField(null=True, blank=True)
    armour_rh_side_deg = models.PositiveSmallIntegerField(null=True, blank=True)
    armour_rear_deg = models.PositiveSmallIntegerField(null=True, blank=True)
    armour_top_deg = models.PositiveSmallIntegerField(null=True, blank=True)
    armour_mantlet_deg = models.PositiveSmallIntegerField(null=True, blank=True)

    # additional armour (applique) if fitted, slope angle is derived from the underlying armour plate
    armour_mantlet_applique_mm = models.PositiveSmallIntegerField(null=True, blank=True)
    armour_front_applique_mm = models.PositiveSmallIntegerField(null=True, blank=True)
    armour_lh_side_applique_mm = models.PositiveSmallIntegerField(null=True, blank=True)
    armour_rh_side_applique_mm = models.PositiveSmallIntegerField(null=True, blank=True)

    # additional armour (spaced) if fitted, slope is always 0 degrees
    armour_mantlet_spaced_mm = models.PositiveSmallIntegerField(null=True, blank=True)
    armour_front_spaced_mm = models.PositiveSmallIntegerField(null=True, blank=True)
    armour_lh_side_spaced_mm = models.PositiveSmallIntegerField(null=True, blank=True)
    armour_rh_side_spaced_mm = models.PositiveSmallIntegerField(null=True, blank=True)
    armour_rear_spaced_mm = models.PositiveSmallIntegerField(null=True, blank=True)

    armour_composition_superstructure = models.CharField(max_length=20, choices=ArmourComposition.choices)
    armour_composition_mantlet = models.CharField(max_length=20, choices=ArmourComposition.choices, null=True, blank=True)
    does_rotate = models.BooleanField()

    # In relation to the entire vehicles, derived from a visual exam of front and side
    # profile photos and then averaged to determine the proportion
    superstructure_proportion_percent = models.PositiveSmallIntegerField()

    HIT_ZONES = {
        "front": ("mantlet", "front"),
        "side_rh": ("rh_side",),
        "side_lh": ("lh_side",),
        "rear": ("rear",),
        "top": ("top",),
    }

    def __str__(self):
        return f"Superstructure #{self.pk}"

    class Meta:
        verbose_name = "Superstructure"
        verbose_name_plural = "Superstructures"

class Vehicle(models.Model):
    name = models.CharField(max_length=100)
    type = models.CharField(max_length=20, choices=VehicleType.choices)
    nationality = models.CharField(max_length=20, choices=Nationality.choices)
    YEAR_CHOICES = [(y, str(y)) for y in range(1915, 1946)]

    available_from_year = models.PositiveSmallIntegerField(
        "available from year (1915 - 1945)",
        default=1939,
        choices=YEAR_CHOICES,
    )
    available_from_month = models.CharField(max_length=2, choices=Month.choices, null=True, blank=True)
    general_info = models.TextField()  # free-text history/description, for display purposes
    image = models.ImageField(upload_to="vehicles/", null=True, blank=True)

    speed_road_kph = models.PositiveSmallIntegerField()
    speed_cc_kph = models.PositiveSmallIntegerField()
    range_road_km = models.PositiveSmallIntegerField()
    range_cc_km = models.PositiveSmallIntegerField()
    weight_tonne = models.FloatField()
    height_m = models.FloatField()
    length_m = models.FloatField()
    width_m = models.FloatField()
    has_radio = models.BooleanField()
    fuel_type = models.CharField(max_length=10, choices=FuelType.choices)

    troop_capacity = models.PositiveSmallIntegerField(null=True, blank=True)

    suspension_type = models.CharField(max_length=30, choices=SuspensionType.choices)

    engine_position = models.CharField(max_length=10, choices=InternalComponentPosition.choices)
    final_drive_position = models.CharField(max_length=10, choices=InternalComponentPosition.choices)
    transmission_position = models.CharField(max_length=10, choices=InternalComponentPosition.choices)
    fuel_tank_position = models.CharField(max_length=10, choices=InternalComponentPosition.choices)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Vehicle"
        verbose_name_plural = "Vehicles"

    @property
    def profile_size(self):
        # calculate overall vehicles profile size based on the structural height of a vehicles
        if self.height_m <= 1.9:
            return "low_profile"
        elif self.height_m >= 2.74:
            return "large_profile"
        else:
            return "medium_profile"


