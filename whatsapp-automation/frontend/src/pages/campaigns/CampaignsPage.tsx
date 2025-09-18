import React from 'react';
import { Plus, Search, Filter } from 'lucide-react';
import { useNavigate } from 'react-router-dom';
import Button from '../../components/ui/Button';
import Card from '../../components/ui/Card';
import Input from '../../components/ui/Input';

const CampaignsPage: React.FC = () => {
  const navigate = useNavigate();

  const handleCreateCampaign = () => {
    navigate('/campaigns/create');
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Campaigns</h1>
          <p className="text-gray-600">Create and manage your WhatsApp campaigns</p>
        </div>
        <Button onClick={handleCreateCampaign}>
          <Plus className="h-4 w-4 mr-2" />
          Create Campaign
        </Button>
      </div>

      {/* Filters and Search */}
      <Card>
        <Card.Body>
          <div className="flex items-center space-x-4">
            <div className="flex-1 relative">
              <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-gray-400" />
              <Input
                type="text"
                placeholder="Search campaigns..."
                className="pl-10"
              />
            </div>
            <Button variant="outline">
              <Filter className="h-4 w-4 mr-2" />
              Filter
            </Button>
          </div>
        </Card.Body>
      </Card>

      {/* Empty State */}
      <Card>
        <Card.Body>
          <div className="text-center py-12">
            <div className="mx-auto w-24 h-24 bg-gray-100 rounded-full flex items-center justify-center mb-4">
              <Plus className="h-12 w-12 text-gray-400" />
            </div>
            <h3 className="text-lg font-medium text-gray-900 mb-2">No campaigns yet</h3>
            <p className="text-gray-600 mb-6 max-w-md mx-auto">
              Get started by creating your first WhatsApp campaign. You can send messages to multiple contacts at once.
            </p>
            <Button onClick={handleCreateCampaign}>
              <Plus className="h-4 w-4 mr-2" />
              Create Your First Campaign
            </Button>
          </div>
        </Card.Body>
      </Card>

      {/* Instructions */}
      <Card>
        <Card.Header>
          <h3 className="text-lg font-medium text-gray-900">Getting Started</h3>
        </Card.Header>
        <Card.Body>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            <div className="text-center">
              <div className="w-12 h-12 bg-blue-100 rounded-lg flex items-center justify-center mx-auto mb-4">
                <span className="text-lg font-bold text-blue-600">1</span>
              </div>
              <h4 className="font-medium text-gray-900 mb-2">Add Contacts</h4>
              <p className="text-sm text-gray-600">
                Import or manually add WhatsApp contacts to your contact list.
              </p>
            </div>
            <div className="text-center">
              <div className="w-12 h-12 bg-green-100 rounded-lg flex items-center justify-center mx-auto mb-4">
                <span className="text-lg font-bold text-green-600">2</span>
              </div>
              <h4 className="font-medium text-gray-900 mb-2">Create Template</h4>
              <p className="text-sm text-gray-600">
                Design your message template with personalized content.
              </p>
            </div>
            <div className="text-center">
              <div className="w-12 h-12 bg-purple-100 rounded-lg flex items-center justify-center mx-auto mb-4">
                <span className="text-lg font-bold text-purple-600">3</span>
              </div>
              <h4 className="font-medium text-gray-900 mb-2">Launch Campaign</h4>
              <p className="text-sm text-gray-600">
                Select contacts, choose template, and send your campaign.
              </p>
            </div>
          </div>
        </Card.Body>
      </Card>
    </div>
  );
};

export default CampaignsPage;
