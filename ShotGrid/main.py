import shotgun_api3

# Creating an API instance
def get_shotgrid(url="https://cphbom.shotgrid.autodesk.com/", script="", key=""):
    return shotgun_api3.Shotgun(url, script_name=script, api_key=key)

def query_data_example():
    filters = [['code', 'is', 'E01_SQ010_SH010']] # Filter defining which elements to query
    data = ['sg_sequence', 'id'] # Data to query
    result = sg.find('Shot', filters, data) # Fetching result from Shotgrid
    return result

def create_shot_example():
    data = {"project": {"type": "Project", "id": 122},
        "sg_sequence": {"type": "Sequence", "id": 42},
        "code": "E01_SQ020_SH010"}
    sg.create('Shot', data)

# def change_shot_names_example(ep):
#     filters = [['code', 'is', 'E01_SQ010']]
#     data = ['shots']
#     result = sg.find('Sequence', filters, data)[0]['shots']
#     for shot in result:
#         new_name = shot['name'].replace('E01', 'S105')
#         data = {'code': new_name}
#         sg.update('Shot', shot['id'], data)

if __name__ == '__main__':
    sg = get_shotgrid(script="cobopipe", key="fbda0Jg$zihrnynjqhiaywhic")
    print(query_data_example())