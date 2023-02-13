def run(data, timestamp):
    print('Hiii')

def status_updated_to_approve(data):
    if not data.get("event_type") == "Shotgun_Task_Change":
        return False
    
    if not data.get("entity").get("type") == "Task":
        return False
    
    if not data.get("meta").get("new_value") in ["apr"]:
        return False

    return True