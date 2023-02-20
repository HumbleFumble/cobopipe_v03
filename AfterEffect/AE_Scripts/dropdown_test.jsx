var cur_win = (function(thisObj){
    var isPanel = thisObj instanceof Panel; // true or false
    var dialog = isPanel  ? thisObj : new Window("window", "GatherHookup Direct");

    dialog.alignChildren = 'left'
    dialog.alignment = ['top','fill']

    dialog.grp = dialog.add("Group{orientation:'column',alignment:['fill','fill'],\
    panel_group: Group{orientation: 'row',\
    static_group: Group{orientation: 'column',\
    drop_down: DropDownList { alignment:['fill','top'],preferredSize: ['100','20'] }},\
    edit_group: Group{orientation: 'column',et_e: EditText{text: '01', preferredSize: ['50','20']}, et_seq: EditText{text: '020', preferredSize: ['50','20']} } }}\
    ")

    dialog.grp.panel_group.static_group.drop_down.add("item", "new");
    dialog.grp.panel_group.static_group.drop_down.selection="new"
    if (!isPanel) {
      // if it's a window
      dialog.show();
    } else {
      // if it's a panel
      dialog.layout.layout(true);
      dialog.layout.resize();
      }
    return dialog
})(this);