extends Node3D

# Fonction pour dessiner la trajectoire
func draw_trajectory(points: Array, line_segment_mesh: Mesh):
	print("Drawing trajectory segments...")
	
	# Supprimer les anciens segments
	for child in get_children():
		child.queue_free()
	
	# Créer de nouveaux segments
	for i in range(points.size() - 1):
		var start = points[i]
		var end = points[i + 1]
		print("Creating segment from ", start, " to ", end)
		
		var segment = MeshInstance3D.new()
		segment.mesh = line_segment_mesh
		
		# Ajouter un matériau pour rendre le segment visible
		var material = StandardMaterial3D.new()
		material.albedo_color = Color(1, 0, 0)  # Rouge pour une meilleure visibilité
		segment.material_override = material
		
		# Positionner et orienter le segment
		var direction = (end - start).normalized()
		var length = start.distance_to(end)
		segment.scale = Vector3(0.1, 0.1, length)  # Ajuster l'échelle pour une meilleure visibilité
		segment.look_at_from_position(start, end)
		
		add_child(segment)
