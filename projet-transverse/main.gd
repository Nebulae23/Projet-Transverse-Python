extends Control

@onready var level=preload("res://world.tscn")
# Called when the node enters the scene tree for the first time.
func _ready() -> void:
	pass # Replace with function body.


# Called every frame. 'delta' is the elapsed time since the previous frame.


func _on_quit_pressed() -> void:
	get_tree().quit
	
func _on_options_pressed() -> void:
	get_tree().change_scene_to_file("res://options.tscn")
func _on_new_game_pressed() -> void:
	get_tree().change_scene_to_file("res://world.tscn")# Replace with function body.
