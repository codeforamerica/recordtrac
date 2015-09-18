$(function(){
	$('#step1').fadeIn('fast');  
	  
	$('#button1').click(function(){
		    
// validation
	
	if ((document.newrequest.agency.value=="--")
	|| (document.newrequest.category.value=="--")
	|| (document.newrequest.topic.value=="")

		
	){
	    alert("All indicated information is required. Please complete all fields");
	    exit();
	    }

		// scroll to the top of the form
	    $('html, body').animate({
	        scrollTop: $("#submitRequest").offset().top
	    }, 500);

	    // fade out step1, fade in step2
		$('#step1').fadeOut('fast', function() {
		  }); 
		$('#step2').fadeIn('slow', function() {
		  });  
	});	
	
	$('#button2').click(function(){
	 
	// validation 
		
	if ((document.newrequest.field.value=="")
	|| (document.newrequest.field.value=="")
	|| (document.newrequest.field.value=="")


	){
	    alert("All  indicated information is required. Please complete all fields");
	    exit();
	    }
	 
	});

	$('#back').click(function(){
		// scroll to the top of the form
	    $('html, body').animate({
	        scrollTop: $("#submitRequest").offset().top
	    }, 500);

	    // fade out step1, fade in step2
		$('#step2').fadeOut('fast', function() {
		  }); 
		$('#step1').fadeIn('slow', function() {
		  });  
	});	

});