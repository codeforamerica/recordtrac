$(function () {

    var business = ["Department of Consumer Affairs",
        "Mayor's Office of Contract Services",
        "Procurement Policy Board",
        "Small Business Services"]
    var civicServices = ["Department of Records and Information Services"]
    var cultureAndRecreation = ["Art Commission",
        "Department of Cultural Affairs",
        "Mayor's Office of Media and Entertainment",
        "Department of Parks and Recreation"]
    var education = ["Department of Education",
        "School Construction Authority"]
    var environment = ["Department of Environmental Protection",
        "Office of Environmental Remediation",
        "Office of Long-Term Planning & Sustainability"]
    var governmentAdministration = ["Office of the Actuary",
        "Office of Administrative Trials and Hearings",
        "Business Integrity Commission",
        "Department of Citywide Administrative Services",
        "Civil Service Commission",
        "Conflicts of Interest Board",
        "Design Commission",
        "Department of Design and Construction",
        "Equal Employment Practices Commission",
        "Department of Finance",
        "City Commission on Human Rights",
        "Department of Information Technology and Telecommunications",
        "Office of Labor Relations",
        "Law Department",
        "Office of Management and Budget",
        "Mayor's Office",
        "Office of Payroll Administration"]
    var health = ["Office of Chief Medical Examiner",
        "Health and Hospitals Corporation",
        "Department of Health and Mental Hygiene"]
    var housingAndDevelopment = ["Office of Chief Medical Examiner",
        "Health and Hospitals Corporation",
        "Department of Health and Mental Hygiene"]
    var publicSafety = ["Department of Buildings",
        "Department of City Planning",
        "New York City Housing Authority",
        "Housing Recovery Operations",
        "Landmarks Preservation Commission",
        "Loft Board",
        "Board of Standards and Appeals"]
    var socialServices = ["Department for the Aging",
        "Administration for Children's Services",
        "Department of Homeless Services",
        "Department of Housing Preservation and Development",
        "Human Resources Administration",
        "Department of Youth and Community Development"]
    var transportation = ["Taxi and Limousine Commission",
        "Department of Transportation"]

    $("#category_info").tooltip();

    $("#agency").ready(function(){
        vals = [];
        vals=business.concat(civicServices,cultureAndRecreation,education,environment,governmentAdministration,
                health,housingAndDevelopment,publicSafety,socialServices,transportation);
        vals.sort();

        for (var i = 0; i < vals.length; i++) {
            $("#agency").value = vals[i];
            $("#agency").append("<option value=\"" + vals[i] + "\">" + vals[i] + "</option>");
        }
    });

    $("#category").change(function () {
        var $dropdown = $(this);
        var key = $dropdown.val();
        var vals = [];

        switch (key) {
            case 'Business':
                vals = business;
                break;
            case 'Civic Services':
                vals = civicServices;
                break;
            case 'Culture and Recreation':
                vals = cultureAndRecreation;
                break;
            case 'Education':
                vals = education;
                break;
            case 'Environment':
                vals = environment;
                break;
            case 'Government Administration':
                vals = governmentAdministration;
                break;
            case 'Health':
                vals = health;
                break;
            case 'Housing':
                vals = housingAndDevelopment;
                break;
            case 'Public':
                vals = publicSafety;
                break;
            case 'Social':
                vals = socialServices;
                break;
            case 'Transportation':
                vals = transportation;
                break;
            default:
                vals=business.concat(civicServices,cultureAndRecreation,education,environment,governmentAdministration,
                    health,housingAndDevelopment,publicSafety,socialServices,transportation);
                break;
        }

        var $jsontwo = $("#agency");
        $jsontwo.empty();
        vals.sort();
        for (var i = 0; i < vals.length; i++) {
            $jsontwo.value = vals[i];
            $jsontwo.append("<option value=\"" + vals[i] + "\">" + vals[i] + "</option>");
        }
        ;
    });

});

$(function () {
    $('#step1').fadeIn('fast');

    var validContact = false;
    var validAddress = false;

    $('#submitRequest').validate({
        rules: {
            request_agency: {
                required: true,
                minlength: 1,
                maxlength: 5000

            },
            request_summary: {
                required: true,
                maxlength: 90
            },
            request_text: {
                required: true,
                minlength: 1,
                maxlength: 5000
            },
            request_first_name: {
                required: true,
                minlength: 1,
                maxlength: 5000
            },
            request_last_name: {
                required: true,
                minlength: 1,
                maxlength: 5000
            }
        },
        highlight: function (element) {
            $(element).closest('.control-group').removeClass('success').addClass('error');
        }
    });

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
    }], function (errors, event) {
        if (errors.length === 0) {
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
    }], function (errors, event) {
        if (errors.length < 3) {
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
        name: 'request_date',
        display: 'Request Date',
        rules: 'required'
    }, {
        name: 'request_contact_information',
        display: 'Request Contact Information',
        rules: 'required'
    }], function (errors, event) {
        if (errors.length > 0) {
            // Show the errors
            $('#step2').fadeOut('fast', function () {
            });
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
                if (errors[i].name == 'request_format') {
                    $('#missing_format').show();
                }
                if (errors[i].name == 'request_date') {
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

            $(stepId).fadeIn('slow', function () {
                $('html, body').animate({
                    scrollTop: $("#submitRequest").offset().top
                }, 500);
            });

        }
    });

    $('#button1').click(function () {
        // scroll to the top of the form
        $('html, body').animate({
            scrollTop: $("#submitRequest").offset().top
        }, 500);
        confirmation = confirm('By selecting "OK" you are acknowledging that this information will be available to the public');
        if (confirmation == true) {
            //Do nothing and continue with the transition
        }
        else {
            exit();
        }
        // fade out step1, fade in step2
        $('#step1').fadeOut('fast', function () {
        });
        $('#step2').fadeIn('slow', function () {
        });
        $('#s1').removeClass('active');
        $('#s2').addClass('active');
    });

    $('#button2').click(function () {


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
    function maxLength(el) {
        if (!('maxLength' in el)) {
            var max = el.attributes.maxLength;
            el.onkeypress = function () {
                if (this.value.length >= max) return false;
            };
        }
    }

    maxLength(document.getElementById("request_summary"));

    // displays characters remaining, highlights extra characters
    var text_max = 90;
    $('#summary_count').text(text_max + ' characters remaining');

    $('#request_summary').keyup(function () {
        var text_length = $('#request_summary').val().length;
        var text_remaining = text_max - text_length;
        $('#summary_count').text(text_remaining + ' characters remaining');
        console.log(text_remaining);
        if (text_remaining < 0) {
            document.getElementById("summary_count").style.color = "black";
        } else {
            document.getElementById("summary_count").style.color = "black";
        }
    });

    maxLength(document.getElementById("request_text"));

    // displays characters remaining, highlights extra characters
    var text_max2 = 5000;
    $('#text_count').text(text_max2 + ' characters remaining');

    $('#request_text').keyup(function () {
        var text_length = $('#request_text').val().length;
        var text_remaining = text_max2 - text_length;
        $('#text_count').text(text_remaining + ' characters remaining');
        console.log(text_remaining);
        if (text_remaining < 0) {
            document.getElementById("text_count").style.color = "black";
        } else {
            document.getElementById("text_count").style.color = "black";
        }
    });
});