extends Node


# Called when the node enters the scene tree for the first time.
func _ready() -> void:
	pass # Replace with function body.


# Called every frame. 'delta' is the elapsed time since the previous frame.
func _process(delta: float) -> void:
	pass



#stats are a dictionnary with the following keys:
#"type": the type of the stat
#"value": the value of the stat
#"weight": the weight of the stat

"""data
character datat is arranged as seen :
	{
	level: int
	current_weapon 
		{
		main_stat:str
		weapon_damage_bonus:int
		weapon_crit_chance:float
		weapon_crit_damage_bonus:int
		}

	stats:
		{
		strenght:
			{
			value:int
			weight:float
			}
		vitality:
			{
			value:int
			weight:float
			}
		agility:
			{
			value:int
			weight:float
			}
		intelligence:
			{
			value:int
			weight:float
			}
		luck:
			{
			value:int
			weight:float
			}
		}
	}







example"""



func _get_modifiying_value(character_data:Dictionary):
	# gets data necessary for calculating flat damage, and stats
	var level = character_data["level"]
	var weapon_stat =0
	var weapon_damage_bonus =0
	for value in character_data["current_weapon"].values():
		weapon_stat = value["main_stat"]
		weapon_damage_bonus = value["weapon_damage_bonus"] 


	var strength = character_data["stats"]["strength"]["value"]
	var strength_weight = character_data["stats"]["strength"]["weight"]

	var vitality = character_data["stats"]["vitality"]["value"]
	var vitality_weight = character_data["stats"]["vitality"]["weight"]

	var intelligence = character_data["stats"]["intelligence"]["value"]
	var intelligence_weight = character_data["stats"]["intelligence"]["weight"]

	var agility = character_data["stats"]["agility"]["value"]
	var agility_weight = character_data["stats"]["agility"]["weight"]

	var luck = character_data["stats"]["luck"]["value"]
	var luck_weight = character_data["stats"]["luck"]["weight"]
	#calculate stats medium gap for determining balancing
	
	var sum_stat=(strength+vitality+intelligence++agility+luck)

	#search for "build" (highest attribute)
	var highest = 0
	var highest_weight=1
	for key in character_data["stats"] :
		#used for equilibrium 
		if highest < character_data["stats"][key]["value"]:
			highest = character_data["stats"][key]["value"]
			var medium = (sum_stat-highest)/4
			if key == "strenght" or key == "agility":
				highest *=1.25
				highest_weight+=
			if key=="intelligence":
				highest*=
				
	
	
	var luck_processed=luck*luck_weight+level

	





	#set up crit damage and chances with overflow mechanic (get in crit damage if overflow of crit chance)
	var crit_chance=luck+highest*highest_weight
	var overflow_1=0
	if crit_chance > 100:
		overflow_1 += (crit_chance - 100)

	var crit_damage=luck*(highest+level)

	var attack_touching_chance=(highest+level)*luck

	var overflow_2=0
	if attack_touching_chance > 100:
		overflow_2 += (attack_touching_chance - 100)

	
	var attack_damage_bonus=(highest*level+weapon_damage_bonus)+(overflow_2)

	
		
		
		
