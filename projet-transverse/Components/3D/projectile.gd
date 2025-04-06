extends Area3D

# Propriétés exportées
@export var damage: int = 10
@export var type: String = "physic"
@export var effect: String = "none"
@export var duration: int = 0
@export var level: int = 0
@export var projectile_gravity: float = 9.8  # Gravité du projectile
@export var trajectory_points: int = 20  # Nombre de points pour la trajectoire
@export var line_segment_mesh: Mesh  # Mesh pour les segments de ligne (cylindre, etc.)
@export var landing_marker: MeshInstance3D  # Marqueur d'atterrissage

# Variables internes
var velocity: Vector3 = Vector3.ZERO
var speed: float = 1.0
var trajectory_instance: Node3D  # Instance de la scène de trajectoire

# Fonction appelée au début du jeu
func _ready():
	# Trouver l'instance de la trajectoire dans les enfants
	trajectory_instance = $TrajectoryLine
	if trajectory_instance:
		print("Trajectory instance found!")
	else:
		print("Trajectory instance NOT found! Please check the node name and hierarchy.")
	update_trajectory_visualization()

# Définir la vitesse initiale
func set_velocity(new_velocity: Vector3):
	velocity = new_velocity * speed
	update_trajectory_visualization()

# Mettre à jour la physique du projectile
func _physics_process(delta):
	velocity.y -= projectile_gravity * delta
	global_transform.origin += velocity * delta

# Calculer la trajectoire
func calculate_trajectory(initial_velocity: Vector3, gravity: float, time_steps: int) -> Array:
	var points: Array = []
	for i in range(time_steps):
		var t: float = i * 0.1
		var x: float = initial_velocity.x * t
		var y: float = initial_velocity.y * t - 0.5 * gravity * t * t
		var z: float = initial_velocity.z * t
		points.append(global_transform.origin + Vector3(x, y, z))  # Ajouter la position actuelle du projectile
	print("Calculated trajectory points: ", points)
	return points

# Dessiner la trajectoire
func draw_trajectory(points: Array):
	if trajectory_instance:
		print("Drawing trajectory with points: ", points)
		trajectory_instance.draw_trajectory(points, line_segment_mesh)
	else:
		print("Trajectory instance is null!")

# Mettre à jour le marqueur d'atterrissage
func update_landing_marker(position: Vector3):
	if landing_marker:
		landing_marker.global_transform.origin = position
		print("Landing marker updated to position: ", position)
	else:
		print("Landing marker is null!")

# Mettre à jour la visualisation de la trajectoire
func update_trajectory_visualization():
	var points = calculate_trajectory(velocity, projectile_gravity, trajectory_points)
	if points.size() > 0:
		draw_trajectory(points)
		update_landing_marker(points[-1])  # Afficher le marqueur à la fin de la trajectoire
	else:
		print("No trajectory points calculated!")

# Gérer les collisions
func _on_body_entered(body: Node3D) -> void:
	if body.has_node("hitbox_component"):
		var hitbox_component = body.get_node("hitbox_component")
		hitbox_component.take_damage_and_effect(damage, type, effect, duration, level)
		queue_free()
	if body is GridMap:
		queue_free()
