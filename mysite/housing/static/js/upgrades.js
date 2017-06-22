$(document).ready(function() {
	filter();
	$(".upgrade-type-selector").click(function(e) {
	    $(".upgrade-type-selector").removeClass("active");
	    $(e.target).addClass("active");
	    filter();
	});

});

function filter() {
	var activeID = $(".active")[0].id;
	var typeSelected = "." + activeID;
	$(".chosen-upgrade").each(function(index, element) {
		element.style.display = 'none';
	});
	$(".choosable-upgrade").each(function(index, element) {
		element.style.display = 'none';
	});
	$(typeSelected).each(function(index, element) {
		element.style.display = 'block';
	});
};