extends Area3D

@export var damage : int = 10
@export var type : String = "physic"
@export var effect : String = "none"
@export var duration : int = 0
@export var level : int = 0
var velocity: Vector3 = Vector3.ZERO
var speed: float = 5.0


func set_velocity(new_velocity: Vector3):
	velocity = new_velocity * speed

func _physics_process(delta):
	velocity.y -= gravity * delta
	# Move the projectile
	global_transform.origin += velocity * delta
	

func _on_body_entered(body: Node3D) -> void:
	if body.has_node("hitbox_component") :
		var hitbox_component = body.get_node("hitbox_component")
		hitbox_component.take_damage_and_effect(damage, type, effect, duration, level)
			# Pass the projectile's data to the hitbox_component
		queue_free()
	if body is GridMap:
		queue_free()
