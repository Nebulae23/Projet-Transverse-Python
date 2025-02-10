extends CharacterBody3D
@export var projectile : PackedScene

func shoot():
	var b = projectile.instantiate()
	owner.add_child(b)
	b.transform = $Muzzle.global_transform
	
func _physics_process(delta: float) -> void:
	
	move_and_slide()
