cmds.setAttr("Rig:Root_Group.asset_type", self.popupTypeDropdown.currentText(), type="string")
cmds.setAttr("Rig:Root_Group.asset_category", self.popupCategoryDropdown.currentText(), type="string")
cmds.setAttr("Rig:Root_Group.asset_name", self.popupNameTextField.text(), type="string")