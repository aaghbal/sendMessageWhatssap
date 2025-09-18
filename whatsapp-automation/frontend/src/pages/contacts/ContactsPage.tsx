import React, { useState } from 'react';
import { Plus, Search, Filter, Phone, User, Mail, Edit, Trash2, Upload, MessageSquare } from 'lucide-react';
import { useNavigate } from 'react-router-dom';
import Button from '../../components/ui/Button';
import Card from '../../components/ui/Card';
import Input from '../../components/ui/Input';

// Mock data for demonstration
const mockContacts = [
  {
    id: 1,
    name: 'John Doe',
    phone: '+1234567890',
    email: 'john@example.com',
    country_code: '+1',
    created_at: '2025-09-15',
    is_active: true
  },
  {
    id: 2,
    name: 'Jane Smith',
    phone: '+1987654321',
    email: 'jane@example.com',
    country_code: '+1',
    created_at: '2025-09-14',
    is_active: true
  },
  {
    id: 3,
    name: 'Ahmed Hassan',
    phone: '+201234567890',
    email: 'ahmed@example.com',
    country_code: '+20',
    created_at: '2025-09-13',
    is_active: false
  }
];

const ContactsPage: React.FC = () => {
  const [contacts, setContacts] = useState(mockContacts);
  const [searchTerm, setSearchTerm] = useState('');
  const navigate = useNavigate();

  const handleCreateContact = () => {
    navigate('/contacts/create');
  };

  const handleEditContact = (contactId: number) => {
    navigate(`/contacts/edit/${contactId}`);
  };

  const handleSendMessage = (contact: any) => {
    // Navigate to campaign creation with pre-selected contact
    navigate('/campaigns/create', { 
      state: { 
        preSelectedContacts: [contact],
        fromContactCreation: true 
      } 
    });
  };

  const handleDeleteContact = (contactId: number) => {
    if (window.confirm('Are you sure you want to delete this contact?')) {
      setContacts(contacts.filter(contact => contact.id !== contactId));
    }
  };

  const filteredContacts = contacts.filter(contact =>
    contact.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
    contact.phone.includes(searchTerm) ||
    contact.email.toLowerCase().includes(searchTerm.toLowerCase())
  );

  const activeContacts = contacts.filter(contact => contact.is_active).length;
  const totalContacts = contacts.length;

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Contacts</h1>
          <p className="text-gray-600">Manage your WhatsApp contacts</p>
        </div>
        <div className="flex space-x-3">
          <Button variant="outline">
            <Upload className="h-4 w-4 mr-2" />
            Import
          </Button>
          <Button onClick={handleCreateContact}>
            <Plus className="h-4 w-4 mr-2" />
            Add Contact
          </Button>
        </div>
      </div>

      {/* Stats Cards */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <Card>
          <Card.Body className="flex items-center">
            <div className="p-3 rounded-lg bg-blue-100">
              <User className="h-6 w-6 text-blue-600" />
            </div>
            <div className="ml-4">
              <p className="text-sm font-medium text-gray-600">Total Contacts</p>
              <p className="text-2xl font-semibold text-gray-900">{totalContacts}</p>
            </div>
          </Card.Body>
        </Card>

        <Card>
          <Card.Body className="flex items-center">
            <div className="p-3 rounded-lg bg-green-100">
              <Phone className="h-6 w-6 text-green-600" />
            </div>
            <div className="ml-4">
              <p className="text-sm font-medium text-gray-600">Active Contacts</p>
              <p className="text-2xl font-semibold text-gray-900">{activeContacts}</p>
            </div>
          </Card.Body>
        </Card>

        <Card>
          <Card.Body className="flex items-center">
            <div className="p-3 rounded-lg bg-orange-100">
              <Mail className="h-6 w-6 text-orange-600" />
            </div>
            <div className="ml-4">
              <p className="text-sm font-medium text-gray-600">With Email</p>
              <p className="text-2xl font-semibold text-gray-900">
                {contacts.filter(c => c.email).length}
              </p>
            </div>
          </Card.Body>
        </Card>
      </div>

      {/* Search and Filters */}
      <Card>
        <Card.Body>
          <div className="flex items-center space-x-4">
            <div className="flex-1 relative">
              <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-gray-400" />
              <Input
                type="text"
                placeholder="Search contacts by name, phone, or email..."
                className="pl-10"
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
              />
            </div>
            <Button variant="outline">
              <Filter className="h-4 w-4 mr-2" />
              Filter
            </Button>
          </div>
        </Card.Body>
      </Card>

      {/* Contacts Table */}
      <Card>
        <Card.Header>
          <div className="flex items-center justify-between">
            <h3 className="text-lg font-medium text-gray-900">All Contacts</h3>
            <span className="text-sm text-gray-500">
              {filteredContacts.length} of {totalContacts} contacts
            </span>
          </div>
        </Card.Header>
        <Card.Body className="p-0">
          {filteredContacts.length > 0 ? (
            <div className="overflow-x-auto">
              <table className="min-w-full divide-y divide-gray-200">
                <thead className="bg-gray-50">
                  <tr>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Contact
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Phone
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Email
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Status
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Added
                    </th>
                    <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Actions
                    </th>
                  </tr>
                </thead>
                <tbody className="bg-white divide-y divide-gray-200">
                  {filteredContacts.map((contact) => (
                    <tr key={contact.id} className="hover:bg-gray-50">
                      <td className="px-6 py-4 whitespace-nowrap">
                        <div className="flex items-center">
                          <div className="flex-shrink-0 h-10 w-10">
                            <div className="h-10 w-10 rounded-full bg-primary-100 flex items-center justify-center">
                              <User className="h-5 w-5 text-primary-600" />
                            </div>
                          </div>
                          <div className="ml-4">
                            <div className="text-sm font-medium text-gray-900">
                              {contact.name}
                            </div>
                          </div>
                        </div>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <div className="flex items-center">
                          <Phone className="h-4 w-4 text-gray-400 mr-2" />
                          <span className="text-sm text-gray-900">{contact.phone}</span>
                        </div>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <div className="flex items-center">
                          <Mail className="h-4 w-4 text-gray-400 mr-2" />
                          <span className="text-sm text-gray-500">{contact.email}</span>
                        </div>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${
                          contact.is_active 
                            ? 'bg-green-100 text-green-800' 
                            : 'bg-gray-100 text-gray-800'
                        }`}>
                          {contact.is_active ? 'Active' : 'Inactive'}
                        </span>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                        {new Date(contact.created_at).toLocaleDateString()}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
                        <div className="flex items-center justify-end space-x-2">
                          <Button
                            variant="outline"
                            size="sm"
                            onClick={() => handleSendMessage(contact)}
                            className="text-green-600 hover:text-green-700 border-green-300 hover:bg-green-50"
                          >
                            <MessageSquare className="h-3 w-3" />
                          </Button>
                          <Button
                            variant="outline"
                            size="sm"
                            onClick={() => handleEditContact(contact.id)}
                          >
                            <Edit className="h-3 w-3" />
                          </Button>
                          <Button
                            variant="outline"
                            size="sm"
                            onClick={() => handleDeleteContact(contact.id)}
                            className="text-red-600 hover:text-red-700"
                          >
                            <Trash2 className="h-3 w-3" />
                          </Button>
                        </div>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          ) : (
            <div className="text-center py-12">
              <User className="mx-auto h-12 w-12 text-gray-400" />
              <h3 className="mt-2 text-sm font-medium text-gray-900">
                {searchTerm ? 'No contacts found' : 'No contacts yet'}
              </h3>
              <p className="mt-1 text-sm text-gray-500">
                {searchTerm 
                  ? 'Try adjusting your search terms'
                  : 'Get started by adding your first contact.'
                }
              </p>
              {!searchTerm && (
                <Button className="mt-4" onClick={handleCreateContact}>
                  <Plus className="h-4 w-4 mr-2" />
                  Add Your First Contact
                </Button>
              )}
            </div>
          )}
        </Card.Body>
      </Card>

      {/* Quick Actions */}
      <Card>
        <Card.Header>
          <h3 className="text-lg font-medium text-gray-900">Quick Actions</h3>
        </Card.Header>
        <Card.Body>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <Button variant="outline" className="justify-start h-auto p-4">
              <div className="text-left">
                <div className="flex items-center mb-2">
                  <Upload className="h-5 w-5 text-primary-600 mr-2" />
                  <span className="font-medium">Import Contacts</span>
                </div>
                <p className="text-sm text-gray-600">
                  Upload a CSV file with your contacts
                </p>
              </div>
            </Button>

            <Button variant="outline" className="justify-start h-auto p-4">
              <div className="text-left">
                <div className="flex items-center mb-2">
                  <Plus className="h-5 w-5 text-primary-600 mr-2" />
                  <span className="font-medium">Create Group</span>
                </div>
                <p className="text-sm text-gray-600">
                  Organize contacts into groups
                </p>
              </div>
            </Button>

            <Button variant="outline" className="justify-start h-auto p-4">
              <div className="text-left">
                <div className="flex items-center mb-2">
                  <Phone className="h-5 w-5 text-primary-600 mr-2" />
                  <span className="font-medium">Bulk Actions</span>
                </div>
                <p className="text-sm text-gray-600">
                  Perform actions on multiple contacts
                </p>
              </div>
            </Button>
          </div>
        </Card.Body>
      </Card>
    </div>
  );
};

export default ContactsPage;
