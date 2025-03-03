extends CharacterBody3D

@export var projectile: PackedScene
@export var shoot_interval: float = 2.0  # Time between shots
var time_since_last_shot: float = 0.0
var player: Node3D  # Reference to the player node

func _ready():
	# Find the player node (assuming it's in the same scene and has a unique name or group)
	player = get_tree().get_root().get_node("/Player")  # Adjust the path as needed
	time_since_last_shot = shoot_interval

func shoot():
	if projectile and player:
		var b = projectile.instantiate()
		get_parent().add_child(b)  # Add the projectile to the scene

		# Set the projectile's position to the muzzle
		b.global_transform.origin = $Muzzle.global_transform.origin

		# Calculate the direction to the player
		var direction = (player.global_transform.origin - $Muzzle.global_transform.origin).normalized()
		b.look_at(player.global_transform.origin)  # Rotate the projectile to face the player

		# Set the projectile's velocity (assuming the projectile has a `velocity` property)
		if b.has_method("set_velocity"):
			b.set_velocity(direction * 20)  # Adjust the speed as needed

func _physics_process(delta: float) -> void:
	# Update the shooting timer
	time_since_last_shot += delta

	# Check if it's time to shoot
	if time_since_last_shot >= shoot_interval:
		shoot()
		time_since_last_shot = 0.0  # Reset the timer

	move_and_slide()
