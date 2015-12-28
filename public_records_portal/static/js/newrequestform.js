$(function () {
    var business = ["Department of Consumer Affairs",
        "Mayor's Office of Contract Services",
        "Procurement Policy Board",
        "Small Business Services"]
    var cultureAndRecreation = ["Art Commission",
        "Department of Cultural Affairs",
        "Mayor's Office of Media and Entertainment",
        "Department of Parks and Recreation"]
    var education = ["Department of Education",
        "School Construction Authority"]
    var environment = ["Department of Environmental Protection",
        "Office of Environmental Remediation",
        "Office of Long-Term Planning & Sustainability",
        "Department of Sanitation"]
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
        "Office of the Mayor",
        "Office of Payroll Administration",
        "Department of Records and Information Services"]
    var health = ["Office of the Chief Medical Examiner",
        "Health and Hospitals Corporation",
        "Department of Health and Mental Hygiene"]
    var housingAndDevelopment = ["Loft Board",
        "Landmarks Preservation Commission",
        "Board of Standards and Appeals",
        "Housing Recovery Operations",
        "Department of City Planning",
        "New York City Housing Authority",
        "Department of Buildings",
        "New York City Housing Development Corporation"]
    var publicSafety = ["Civilian Complaint Review Board",
        "Commission to Combat POlice Corruption",
        "Board of Correction",
        "Department of Correction",
        "NYC Emergency Management",
        "New York City Fire Department",
        "Department of Investigation",
        "Police Department",
        "Department of Probation",
        "NYC Office of the Special Narcotics Prosecutor"]
    var socialServices = ["Department for the Aging",
        "Administration for Children's Services",
        "Department of Homeless Services",
        "Department of Housing Preservation and Development",
        "Human Resources Administration",
        "Department of Youth and Community Development"]
    var transportation = ["Taxi and Limousine Commission",
        "Department of Transportation"]

    $("#category_info").tooltip();

    $("#agency").ready(function () {
        vals = [];
        vals = business.concat(cultureAndRecreation, education, environment, governmentAdministration,
            health, housingAndDevelopment, publicSafety, socialServices, transportation);
        vals.sort();

        for (var i = 0; i < vals.length; i++) {
            if (vals[i]==($("#agency option:selected").text())){
                continue;
            }
            else{
                $("#agency").value = vals[i];
                $("#agency").append("<option value=\"" + vals[i] + "\">" + vals[i] + "</option>");
            }
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
            case 'Social Services':
                vals = socialServices;
                break;
            case 'Transportation':
                vals = transportation;
                break;
            default:
                vals = business.concat(cultureAndRecreation, education, environment, governmentAdministration,
                    health, housingAndDevelopment, publicSafety, socialServices, transportation);
                break;
        }

        var $jsontwo = $("#agency");

        $jsontwo.empty();
        vals.sort();
        for (var i = 0; i < vals.length; i++) {
            if (vals[i]==($("#agency option:selected").text())){
                $jsontwo.append("repeat agency");
                return;
            }
            else {
                $jsontwo.value = vals[i];
                $jsontwo.append("<option value=\"" + vals[i] + "\">" + vals[i] + "</option>");
            }
        }
        ;
    });

});

$(function () {

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
