extends Area3D

@export var health_component : Node 
@export var status_component : Node 

func _ready() -> void:
	pass


func take_damage_and_effect(damage: int, type: String, effect: String, duration: int, level: int):
	# Apply damage to the health component
	health_component.take_damage(damage)
	# Apply the effect to the damage component
	status_component.apply_effect(effect, duration, level, type)
	
	
#dictionnary for attack format
#attack_type : projetcile/physic/melee/magic ==> to apply  modifier/vectors on the damage and statut and
#damage: return damage to health component
#statut: return the status to statut manager component
