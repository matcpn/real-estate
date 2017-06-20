$(document).ready(function() {
	$(".upgrade-type-selector").click(function(e) {
	   $(".upgrade-type-selector").removeClass("active");
	   $(e.target).addClass("active");
	});
});