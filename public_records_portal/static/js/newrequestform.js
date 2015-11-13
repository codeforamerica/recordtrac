

$(function() {

            var business = ["Department of Consumer Affairs", "Mayor's Office of Contract Services", "Procurement Policy Board",
            "Small Business Sercies"]
            var civicServices =["Department of Records"]
            var cultureAndRecreation = ["Art Commission","Department of Cultural Affairs", "Mayor's Office of Media and Entertainment",
                "Department of Parks and Recreation"]
            var education = ["Department of Education", "School Construction Authroity"]
            var environment = ["Department of Environmental Protection","Office of Environmental Remediation",
                                   "Office of Long-Term Planning & Sustainability"]
            var governmentAdministration=["NYC Office of the Actuary","Office of Administrative Trials and Hearings",
                                                 "Business Integrity Commission","Department of Citywide Administrative Services",
                                                 "Civil Service Commission", "Conflicts of Interest Board","Design Commission",
                                                 "Department of Design and Construction","Equal Employment Practices Commission",
                                                 "Department of Finance","City Commission on Human Rights",
                                                 "Department of Information Technology and Telecommunications",
                                                 "NYC Office of Labor Relations",
                                                 "Law Department",
                                                 "Office of Management and Budget",
                                                 "Mayor's Office",
                                                 "Office of Payroll Administration"]
            var health = ["NYC Office of Chief Medical Examiner", "Health and Hospitals Corporation", "Department of Health and Mental Hygiene"]
            var housingAndDevelopment = ["NYC Office of Chief Medical Examiner", "Health and Hospitals Corporation",
                              "Department of Health and Mental Hygiene"]
            var publicSafety = ["Department of Buildings","Department of City Planning", "New York City Housing Authroity",
                "Housing Recovery Operations", "Landmarks Preservation Commission","Loft Board","Board of Standards and Appeals"]
            var socialServices = ["Department for the Aging","Administration for Children's Services",
                                       "Department of Homeless Services","Department of Housing Preservations and Development",
                                       "Human Resources Administration","Department of Youth and Community Development"]
            var transportation = ["Taxi and Limousine Commission","Department of Transportation"]


        $("#category").change(function() {

            var $dropdown = $(this);

                var key = $dropdown.val();
                var vals = [];

                switch(key) {
                    case 'Business':
                        vals = business;
                        break;
                    case 'Civic Services':
                        vals = civicServices;
                        break;
                    case 'Culture and Recreation':
                        vals=cultureAndRecreation;
                        break;
                    case 'Education':
                        vals=education;
                        break;
                    case 'Environment':
                        vals=environment;
                        break;
                    case 'Government Administration':
                        vals=governmentAdministration;
                        break;
                    case 'Health':
                        vals=health;
                        break;
                    case 'Housing':
                        vals=housingAndDevelopment;
                        break;
                    case 'Public':
                        vals=publicSafety;
                        break;
                    case 'Social':
                        vals=socialServices;
                        break;
                    case 'Transportation':
                        vals=transportation;
                        break;
                    case 'base':
                        vals = ['Please choose from above'];
                }

                var $jsontwo = $("#agency");
                $jsontwo.empty();
                for (var i = 0 ; i < vals.length; i++){
                    $jsontwo.append("<option>" + vals[i] + "</option>");
                };
        });

});



$(function () {
    $('#step1').fadeIn('fast');

    var validContact = false;
    var validAddress = false;


    $('#submitRequest').validate({
        rules: {
            request_agency: {
                required: true
            },
            request_summary: {
                required: true,
                maxlength: 90
            },
            request_text: {
                required: true
            },
            request_first_name: {
                required: true
            },
            request_last_name: {
                required: true
            }
        },
        highlight: function (element) {
            $(element).closest('.control-group').removeClass('success').addClass('error');
        }
    });


    $('#button1').click(function () {

        if ($('#submitRequest').valid()) {
            // scroll to the top of the form
            $('html, body').animate({
                scrollTop: $("#submitRequest").offset().top
            }, 500);

            // fade out step1, fade in step2
            $('#step1').fadeOut('fast', function () {
            });
            $('#step2').fadeIn('slow', function () {
            });
            $('#s1').removeClass('active');
            $('#s2').addClass('active');
        }

    });

    $('#button2').click(function (e) {

        if ($('#request_address_street_one').val() && $('#request_address_city').val() && $('#request_address_zip').val()) {
            validAddress = true;
        }

        if ($('#request_email').val() || $('#request_email').val() || $('#request_email').val() || validAddress) {
            validContact = true;
        }

        if ($('#submitRequest').valid() && !validContact) {
            e.preventDefault();
            $('#missing_contact_information').show();
            $('#request_email').focus();
        }
    });

    $('#back').click(function () {
        // scroll to the top of the form
        $('html, body').animate({
            scrollTop: $("#submitRequest").offset().top
        }, 500);

        // fade out step1, fade in step2
        $('#step2').fadeOut('fast', function () {
        });
        $('#step1').fadeIn('slow', function () {
        });
    });
    $('#s1 a').click(function () {
        // when step one is clicked, go to step 1

        if (Modernizr.touch) {
            $('html, body').animate({
                scrollTop: $("#submitRequest").offset().top
            }, 500);
        } else {
            // don't scroll to the top
        }


        $('#step2').fadeOut('fast', function () {
        });
        $("#s2").removeClass("active");
        $("#s1").addClass("active");
        $('#step1').fadeIn('slow', function () {
        });
    });

    $('#s2 a').click(function () {
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

        $('#step1').fadeOut('fast', function () {
        });
        $("#s1").removeClass("active");
        $("#s2").addClass("active");
        $('#step2').fadeIn('slow', function () {
        });
    });

    // displays characters remaining, highlights extra characters
    var text_max = 90;
    $('#summary_count').text(text_max + ' characters remaining');

    $('#request_summary').keyup(function () {
        var summary = $('request_summary');
        var text_length = $('#request_summary').val().length;
        var text_remaining = text_max - text_length;
        if (text_remaining < 0) {
            //highlight range of summary (90:) red
        }
        $('#summary_count').text(text_remaining + ' characters remaining');
    });
});