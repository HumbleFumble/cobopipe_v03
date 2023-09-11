/*
	Remove Unused Colors
	
			v1.01 - The script no longer opens "Remove Unused Palettes From Scene List" dialog.
			v1.02 - The script removes the unused palettes from disc.
			v1.03 - Script Optimization. Prevent infinity loop after failed to remove empty palettes.
	
	Remove unused color swatches on scene palettes. The script will also remove empty palettes.
	This script is compatible with Harmony Premium 15 and up.
	
	Installation:
	
	1) Download and Unarchive the zip file.
	2) Locate to your user scripts folder(a hidden folder):
	   https://docs.toonboom.com/help/harmony-17/premium/scripting/import-script.html	
	   
	3) Add all unzipped files (*.js, *.ui, and script-icons folder) directly to the folder above.   
	4) Add one or both of the following functions to any toolbar:

	   - PAL_Remove_All_Unused_Colors_And_Palettes
	   - PAL_Remove_Unused_Colors_On_Selected_Palette
	
	
	Direction: 
	
	- For PAL_Remove_All_Unused_Colors_And_Palettes
	
	1) Before running the script, make sure palette list is loaded(unlocked) on palette view.
	2) Run this script. All unused colors and palettes will be removed.
	3) On Remove Unused Palettes From Scene Palette List dialog, hit Select All and then okay,
	   This will remove all empty crossed-out palettes.
	   
	- For PAL_Remove_Unused_Colors_On_Selected_Palette
	
	1) Select a palette to remove unused colors from.
	2) Run the script. Palettes will be removed when it becomes empty.
	

	Co-writers:

		Liza D, Mathieu C, Yu U 
		
*/

scriptVer = "1.03";

function PAL_Remove_All_Unused_Colors_And_Palettes()
{
	var pf = new private_functions;			
	if (!KeyModifiers.IsShiftPressed())
		if (!pf.confirmBox("", "all"))
			return;

	var usedColors = pf.getNodeColors();
	var paletteList = PaletteObjectManager.getScenePaletteList();

	scene.beginUndoRedoAccum("Remove Unused Scene Colors And Palettes");
	
	for (var idx = paletteList.numPalettes-1; idx >= 0; idx--)
	{
		var palId = PaletteManager.getPaletteId(idx);	
		var palette = PaletteObjectManager.getPalette(palId);
		for (var idx2 = palette.nColors -1; idx2 >= 0; idx2--)	
		{	
			var foundColor = palette.getColorByIndex(idx2);
			if (usedColors.indexOf(foundColor.id) === -1) 
				palette.removeColor(foundColor.id);
		}
		
		// remove palette if empty
		if (palette.nColors === 0)
		{
			try
			{
				PaletteObjectManager.removePaletteReferencesAndDeleteOnDisk(palId);
			}
			catch(err){}
		}
	}
	
	scene.endUndoRedoAccum();
}


		
function PAL_Remove_Unused_Colors_On_Selected_Palette()
{
	var pf = new private_functions;	
	var usedColors = pf.getNodeColors();

	var palId = PaletteManager.getCurrentPaletteId();	
	var palette = PaletteObjectManager.getPalette(palId);
	var palName = palette.getName();	
	if (!KeyModifiers.IsShiftPressed())	
		if (!pf.confirmBox(palName, "selected"))
			return;

	scene.beginUndoRedoAccum("Remove Unused Colors On Selected Palette");

	for (var idx2 = palette.nColors -1; idx2 >= 0; idx2--)
	{	
		var foundColor = palette.getColorByIndex(idx2);
		if (usedColors.indexOf(foundColor.id) === -1) 
			palette.removeColor(foundColor.id);
	}

	// remove palette if empty
	if (palette.nColors === 0)
	{
		try
		{
			PaletteObjectManager.removePaletteReferencesAndDeleteOnDisk(palId);
		}
		catch(err){}
	}
	
	scene.endUndoRedoAccum();
}



function private_functions()
{
	this.confirmBox = function(palName, mode)
	{
		var dialog = new Dialog();
		if (mode === "all")
		{
			dialog.title = "Remove All Unused Colors And Palettes v" + scriptVer;
			var str1 = "You are about to remove all unused colors and palettes of the scene file.\n\n\nTip: You can skip this confirmation dialog from popping up by\nholding down shift while pressing on the script's icon :)";
		}
		else
		{
			dialog.title = "Remove Unused Colors On Selected Palette v" + scriptVer;
			var str1 = "You are about to remove unused colors on " + palName + " palette.\n\n\nTip: You can skip this confirmation dialog from popping up by\nholding down shift while pressing on the script's icon :)";
		}
		dialog.width = 400;

		var input1 = new TextEdit;
		input1.label = "";
		input1.text = str1;

		dialog.add(input1);
		
		if (!dialog.exec())
			return false;
		else
			return true;		
	};

	
	this.getNodeColors = function()
	{
		// Make list of colors used in the scene		
		var nodes = node.getNodes(["READ"]);
		
		var nodeColors = [];		
		for (var nd = 0; nd < nodes.length; nd++)
		{
			var useTiming = node.getAttr(nodes[nd], 1, "drawing.elementMode").boolValue();
			var drawColumn = node.linkedColumn(nodes[nd], useTiming ? "drawing.element" : "drawing.customName.timing");			
			var frameList = this.getFrames(drawColumn);
		
			for (var fr = 0; fr < frameList.length; fr++)
			{
				var drawingColors = DrawingTools.getDrawingUsedColors({node: nodes[nd], frame: frameList[fr]});
				for (var co = 0; co < drawingColors.length; co++)
					if (nodeColors.indexOf(drawingColors[co]) === -1)
						nodeColors.push(drawingColors[co]);
			}
		}
		return nodeColors;
	};
	
	this.getFrames = function(drawColumn)
	{
		var colList = [], frameList = [];
		for (var fr = 1; fr <= frame.numberOf(); fr++)
		{		
			var col = column.getEntry (drawColumn, 1, fr);
			if (col !== "" && colList.indexOf(col) === -1)
			{
				colList.push(col);
				frameList.push(fr);
			}
		}
		return frameList;
	};
}