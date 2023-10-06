#TODO Make a script that goes in and changes the settings of the local harmony preferences

import os

import xml.etree.ElementTree as ET

my_prefs_xml_string = """
<preferences>
    <bool id="ACCEPT_UNICODE_NAME" value="Y"/>
    <bool id="ADVANCED_DISPLAY_IN_VIEWS" value="Y"/>
    <bool id="ADVANCED_ELEMENT_BASIC_ANIMATE" value="Y"/>
    <bool id="ADVANCED_PALETTELIST" value="Y"/>
    <bool id="COMPOSITE_DEFAULT_PASS_THROUGH" value="Y"/>
    <bool id="FOCUS_ON_MOUSE_ENTER" value="Y"/>
    <bool id="TIMELINE_REDUCE_INDENTATION" value="Y"/>
    <bool id="ELEMENT_CAN_BE_ANIMATED_DEFAULT_VALUE" value="N"/>
    <bool id="ENABLE_LOG_IO" value="Y"/>
    <bool id="ENABLE_MIDDLE_BUTTON_PANS_VIEW" value="Y"/>
    <bool id="PEG_DEFAULT_SEPARATE_POSITION" value="Y"/>
    <bool id="USE_OVERLAY_UNDERLAY_ART" value="Y"/>
    <bool value="Y" id="PEG_DEFAULT_SEPARATE_POSITION"/>
    <bool value="N" id="EXPORTOGL_LAUNCH_PLAYER"/>
</preferences>
"""

# changes_root = ET.fromstring(my_prefs_xml_string)
# # changes_root = changes_tree.getroot()
# for change_bool in changes_root:
#     change_id = change_bool.get('id')


user_appdata = os.getenv("APPDATA")
full_path = f"{user_appdata}/Toon Boom Animation/Toon Boom Harmony Premium/full-2200-pref/Harmony Premium-pref.xml"
if os.path.exists(full_path):

    # Load and parse the original XML file
    original_tree = ET.parse(full_path)
    original_root = original_tree.getroot()

    # Load and parse the changes XML file
    changes_root = ET.fromstring(my_prefs_xml_string)
    # changes_root = changes_tree.getroot()

    # Iterate over each <bool> element in the changes.xml
    for change_bool in changes_root:
        change_id = change_bool.get('id')

        # Find the corresponding <bool> element in the original.xml by ID
        original_bool = original_root.find(f".//*[@id='{change_id}']")

        # If the <bool> element exists in original.xml, update its value attribute
        if original_bool is not None:
            original_bool.set('value', change_bool.get('value'))
        # If the <bool> element doesn't exist in original.xml, add it
        else:
            original_root.append(change_bool)

    # Save the changes back to the original XML file
    original_tree.write(full_path)


