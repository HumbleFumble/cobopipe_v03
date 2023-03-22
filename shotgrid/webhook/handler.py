from shotgrid.status_update import update_downstream

def sg_handler(webhook_id, data, timestamp):
    if webhook_id == '6583bd26-f6da-4eaf-9b39-a9b5023f7722':
        if status_updated_to_approve(data):
            entity_id = data.get("meta").get("entity_id")
            update_downstream(entity_id)
    if webhook_id == "10c2b363-dbb7-4059-8836-ef99b5f8794f": #shot duration changed webhook (Christian test)
        print(f"Shot(id: {data.get('entity').get('id')}) duration changed from: {data.get('meta').get('old_value')} to {data.get('meta').get('new_value')}")


def cb_handler(data):
    if data.get('hook') == 'submit_zip':
        from Deadline.submit.CommandLine import submit_command_line_job
        submit_command_line_job( *data.get('args'), **data.get('kwargs') )
    elif data.get('hook') == 'submit_zip_unpack':
        from Deadline.submit.CommandLine import submit_command_line_job
        submit_command_line_job( *data.get('args'), **data.get('kwargs') )

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