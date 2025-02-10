extends Area2D

@onready var status_component=$damage_calculator_component
@export var damage : int = 5
@export var type : String = "physic"
@export var effect : String = "none"
@export var duration : int = 0
@export var level : int = 0
signal hit(damage: int,type: String, effect: String,duration:int,level:int)




var speed = 750

func _physics_process(delta):
	position += transform.x * speed * delta

func _on_projectile_body_entered(body):
	# Check if the body has a hitbox_component
	if body.has_node("Hitbox_Component"):
		var hitbox_component = body.get_node("Hitbox_Component")
		hitbox_component.take_damage_and_effect(damage, type, effect, duration, level)
			# Pass the projectile's data to the hitbox_component
	queue_free()
