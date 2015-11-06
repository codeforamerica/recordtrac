$(function() {
    $('#step1').fadeIn('fast');

    var validContact = false;
    var validAddress = false;
    var valid

    var addressValidator = new FormValidator('submitRequest', [{
        name: 'address_1',
        display: 'Address 1',
        rules: 'required'
    }, {
        name: 'city',
        display: 'City',
        rules: 'required'
    }, {
        name: 'zip_code',
        display: 'Zip Code',
        rules: 'required'
    }], function(errors, event) {
        if(errors.length === 0) {
            validAddress = true;
        }
    });

    var contactValidator = new FormValidator('submitRequest', [{
        name: 'email',
        display: 'Email',
        rules: 'required'
    }, {
        name: 'phone',
        display: 'Phone',
        rules: 'required'
    }, {
        name: 'fax',
        display: 'Fax',
        rules: 'required'
    }], function(errors, event) {
        if(errors.length < 3) {
            validContact = true;
        }
    });

    var validator = new FormValidator('submitRequest', [{
        name: 'request_agency',
        display: 'Request Agency',
        rules: 'required'
    }, {
        name: 'request_summary',
        display: 'Topic',
        rules: 'required'
    }, {
        name: 'request_text',
        display: 'Request Details',
        rules: 'required'
    }, {
        name: 'request_first_name',
        display: 'Requester First Name',
        rules: 'required'
    }, {
        name: 'request_last_name',
        display: 'Request Last Name',
        rules: 'required'
    }, {
       name: 'request_format',
       display: 'Request Format',
       rules: 'required'
    }, {
        name:'request_date',
        display: 'Request Date',
        rules: 'required'
    }, {
        name: 'request_contact_information',
        display: 'Request Contact Information',
        rules: 'required'
    }], function(errors, event) {
        if (errors.length > 0) {
            // Show the errors
            $('#step2').fadeOut('fast', function() {});
            var errorString = '';
            for (var i = 0, errorLength = errors.length; i < errorLength; i++) {
                errorString += errors[i].message + '<br />';
                if (errors[i].name === 'request_agency') {
                    $('#missing_agency').show();
                }
                if (errors[i].name === 'request_summary') {
                    $('#missing_summary').show();
                }
                if (errors[i].name === 'request_text') {
                    $('#missing_text').show();
                }
                if (errors[i].name === 'request_first_name') {
                    $('#missing_first_name').show();
                }
                if (errors[i].name === 'request_last_name') {
                    $('#missing_last_name').show();
                }
                if (errors[i].name == 'request_format'){
                    $('#missing_format').show();
                }
                if (errors[i].name== 'request_date'){
                    $('#missing_date').show();
                }
                if (!validContact && !validAddress) {
                    $('#missing_contact_information').show();
                }
            }
            var stepId = '#step2';
            var toolTipId = '#detailsTitle';

            if (errorString.indexOf("Request Category") >= 0 || errorString.indexOf("Request Agency") >= 0 || errorString.indexOf("Topic") >= 0) {
                stepId = '#step1';
                toolTipId = '#categoryTitle';
            }

            $(stepId).fadeIn('slow', function() {
                $('html, body').animate({
                    scrollTop: $("#submitRequest").offset().top
                }, 500);
            });

        }
    });

    $('#button1').click(function() {
        // scroll to the top of the form
        $('html, body').animate({
            scrollTop: $("#submitRequest").offset().top
        }, 500);
        confirmation=confirm('By selecting "OK" you are acknowledging that this information will be available to the public');
        if(confirmation==true){
            //Do nothing and continue with the transition
        }
        else{
            exit();
        }
        // fade out step1, fade in step2
        $('#step1').fadeOut('fast', function() {});
        $('#step2').fadeIn('slow', function() {});
        $('#s1').removeClass('active');
        $('#s2').addClass('active');
    });

    $('#button2').click(function() {


    });

    $('#back').click(function() {
        // scroll to the top of the form
        $('html, body').animate({
            scrollTop: $("#submitRequest").offset().top
        }, 500);

        // fade out step1, fade in step2
        $('#step2').fadeOut('fast', function() {});
        $('#step1').fadeIn('slow', function() {});
    });
    $('#s1 a').click(function() {
        // when step one is clicked, go to step 1

        if (Modernizr.touch) {
            $('html, body').animate({
                scrollTop: $("#submitRequest").offset().top
            }, 500);
        } else {
            // don't scroll to the top
        }


        $('#step2').fadeOut('fast', function() {});
        $("#s2").removeClass("active");
        $("#s1").addClass("active");
        $('#step1').fadeIn('slow', function() {});
    });

    $('#s2 a').click(function() {
        // when step two is clicked, go to step 1

        // validation

        if (!$('#agency').val() || !$('#request_summary').val()) {
            alert("All indicated information is required. Please complete all fields");
            exit();
        }

        if (Modernizr.touch) {
            $('html, body').animate({
                scrollTop: $("#submitRequest").offset().top
            }, 500);
        } else {
            // don't scroll to the top
        }

        $('#step1').fadeOut('fast', function() {});
        $("#s1").removeClass("active");
        $("#s2").addClass("active");
        $('#step2').fadeIn('slow', function() {});
    });

});
