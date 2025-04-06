extends CharacterBody3D

# Propriétés exportées
@export var projectile: PackedScene  # Scène du projectile
@export var shoot_interval: float = 2.0  # Temps entre les tirs
@export var player: NodePath  # Chemin vers le nœud du joueur
@export var projectile_speed: float = 20.0  # Vitesse du projectile

# Variables internes
var time_since_last_shot: float = 0.0
var player_node: Node3D  # Référence au nœud du joueur

func _ready():
	# Récupérer le nœud du joueur à partir du chemin exporté
	player_node = get_node(player)
	time_since_last_shot = shoot_interval  # Initialiser le timer

func shoot():
	if projectile and player_node:
		# Instancier le projectile
		var projectile_instance = projectile.instantiate()
		get_parent().add_child(projectile_instance)  # Ajouter le projectile à la scène
		print("Projectile instantiated and added to scene!")

		# Positionner le projectile à l'emplacement du "Muzzle"
		projectile_instance.global_transform.origin = $Muzzle.global_transform.origin

		# Calculer la direction vers le joueur
		var direction = (player_node.global_transform.origin - $Muzzle.global_transform.origin).normalized()

		# Orienter le projectile vers le joueur
		projectile_instance.look_at(player_node.global_transform.origin)

		# Définir la vitesse du projectile (si le projectile a une méthode `set_velocity`)
		if projectile_instance.has_method("set_velocity"):
			projectile_instance.set_velocity(direction * projectile_speed)
			print("Projectile velocity set!")

func _physics_process(delta: float) -> void:
	# Mettre à jour le timer de tir
	time_since_last_shot += delta

	# Appliquer la gravité si l'ennemi n'est pas au sol
	if not is_on_floor():
		velocity += get_gravity() * delta

	# Vérifier s'il est temps de tirer
	if time_since_last_shot >= shoot_interval:
		shoot()
		time_since_last_shot = 0.0  # Réinitialiser le timer

	# Déplacer l'ennemi
	move_and_slide()
