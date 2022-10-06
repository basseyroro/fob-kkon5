{
    'name' : 'Weblearns General Module',
    'version' : '1.1',
    'summary': 'General module upgrade HR',
    'author': 'Weblearns',
    'sequence': 10,
    'description': "General module upgrade HR",
    'category': 'Human Resource',
    'website': 'https://onlineweblearns.blogspot.com',
    'depends' : ['hr', 'hr_payroll'],
    'data': [
        "security/ir.model.access.csv",
        "view/hr_view.xml",
        "view/hr_extend_view.xml"
    ],
    'installable': True,
    'license': 'LGPL-3',
}
