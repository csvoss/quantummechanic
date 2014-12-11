$(function() {
    $(".gate").click(function() {
	var gate = $(this).attr("data-name");
	var state = $("#canvas").attr("data-state");
	var qubit1 = $("input#qubit1").val();
	var qubit2 = $("input#qubit2").text();
	var theta = $("input#theta").val();
	var nth = $("input#nth").val();
	$.ajax("/addgate/", {
	    data: {
		"state": state,
		"new_gate": [gate, qubit1, qubit2, theta, nth],
	    },
	    success: function(data, status, jqxhr) {
		$("#canvas").attr("data-state", data["new_state"]);
		$("#canvas").html(data["new_image"]);
	    },
	    error: function(jqxhr, status, errorthrown) {
		alert("An error occurred. Please try again, or report bug if error persists.");
	    },
	    dataType: "json",
	});
    });
});
