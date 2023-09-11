/*
	Copy Deformation Values To Resting v1.0
	
	The script that sets resting parameters based on the current frame's deform parameters.
	(Essentially the reversed function of "Reset Current Keyframe").
	This version does not support free-form deformers.
	

	Installation:
	
	1) Download and Unarchive the zip file.
	2) Locate to your user scripts folder (a hidden folder):
	   https://docs.toonboom.com/help/harmony-17/premium/scripting/import-script.html	
	   
	3) Add all unzipped files ( *.js, and script-icons folder ) directly to the folder above.
	4) Add DEF_Copy_Deformation_Values_To_Resting to any toolbar.	
	
	
	Direction:

	1) Select deformation node(s) in Camera, Timeline or Node view.
	2) Run DEF_Copy_Deformation_Values_To_Resting.

		
	Author:

		Yu Ueda (raindropmoment.com)

*/



function DEF_Copy_Deformation_Values_To_Resting()
{
	main_function();
	
	function main_function()
	{
		var pf = new private_functions;
		var sNodes = selection.selectedNodes();

		var nodeList = pf.getDeformers( sNodes, [], [], [] );
		var boneList = nodeList[0];
		var curveList = nodeList[1];
		var offsetList = nodeList[2];
		
		if( boneList.length <= 0 && offsetList.length <= 0 && curveList.length <= 0 )
		{
			MessageBox.information( "Please select at least one bone, offset or curve nodes." );
			return;
		}	
		
		scene.beginUndoRedoAccum( "Copy deformation values to resting" );	
		
		if( boneList.length >= 1 )
		{
			for ( var i in boneList )
			{ pf.setBone( boneList[i] ) };
		}	
		
		if( offsetList.length >= 1 )
		{
			for ( var i in offsetList )
			{ pf.setOffset( offsetList[i] ) };
		}
		
		if( curveList.length >= 1 )
		{
			for ( var i in curveList )
			{ pf.setCurve( curveList[i] ) };		
		}
		
		scene.endUndoRedoAccum();	
	}

	
	
	function private_functions()
	{
		this.getDeformers = function( nodeList, boneList, curveList, offsetList )
		{
			for ( var i = 0; i < nodeList.length; i++ )
			{
				if( node.type( nodeList[i] ) == "BendyBoneModule" )
				{
					boneList.push( nodeList[i] );
				}				
				else if( node.type( nodeList[i] ) == "CurveModule" )
				{
					curveList.push( nodeList[i] );
				}
				else if( node.type( nodeList[i] ) == "OffsetModule" )
				{
					offsetList.push( nodeList[i] );
				}
				else if ( node.type( nodeList[i] ) == "GROUP" )
				{
					var subNodeList = node.subNodes( nodeList[i] );
					var subList = this.getDeformers( subNodeList, [], [], [] );
					boneList.push.apply( boneList, subList[0] );				
					curveList.push.apply( curveList, subList[1] );
					offsetList.push.apply( offsetList, subList[2] );								
				}
			}
		return [ boneList, curveList, offsetList ];
		}
		
		
		this.setBone = function( argNode )
		{
			var offsetX = node.getAttr( argNode, frame.current(), "offset.x" ).doubleValue();
			var offsetY = node.getAttr( argNode, frame.current(), "offset.y" ).doubleValue();
			var radius = node.getAttr( argNode, frame.current(), "radius" ).doubleValue();
			var orient = node.getAttr( argNode, frame.current(), "orientation" ).doubleValue();		
			var bias = node.getAttr( argNode, frame.current(), "bias" ).doubleValue();
			var length = node.getAttr( argNode, frame.current(), "length" ).doubleValue();			
			
			node.setTextAttr( argNode, "restoffset.x", frame.current(), offsetX );
			node.setTextAttr( argNode, "restoffset.y", frame.current(), offsetY );
			node.setTextAttr( argNode, "restradius", frame.current(), radius );
			node.setTextAttr( argNode, "restorientation", frame.current(), orient );
			node.setTextAttr( argNode, "restbias", frame.current(), bias );
			node.setTextAttr( argNode, "restlength", frame.current(), length );
		}	

		
		this.setOffset = function( argNode )
		{
			var p0X = node.getAttr( argNode, frame.current(), "offset.x" ).doubleValue();
			var p0Y = node.getAttr( argNode, frame.current(), "offset.y" ).doubleValue();
			var p0orient = node.getAttr( argNode, frame.current(), "orientation" ).doubleValue();			
			
			node.setTextAttr( argNode, "restingoffset.x", frame.current(), p0X );
			node.setTextAttr( argNode, "restingoffset.y", frame.current(), p0Y );	
			node.setTextAttr( argNode, "restingorientation", frame.current(), p0orient );	
		}	
		
		
		this.setCurve = function( argNode )
		{
			var p1X = node.getAttr( argNode, frame.current(), "offset.x" ).doubleValue();
			var p1Y = node.getAttr( argNode, frame.current(), "offset.y" ).doubleValue();
			var p1length0 = node.getAttr( argNode, frame.current(), "length0" ).doubleValue();
			var p1orient0 = node.getAttr( argNode, frame.current(), "orientation0" ).doubleValue();		
			var p1length1 = node.getAttr( argNode, frame.current(), "length1" ).doubleValue();
			var p1orient1 = node.getAttr( argNode, frame.current(), "orientation1" ).doubleValue();			
			
			node.setTextAttr( argNode, "restingoffset.x", frame.current(), p1X );
			node.setTextAttr( argNode, "restingoffset.y", frame.current(), p1Y );
			node.setTextAttr( argNode, "restlength0", frame.current(), p1length0 );
			node.setTextAttr( argNode, "restingorientation0", frame.current(), p1orient0 );
			node.setTextAttr( argNode, "restlength1", frame.current(), p1length1 );
			node.setTextAttr( argNode, "restingorientation1", frame.current(), p1orient1 );
		}
	}
}