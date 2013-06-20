/**
 * Scripts for the print view
 * Vladimir Ignatov
 */

// Initialize the BPC global obeject as needed
if (!window.BPC) {
	BPC = {};
}

jQuery(function($) {
	
	/**
	 * Initializes the patient object and renders everything. 
	 */
	function initPrintApp( patient, isDemo ) {
		BPC.initPatient( patient );
		console.log( patient, BPC );
		render( patient );
		
		// Below is just a temp. code for testing ------------------------------
		return;
		var rec1 = patient.data[0];
		var rec2 = patient.data[1];
		
		$("#header").after(
			'Rec 1: <input type="date" id="date1" /><input type="time" id="time1" />' +
			'&nbsp;&nbsp;&nbsp;' + 
			'Rec 2: <input type="date" id="date2" /><input type="time" id="time2" />'
		);
		
		$("#date1").prop("valueAsNumber", rec1.unixTime).change(onTimeChange);
		$("#date2").prop("valueAsNumber", rec2.unixTime).change(onTimeChange);
		$("#time1").prop("valueAsNumber", rec1.unixTime).change(onTimeChange);
		$("#time2").prop("valueAsNumber", rec2.unixTime).change(onTimeChange);
		
		function onTimeChange() {
			var d1 = new XDate($("#date1").prop("valueAsNumber"));
			var t1 = new XDate($("#time1").prop("valueAsNumber"));
			var d2 = new XDate($("#date2").prop("valueAsNumber"));
			var t2 = new XDate($("#time2").prop("valueAsNumber"));
			
			d1.setHours(t1.getUTCHours());
			d2.setHours(t2.getUTCHours());
			
			patient.data[0].unixTime = d1.getTime();
			patient.data[1].unixTime = d2.getTime();
			
			patient.data[0].date = d1.toString("yyyy-MM-dd");
			patient.data[1].date = d2.toString("yyyy-MM-dd");
			
			patient.data[0].timestamp = d1.toString("yyyy-MM-dd'T'HH:mm:sszzz");//"1999-01-21T04:32:00Z"
			patient.data[1].timestamp = d2.toString("yyyy-MM-dd'T'HH:mm:sszzz");
			
			patient.data[0].age = new XDate(patient.birthdate).diffYears(d1);
			patient.data[1].age = new XDate(patient.birthdate).diffYears(d2);
			
			//console.log(d1.toString() + "\n" + d2.toString());
			
			render( patient );
		}
	}
	
	/**
	 * Render all the views
	 */
	function render( patient ) 
	{
		var pacientCrop3 = patient.recentEncounters(3);
		
		drawHeader( "#header", patient );
		
		drawShortGraph( "#short-graph", pacientCrop3 );
		drawTable( "#short-table-view", pacientCrop3, true );
		
		drawLongGraph( "#long-graph", patient );
		drawTable( "#table-view", patient, false );
		
		setTitle( patient );
	}
	
	/**
	 * Draws the "short-view" graph.
	 * @param {String CSS selector | DOMElement | jQuery } container 
	 * @param {Patient} patient
	 */
	function drawShortGraph( container, patient ) {
		(new BPC.ShortGraph($(container).empty(), patient.recentEncounters(3))).draw();
	}
	
	/**
	 * Draws the "long-view" graph.
	 * @param {String CSS selector | DOMElement | jQuery } container 
	 * @param {Patient} patient
	 */
	function drawLongGraph( container, patient ) {
		(new BPC.LongGraph($(container).empty(), patient)).draw();
	}
	
	/**
	 * Renders the header of the print doc. populating the patient name and some
	 * other general data.
	 * @param {String CSS selector | DOMElement | jQuery } container 
	 * @param {Patient} patient
	 */
	function drawHeader( container, patient ) {
		
		var lastRecord, 
			tplData = {
				date : new XDate().toString('d MMM yy H:mm'),
				name : patient.name,
				sex  : patient.sex,
				dob  : new XDate(patient.birthdate).toString('d MMM yy')
			};
		
		// Find the last height record 
		if (patient.data && patient.data.length) {
			lastRecord = $.grep(patient.data, function(record, index) {
				return !!record.height;
			}).sort(function(a, b) {
				return b.unixTime - a.unixTime;
			})[0];
			
			if (lastRecord && lastRecord.height) {
				tplData.lastHeight = lastRecord.height + "cm";
				tplData.lastHeightDate = new XDate(lastRecord.unixTime).toString('d MMM yy');
			} else {
				tplData.lastHeight = "";
				tplData.lastHeightDate = ""
			}
		}
		
		// Generate the output
		$(container).empty().setTemplateElement("header-template").processTemplate(tplData);
	}
	
	/**
	 * Renders the "long" table at the bottom of the print doc.
	 * @param {String CSS selector | DOMElement | jQuery } container 
	 * @param {Patient} patient
	 */
	function drawTable( container, patient, short ) {
		
		// Apply filters 
		var p = patient.applyFilters();
		
		// Reverse the data order
		p.data.reverse();
		
		// Generate the table output
		$(container).empty().setTemplateElement("template").processTemplate(
			p, 
			{ short : !!short ? 1 : 0 }
		);
	}
	
	/**
	 * Sets the document.title. This will be used by the browser as the 
	 * default file name in the "Save as" dialog in case the user wants to print
	 * to file.
	 */
	function setTitle( patient ) {
		document.title = patient.name + " BPC " + new XDate().toString('d-MMM-yy');
	}
	
	// Bootstrap ---------------------------------------------------------------
	if (window.parent && 
		parent.BPC && 
		parent.BPC.patient && 
		!$.isEmptyObject(parent.BPC.patient)) 
	{
		initPrintApp( parent.BPC.patient );
	} else {
		initPrintApp( BPC.getSamplePatient(), true );
	}
	
	/*SMART.ready(function() {
		if ( typeof SMART === "undefined" ) {
			$("#info").text("Error: SMART Connect interface not found");
		} else {
			// Fire up the SMART API calls and initialize the application asynchronously
			$.when(BPC.get_demographics(), BPC.get_vitals(0))
			 .then( function (demographics, vitals) {
				var total = vitals.total;
				BPC.initPrintApp ( BPC.processData(demographics, vitals) );
				if (BPC.settings.loading_mode === "progressive") {
					BPC.loadAdditionalVitals (demographics, vitals, BPC.settings.vitals_limit, total);
				} else {
					BPC.vitals = vitals;
					BPC.demographics = demographics;
				}
			},
			function (message) {
				BPC.displayError (message.data);
			});
		}
	});
	
	SMART.fail (function () {
		initPrintApp ( BPC.getSamplePatient(), true );
	});*/
});