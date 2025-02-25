extends Control

@onready var timer=$ItemList/VSplitContainer2/VSplitContainer/Healthbar/Timer
@onready var HealthBar=$ItemList/VSplitContainer2/VSplitContainer/Healthbar
@onready var  damageBar=$ItemList/VSplitContainer2/VSplitContainer/Healthbar/DamageBar






func _on_health_component_health_changed(current_amount: int, max_amount: int) -> void:
	var health=current_amount
	var max_health=max_amount
	HealthBar.max_value=max_health
	HealthBar.value=health
	damageBar.value=health
	damageBar.max_value=max_health
