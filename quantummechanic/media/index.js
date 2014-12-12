$(function() {
    locked = false;

    function lock() {
	locked = true;
	$("div#gates div.gate:hover").css("cursor", "auto");
    }

    function unlock() {
	locked = false;
	$("div#gates div.gate:hover").css("cursor", "pointer");
    }

    $(".gate").click(function() {
	if (!locked) {
	    lock();
	    var gate = $(this).attr("data-name");
	    var state = $("#canvas").attr("data-state");
	    var qubit1 = $("select#qubit1 option:selected").text();
	    var qubit2 = $("select#qubit2 option:selected").text();
	    var qubit3 = $("select#qubit3 option:selected").text();
	    var theta = $("input#theta").val();
	    var nth = $("input#nth").val();
	    $.ajax("/addgate/", {
		data: {
		    "state": state,
		    "new_gate": [gate, qubit1, qubit2, qubit3, theta],
		    "nth": nth,
		},
		success: function(data, status, jqxhr) {
		    if (data["error"]) {
			alert(data["error_message"]);
		    }
		    $("#canvas").attr("data-state", data["new_state"]);
		    $("#canvas").html(data["new_image"]);
		    $("#matrix").html(data["new_matrix"]);
		    unlock();
		},
		error: function(jqxhr, status, errorthrown) {
		    alert(status);
		    unlock();
		},
		dataType: "json",
	    });
	}
    });
    $("#undo").click(function() {
	if (!locked) {
	    lock();
	    var state = $("#canvas").attr("data-state");
	    $.ajax("/undo/", {
		data: {
		    "state": state,
		},
		success: function(data, status, jqxhr) {
		    if (data["error"]) {
			alert(data["error_message"]);
		    }
		    $("#canvas").attr("data-state", data["new_state"]);
		    $("#canvas").html(data["new_image"]);
		    $("#matrix").html(data["new_matrix"]);
		    unlock();
		},
		error: function(jqxhr, status, errorthrown) {
		    alert(status);
		    unlock();
		},
		dataType: "json",
	    });
	}
    });
    $("#clear").click(function() {
	if (!locked) {
	    lock();
	    var state = $("#canvas").attr("data-state");
	    $.ajax("/clear/", {
		data: {
		    "state": state,
		},
		success: function(data, status, jqxhr) {
		    if (data["error"]) {
			alert(data["error_message"]);
		    }
		    $("#canvas").attr("data-state", data["new_state"]);
		    $("#canvas").html(data["new_image"]);
		    $("#matrix").html(data["new_matrix"]);
		    unlock();
		},
		error: function(jqxhr, status, errorthrown) {
		    alert(status);
		    unlock();
		},
		dataType: "json",
	    });
	}
    });
});
