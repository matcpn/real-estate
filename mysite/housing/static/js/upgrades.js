$(document).ready(function() {
	$(".upgrade-type-selector").click(function(e) {
	    $(".upgrade-type-selector").removeClass("active");
	    $(e.target).addClass("active");
	    $(".choosable-upgrade").each(function(index, element) {
			element.style.display = 'none';
		});
		var clickedID = e.target.id;
		var classClicked = "." + clickedID;
		$(classClicked).each(function(index, element) {
			element.style.display = 'block';
		});
	});

});

function filter(e) {
	$(".choosable-upgrade").each(function(index, element) {
		element.style.display = 'none';
	});
	var clickedID = e.target.id;
	$("."+clickedID).forEach(function(index, element) {
		element.style.display = 'block';
	});
};