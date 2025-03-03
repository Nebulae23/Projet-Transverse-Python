extends CharacterBody3D

@export var projectile: PackedScene
@export var shoot_interval: float = 2.0  # Time between shots
var time_since_last_shot: float = 0.0
@export var player: NodePath  # Path to the player node
var player_node: Node3D  # Reference to the player node

func _ready():
	# Get the player node from the exported path
	player_node = get_node(player)
	time_since_last_shot = shoot_interval

func shoot():
	if projectile and player_node:
		# Instantiate the projectile
		var b = projectile.instantiate()
		get_parent().add_child(b)  # Add the projectile to the scene

		# Set the projectile's position to the muzzle
		b.global_transform.origin = $Muzzle.global_transform.origin

		# Calculate the direction to the player
		var direction = (player_node.global_transform.origin - $Muzzle.global_transform.origin).normalized()
		b.look_at(player_node.global_transform.origin)  # Rotate the projectile to face the player

		# Set the projectile's velocity (assuming the projectile has a `set_velocity` method)
		if b.has_method("set_velocity"):
			b.set_velocity(direction * 20)  # Adjust the speed as neededd as needed

func _physics_process(delta: float) -> void:
	# Update the shooting timer
	time_since_last_shot += delta
	# Add the gravity.
	if not is_on_floor():
		velocity += get_gravity() * delta

	# Check if it's time to shoot
	if time_since_last_shot >= shoot_interval:
		shoot()
		time_since_last_shot = 0.0  # Reset the timer

	move_and_slide()
