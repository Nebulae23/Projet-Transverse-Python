extends Area3D

@onready var status_component=$damage_calculator_component
@export var damage : int = 5
@export var type : String = "physic"
@export var effect : String = "none"
@export var duration : int = 0
@export var level : int = 0
var velocity: Vector3 = Vector3.ZERO
var speed: float = 20.0


func set_velocity(new_velocity: Vector3):
	velocity = new_velocity * speed



func _physics_process(delta):
	velocity.y -= gravity * delta
	# Move the projectile
	global_transform.origin += velocity * delta
	position += transform * speed * delta

func _on_projectile_body_entered(body):
	# Check if the body has a hitbox_component
	if body.has_node("Hitbox_Component"):
		var hitbox_component = body.get_node("Hitbox_Component")
		hitbox_component.take_damage_and_effect(damage, type, effect, duration, level)
			# Pass the projectile's data to the hitbox_component
	queue_free()
