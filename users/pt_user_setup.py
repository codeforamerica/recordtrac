non_partner_agencies = [
    "Administration for Children's Services",
    "Art Commission",
    "Board of Correction",
    "Board of Standards and Appeals",
    "Business Integrity Commission",
    "Civil Service Commission",
    "Civilian Complaint Review Board",
    "Commission to Combat Police Corruption",
    "Conflicts of Interest Board",
    "Department for the Aging",
    "Department of Buildings",
    "Department of City Planning",
    "Department of Citywide Administrative Services",
    "Department of Consumer Affairs",
    "Department of Correction",
    "Department of Cultural Affairs",
    "Department of Design and Construction",
    "Department of Environmental Protection",
    "Department of Finance",
    "Department of Health and Mental Hygiene",
    "Department of Homeless Services",
    "Department of Housing Preservations and Development",
    "Department of Investigation",
    "Department of Parks and Recreation",
    "Department of Probation",
    "Department of Transporation",
    "Department of Youth and Community Development",
    "Design Commission",
    "Equal Employment Practices Commission",
    "Health and Hospitals Corporation",
    "Housing Recovery Operations",
    "Human Resources Administration",
    "Landmarks Preservation Commission",
    "Law Department",
    "Loft Board",
    "New York City Fire Department",
    "New York City Housing Authority",
    "Office of Environmental Remediation",
    "Office of Labor Relations",
    "Office of Long-Term Planning & Sustainability",
    "Office of Management and Budget",
    "Office of Payroll Administration",
    "Office of the Actuary",
    "Office of the Special Narcotics Prosecutor",
    "Police Department",
    "Procurement Policy Board",
    "School Construction Authority",
    "Small Business Services",
    "Taxi and Limousine Commission"
]
partner_agencies = [
    "City Commission on Human Rights",
    "Department of Education",
    "Department of Information Technology and Telecommunications",
    "Department of Records and Information Services",
    "Mayor's Office of Contract Services",
    "Mayor's Office of Media and Entertainment",
    "Office of Administrative Trials and Hearings",
    "Office of the Chief Medical Examiner",
    "Office of Emergency Management",
    "Office of the Mayor",
]

k = 1
staff = open("staff_pt.csv", "w")
liaisons = open("liaisons_pt.csv", "w")

liaisons.write('department name,PRR liaison,PRR backup')
staff.write('name,email,department name,phone number')

for i in range(len(partner_agencies) - 1):
    liaisons.write("%s,psstestuser%02d@mailinator.com\n" % (partner_agencies[i], k))
    for j in range(30):
        staff.write("PTFname PTLname,psstestuser000%02d@mailinator.com,%s,311\n" %
                    (k, partner_agencies[i]))
        k += 1
for i in range(len(non_partner_agencies) - 1):
    staff.write("PTFname PTLname,psstestuser000%02d@mailinator.com,%s,311\n" %
                    (k, non_partner_agencies[i]))
    liaisons.write("%s,psstestuser%02d@mailinator.com\n" % (non_partner_agencies[i], k))
    k += 1

