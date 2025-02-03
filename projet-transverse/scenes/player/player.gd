extends CharacterBody3D

@onready var anim = get_node("AnimationPlayer")

@onready var healthbar=$Camera3D/CanvasLayer/HUD

@onready var speed:int =5
@onready var maxHealth:int=30
@onready var currenthealth:int = maxHealth


const SPEED = 5.0
const JUMP_VELOCITY = 4.5

func _ready():
	healthbar.init_Health(currenthealth)

func _physics_process(delta: float) -> void:
	# Add the gravity.
	if not is_on_floor():
		velocity += get_gravity() * delta

	# Handle jump.
	if Input.is_action_just_pressed("ui_accept") and is_on_floor():
		velocity.y = JUMP_VELOCITY

	# Get the input direction and handle the movement/deceleration.
	# As good practice, you should replace UI actions with custom gameplay actions.
	var input_dir := Input.get_vector("ui_left", "ui_right", "ui_up", "ui_down")
	var direction := (transform.basis * Vector3(input_dir.x, 0, input_dir.y)).normalized()

	if direction:
		velocity.x = direction.x * SPEED
		velocity.z = direction.z * SPEED
		if velocity.x<0:
			anim.play("Run_left")
		if velocity.z>0:
			anim.play("Run_down")
		if velocity.x>0:
			anim.play("Run_right")
		if velocity.z<0:
			anim.play("Run_up")
	else:
		velocity.x = move_toward(velocity.x, 0, SPEED)
		velocity.z = move_toward(velocity.z, 0, SPEED)
		anim.play("Idle_down")
	
	if Input.is_action_just_pressed("ui_e"):
		currenthealth-=5
		healthbar.health=currenthealth
		
		
	move_and_slide()


	
	

	
