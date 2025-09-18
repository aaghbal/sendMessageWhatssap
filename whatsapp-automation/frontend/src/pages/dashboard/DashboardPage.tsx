import React from 'react';
import { 
  Users, 
  MessageSquare, 
  Send, 
  Calendar,
  Activity
} from 'lucide-react';
import { useQuery } from '@tanstack/react-query';
import { useNavigate } from 'react-router-dom';
import { apiService } from '../../services/api';
import { DashboardStats } from '../../types';
import Card from '../../components/ui/Card';
import LoadingSpinner from '../../components/ui/LoadingSpinner';
import Button from '../../components/ui/Button';

const DashboardPage: React.FC = () => {
  const navigate = useNavigate();
  const { data: stats, isLoading, error } = useQuery<DashboardStats>({
    queryKey: ['dashboard-stats'],
    queryFn: () => apiService.getDashboardStats(),
  });

  const handleCreateCampaign = () => {
    navigate('/campaigns');
  };

  const formatNumber = (num: number) => {
    return new Intl.NumberFormat().format(num);
  };

  const formatPercentage = (num: number) => {
    return `${num.toFixed(1)}%`;
  };

  const statCards = [
    {
      title: 'Total Contacts',
      value: stats?.total_contacts || 0,
      icon: Users,
      color: 'text-blue-600',
      bgColor: 'bg-blue-100',
    },
    {
      title: 'Templates',
      value: stats?.total_templates || 0,
      icon: MessageSquare,
      color: 'text-green-600',
      bgColor: 'bg-green-100',
    },
    {
      title: 'Campaigns',
      value: stats?.total_campaigns || 0,
      icon: Send,
      color: 'text-purple-600',
      bgColor: 'bg-purple-100',
    },
    {
      title: 'Active Campaigns',
      value: stats?.active_campaigns || 0,
      icon: Activity,
      color: 'text-orange-600',
      bgColor: 'bg-orange-100',
    },
  ];

  const messageStats = [
    {
      title: 'Messages Today',
      value: stats?.messages_sent_today || 0,
      color: 'text-blue-600',
    },
    {
      title: 'Messages This Month',
      value: stats?.messages_sent_this_month || 0,
      color: 'text-green-600',
    },
    {
      title: 'Success Rate',
      value: formatPercentage(stats?.success_rate_this_month || 0),
      color: 'text-purple-600',
    },
  ];

  if (isLoading) {
    return (
      <div className="flex items-center justify-center min-h-64">
        <LoadingSpinner size="lg" />
      </div>
    );
  }

  if (error) {
    return (
      <div className="text-center py-12">
        <p className="text-red-600">Error loading dashboard data</p>
      </div>
    );
  }

  return (
    <div className="space-y-8">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Dashboard</h1>
          <p className="text-gray-600">Overview of your WhatsApp automation</p>
        </div>
        <div className="flex space-x-4">
          <Button variant="outline">
            View Reports
          </Button>
          <Button onClick={handleCreateCampaign}>
            Create Campaign
          </Button>
        </div>
      </div>

      {/* Stats Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        {statCards.map((stat, index) => {
          const Icon = stat.icon;
          return (
            <Card key={index}>
              <Card.Body className="flex items-center">
                <div className={`p-3 rounded-lg ${stat.bgColor}`}>
                  <Icon className={`h-6 w-6 ${stat.color}`} />
                </div>
                <div className="ml-4">
                  <p className="text-sm font-medium text-gray-600">{stat.title}</p>
                  <p className="text-2xl font-semibold text-gray-900">
                    {formatNumber(stat.value)}
                  </p>
                </div>
              </Card.Body>
            </Card>
          );
        })}
      </div>

      {/* Message Stats */}
      <Card>
        <Card.Header>
          <h3 className="text-lg font-medium text-gray-900">Message Statistics</h3>
        </Card.Header>
        <Card.Body>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            {messageStats.map((stat, index) => (
              <div key={index} className="text-center">
                <p className="text-sm font-medium text-gray-600">{stat.title}</p>
                <p className={`text-3xl font-bold ${stat.color}`}>
                  {typeof stat.value === 'string' ? stat.value : formatNumber(stat.value)}
                </p>
              </div>
            ))}
          </div>
        </Card.Body>
      </Card>

      {/* Recent Campaigns */}
      <Card>
        <Card.Header className="flex items-center justify-between">
          <h3 className="text-lg font-medium text-gray-900">Recent Campaigns</h3>
          <Button variant="outline" size="sm">
            View All
          </Button>
        </Card.Header>
        <Card.Body>
          {stats?.recent_campaigns && stats.recent_campaigns.length > 0 ? (
            <div className="space-y-4">
              {stats.recent_campaigns.map((campaign) => (
                <div key={campaign.id} className="flex items-center justify-between p-4 border border-gray-200 rounded-lg">
                  <div>
                    <h4 className="font-medium text-gray-900">{campaign.name}</h4>
                    <p className="text-sm text-gray-600">{campaign.description}</p>
                    <div className="flex items-center mt-2 space-x-4">
                      <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${
                        campaign.status === 'completed' 
                          ? 'bg-green-100 text-green-800'
                          : campaign.status === 'running'
                          ? 'bg-blue-100 text-blue-800'
                          : campaign.status === 'failed'
                          ? 'bg-red-100 text-red-800'
                          : 'bg-gray-100 text-gray-800'
                      }`}>
                        {campaign.status}
                      </span>
                      <span className="text-xs text-gray-500 flex items-center">
                        <Calendar className="h-3 w-3 mr-1" />
                        {new Date(campaign.created_at).toLocaleDateString()}
                      </span>
                    </div>
                  </div>
                  <Button variant="outline" size="sm">
                    View Details
                  </Button>
                </div>
              ))}
            </div>
          ) : (
            <div className="text-center py-8">
              <Send className="mx-auto h-12 w-12 text-gray-400" />
              <h3 className="mt-2 text-sm font-medium text-gray-900">No campaigns yet</h3>
              <p className="mt-1 text-sm text-gray-500">
                Get started by creating your first campaign.
              </p>
              <Button className="mt-4" onClick={handleCreateCampaign}>
                Create Campaign
              </Button>
            </div>
          )}
        </Card.Body>
      </Card>
    </div>
  );
};

export default DashboardPage;
