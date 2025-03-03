extends Node

@export var health_component : Node 


# Called when the node enters the scene tree for the first time.
func _ready() -> void:
	pass # Replace with function body.


# Called every frame. 'delta' is the elapsed time since the previous frame.
func _process(delta: float) -> void:
	
	pass


#using an equation we can increase the damage or the duration/effect severity the x of the equation can be the level of the status, type define witch modifier to use for  decreasing the effect of status
func _apply_effect(status,duration,level,type):
	
	
	
	
	
	if status=="Corroding":
		var damage = 2*(level)+randf_range(0,5)
		for i in range(0,(4*level+randf_range(0,5))):
			health_component.take_damage(damage)
		
	if status=="Burned":
		var damage = 2*(level)+randf_range(0,3)
		for i in range(0,(3*level+randf_range(0,2))):
			health_component.take_damage(damage)
		
	pass
