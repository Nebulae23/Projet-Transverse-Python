extends Area3D


# Called when the node enters the scene tree for the first time.
func _ready() -> void:
	pass # Replace with function body.


# Called every frame. 'delta' is the elapsed time since the previous frame.
func _process(delta: float) -> void:
	for body in get_overlapping_bodies():
		if body.is_in_group("Damage_source"):
			pass
	
	
signal knockback(amount:int)

#dictionnary for attack format
#attack_type : projetcile/physic/melee/magic ==> to apply  modifier/vectors on the damage and statut and
#damage: return damage to health component
#statut: return the status to statut manager component
