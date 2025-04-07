extends Control

@onready var timer=$ItemList/VSplitContainer2/VSplitContainer/Healthbar/Timer
@onready var HealthBar=$ItemList/VSplitContainer2/VSplitContainer/Healthbar
@onready var  damageBar=$ItemList/VSplitContainer2/VSplitContainer/Healthbar/DamageBar

@onready var EnergyBar=$ItemList/VSplitContainer2/VSplitContainer/EnergyBar
@onready var ExhaustionBar=$ItemList/VSplitContainer2/VSplitContainer/EnergyBar/ExhaustionBar
@onready var timer2=$ItemList/VSplitContainer2/VSplitContainer/EnergyBar/Timer




func _on_health_component_health_changed(current_amount: int, max_amount: int) -> void:
	var health=current_amount
	var max_health=max_amount
	HealthBar.max_value=max_health
	HealthBar.value=health
	damageBar.value=health
	damageBar.max_value=max_health
	
func _on_energy_component_energy_changed(current_amount: int, max_amount: int) -> void:
	var energy=current_amount
	var max_energy=max_amount
	EnergyBar.max_value=max_energy
	EnergyBar.value=energy
	ExhaustionBar.value=energy
	ExhaustionBar.max_value=max_energy


func _on_button_pressed() -> void:
	get_tree().change_scene_to_file("res://main.tscn")
