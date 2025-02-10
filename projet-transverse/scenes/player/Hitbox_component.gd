extends Area3D

@onready var health_component= $Health_Component
@onready var status_component= $Status_Component


# Called when the node enters the scene tree for the first time.
func _ready() -> void:
	pass # Replace with function body.


# Called every frame. 'delta' is the elapsed time since the previous frame.
func _process(delta: float) -> void:
	for body in get_overlapping_bodies():
		if body.is_in_group("Damage_source"):
			var damage : int = body.data["damage"] #Body ==> for referecing the body that has entered the area, data is the dictionnary
			var status : String = body.data["status"]
			var duration : int = body.data["duration"]
			var level : int = body.data["level"]
			var type : String = body.data["type"]
			health_component.take_damage(damage)
			status_component.apply_effect(status,duration,level,type)
			
			pass
	
	
signal knockback(amount:int)

#dictionnary for attack format
#attack_type : projetcile/physic/melee/magic ==> to apply  modifier/vectors on the damage and statut and
#damage: return damage to health component
#statut: return the status to statut manager component
