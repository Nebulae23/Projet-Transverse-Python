extends Area3D

@onready var health_component = $Health_Component
@onready var damage_component = $damage_calculator_Component

func _ready() -> void:
	pass

func _on_body_entered(body: Node):
	# Check if the body is a projectile or has the required data
	if body.is_in_group("Damage_source"):
		var damage = body.get("damage")
		var effect = body.get("effect")
		var type = body.get("type")
		var duration = body.get("duration")
		var level = body.get("level")
		take_damage_and_effect(damage, type, effect, duration, level)

func take_damage_and_effect(damage: int, type: String, effect: String, duration: int, level: int):
	# Apply damage to the health component
	health_component.take_damage(damage)
	# Apply the effect to the damage component
	damage_component.apply_effect(effect, duration, level, type)
	
	
#dictionnary for attack format
#attack_type : projetcile/physic/melee/magic ==> to apply  modifier/vectors on the damage and statut and
#damage: return damage to health component
#statut: return the status to statut manager component
