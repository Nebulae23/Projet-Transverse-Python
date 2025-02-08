extends Control

@onready var timer=$ItemList/VSplitContainer2/VSplitContainer/Healthbar/Timer
@onready var HealthBar=$ItemList/VSplitContainer2/VSplitContainer/Healthbar
@onready var  damageBar=$ItemList/VSplitContainer2/VSplitContainer/Healthbar/DamageBar



var health =10 : set = _set_Health

func _set_Health(new_Health):
	var prev_health=health
	health=min(HealthBar.max_value ,new_Health)
	
	if health <=0:
		queue_free()
	
	if health < prev_health:
		timer.start()
	else:
		damageBar.value=health



func init_Health(_health):
	health=_health
	HealthBar.max_value=health
	HealthBar.value=health
	damageBar.value=health
	damageBar.max_value=health


	
func _on_timer_timeout() -> void:
	damageBar.value = health
