extends Node


enum TYPE { EXHAUSTION, ENERGY, FULL_ENERGY }

## The Health Component is used to give any node it's attached to health related functions.
##
## This component offers a variety of functions that can be personalized for each instance, including clamping [member current_health] values, ignoring all damage taken,
## exceeding [member max_health], and automatically emitting signals for damaging and healing events.[br][br]
##
## There are three primary methods for interacting with health.[br]
## [method take_damage][br]
## [method take_healing][br]
## [method resurrect][br][br]
## Another two methods are also provided to forcibly cause damage and healing which [u]can[/u] ignore [member god_mode], primarily used for scripting interactions.[br]
## [method force_damage][br]
## [method force_heal][br][br]

signal energy_changed(current_amount: int, max_amount: int) ## Emitted every time [member current_energy] is changed in a neutral context, should be used with interface functions
signal exhaustion(amount: int) ## Emitted when [member current_energy] is changed in a negative context.
signal energized(amount: int) ## Emitted when [member current_energy] is changed in a postive context.
signal energy_fulled ## Emitted when [member current_energy] was at 0, and now is positive.
signal exhausted(overkill: int) ## Emitted when [member current_energy] has reached 0.

@export var max_energy: int = 100: ## The maximum amount of [member current_health] this component can have normally. By default on creation current [member current_health] will be set to this value.
	set(value):
		var previous: int = max_energy
		max_energy = value
		if energy_difference:
			current_energy += max_energy - previous
		current_energy = clamp(current_energy, 0, max_energy)
		energy_changed.emit(current_energy, max_energy)

@export var exceed_maximum_energy: bool = false ## Allows current [member current_health] to exceed [member max_health], used in niche situations.
@export var energy_difference: bool = true ## When modifying [member max_health] if it should grant the [member current_health] gained from [member max_health] increasing.
@export var god_mode: bool = false ## Causes all damage to be ignored unless forced by [method force_damage]. This does not stop healing from occuring.

var current_energy: int = max_energy: ## The current health, Will clamp any value changes to 0 or [member max_health] unless [member exceed_maximum_health] is enabled.
	set(value):
		if exceed_maximum_energy:
			current_energy = max(0, value)
		else:
			current_energy = clamp(value, 0, max_energy)
		energy_changed.emit(current_energy, max_energy)
var no_energy: bool = false ## Used for resurrection purposes.

#region Public Functions

## The Public Method to negatively effect [member current_health].
func take_exhasution_level(exhaustion_level: int) -> void:
	_change_energy(exhaustion_level, TYPE.EXHAUSTION)

## The Public Method to postively effect [member current_health].
func take_boost(boost: int) -> void:
	_change_energy(boost, TYPE.ENERGY)

## The Public Method to resurrect if [member dead].
func full_energy(boost: int) -> void:
	_change_energy(boost, TYPE.FULL_ENERGY)

#endregion

#region Private Functions

## The Private method to effect the [member current_health] of the component.[br][br]
## Expected Operations:[br]
## 1. You can always be healed unless [member dead].[br]
## 2. You can only be resurrected when [member dead].[br]
## 3. If [member god_mode] is enabled, exit early.[br]
## 4. Lastly if [member current_health] is equal to 0, [signal died] will be emitted with overkilled amount.[br]
func _change_energy(amount: int, type: TYPE) -> void:
	match type:
		TYPE.ENERGY:
			if no_energy:
				return
			current_energy += amount
			energized.emit(amount)
		TYPE.FULL_ENERGY:
			if not no_energy:
				return
			no_energy = false
			current_energy += amount
			energized.emit(amount)
			energy_fulled.emit()
		TYPE.EXHAUSTION:
			if god_mode:
				return
			var overkill: int = amount - current_energy
			current_energy -= amount
			exhaustion.emit(amount)
			if current_energy <= 0:
				no_energy = true
				exhausted.emit(overkill)

#endregion

#region Force Methods

## This method will forcibly cause damage, and can be set to not ignore [member god_mode].[br]
## [u]This is not the intended way to cause damage or healing and shoud be used only for scripting scenarios.[/u]
func force_exhaustion(amount: int, ignore_god_mode: bool = true) -> void:
	var current_god_status: bool = god_mode
	if ignore_god_mode:
		god_mode = false
	_change_energy(amount, TYPE.EXHAUSTION)
	god_mode = current_god_status

## This method will forcibly increase [member current_health] and cause resurrection to happen.[br]
## [u]This is not the intended way to cause damage or healing and shoud be used only for scripting scenarios.[/u]
func force_boost(amount: int) -> void:
	if no_energy:
		_change_energy(amount, TYPE.FULL_ENERGY)
	else:
		_change_energy(amount, TYPE.ENERGY)

	

#endregion
