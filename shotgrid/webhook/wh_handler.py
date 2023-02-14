from shotgrid.status_update import update_downstream

def run(data, timestamp):
    if status_updated_to_approve(data):
        entity_id = data.get("meta").get("entity_id")
        update_downstream(entity_id)

def status_updated_to_approve(data):
    if not data.get("event_type") == "Shotgun_Task_Change":
        return False
    
    if not data.get("entity").get("type") == "Task":
        return False

    if not data.get("meta").get("attribute_name") == "sg_status_list":
        return False
    
    if not data.get("meta").get("new_value") in ["apr"]:
        return False

    return True


