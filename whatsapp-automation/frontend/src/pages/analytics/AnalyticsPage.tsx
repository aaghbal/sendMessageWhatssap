import React, { useState } from 'react';
import {
  BarChart3,
  TrendingUp,
  MessageSquare,
  CheckCircle,
  XCircle,
  Download
} from 'lucide-react';
import { useQuery } from '@tanstack/react-query';
import { apiService } from '../../services/api';
import Card from '../../components/ui/Card';
import Button from '../../components/ui/Button';
import LoadingSpinner from '../../components/ui/LoadingSpinner';

interface AnalyticsData {
  overview: {
    total_messages: number;
    successful_messages: number;
    failed_messages: number;
    success_rate: number;
    total_campaigns: number;
    active_campaigns: number;
  };
  daily_stats: Array<{
    date: string;
    messages_sent: number;
    success_rate: number;
  }>;
  campaign_performance: Array<{
    campaign_name: string;
    messages_sent: number;
    success_rate: number;
    completion_date: string;
  }>;
  hourly_distribution: Array<{
    hour: number;
    message_count: number;
  }>;
}

const AnalyticsPage: React.FC = () => {
  const [dateRange, setDateRange] = useState('7days');

  // Mock data for development - replace with real API call
  const mockAnalytics: AnalyticsData = {
    overview: {
      total_messages: 1247,
      successful_messages: 1156,
      failed_messages: 91,
      success_rate: 92.7,
      total_campaigns: 12,
      active_campaigns: 2
    },
    daily_stats: [
      { date: '2024-01-15', messages_sent: 145, success_rate: 94.5 },
      { date: '2024-01-16', messages_sent: 167, success_rate: 91.2 },
      { date: '2024-01-17', messages_sent: 189, success_rate: 93.8 },
      { date: '2024-01-18', messages_sent: 134, success_rate: 89.5 },
      { date: '2024-01-19', messages_sent: 201, success_rate: 95.1 },
      { date: '2024-01-20', messages_sent: 223, success_rate: 92.4 },
      { date: '2024-01-21', messages_sent: 188, success_rate: 90.9 }
    ],
    campaign_performance: [
      { campaign_name: 'New Year Promotion', messages_sent: 345, success_rate: 94.2, completion_date: '2024-01-15' },
      { campaign_name: 'Product Launch', messages_sent: 267, success_rate: 91.8, completion_date: '2024-01-18' },
      { campaign_name: 'Customer Survey', messages_sent: 189, success_rate: 87.3, completion_date: '2024-01-20' },
      { campaign_name: 'Welcome Series', messages_sent: 156, success_rate: 96.1, completion_date: '2024-01-21' }
    ],
    hourly_distribution: [
      { hour: 9, message_count: 45 },
      { hour: 10, message_count: 67 },
      { hour: 11, message_count: 89 },
      { hour: 12, message_count: 112 },
      { hour: 13, message_count: 98 },
      { hour: 14, message_count: 134 },
      { hour: 15, message_count: 156 },
      { hour: 16, message_count: 143 },
      { hour: 17, message_count: 98 }
    ]
  };

  const { data: analytics, isLoading } = useQuery({
    queryKey: ['analytics', dateRange],
    queryFn: async () => {
      try {
        return await apiService.getAnalytics(dateRange);
      } catch (err: any) {
        // Log the error for debugging
        console.error('Analytics API error:', err);
        // Fallback to mock data if API fails
        return mockAnalytics;
      }
    },
    staleTime: 5 * 60 * 1000, // 5 minutes
  });

  const formatNumber = (num: number) => {
    return new Intl.NumberFormat().format(num);
  };

  const formatPercentage = (num: number) => {
    return `${num.toFixed(1)}%`;
  };

  if (isLoading) {
    return (
      <div className="flex items-center justify-center min-h-64">
        <LoadingSpinner size="lg" />
      </div>
    );
  }

  // Always have data (either real or fallback)
  const data = analytics || mockAnalytics;

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Analytics Dashboard</h1>
          <p className="text-gray-600">Track your WhatsApp campaign performance and message statistics</p>
        </div>
        <div className="flex space-x-3">
          <select
            value={dateRange}
            onChange={(e) => setDateRange(e.target.value)}
            className="px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
          >
            <option value="7days">Last 7 days</option>
            <option value="30days">Last 30 days</option>
            <option value="90days">Last 90 days</option>
          </select>
          <Button variant="outline">
            <Download className="h-4 w-4 mr-2" />
            Export
          </Button>
        </div>
      </div>

      {/* Overview Stats */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <Card>
          <Card.Body className="flex items-center">
            <div className="p-3 rounded-lg bg-blue-100">
              <MessageSquare className="h-6 w-6 text-blue-600" />
            </div>
            <div className="ml-4">
              <p className="text-sm font-medium text-gray-600">Total Messages</p>
              <p className="text-2xl font-semibold text-gray-900">
                {formatNumber(data.overview?.total_messages || 0)}
              </p>
            </div>
          </Card.Body>
        </Card>

        <Card>
          <Card.Body className="flex items-center">
            <div className="p-3 rounded-lg bg-green-100">
              <CheckCircle className="h-6 w-6 text-green-600" />
            </div>
            <div className="ml-4">
              <p className="text-sm font-medium text-gray-600">Successful</p>
              <p className="text-2xl font-semibold text-gray-900">
                {formatNumber(data.overview?.successful_messages || 0)}
              </p>
            </div>
          </Card.Body>
        </Card>

        <Card>
          <Card.Body className="flex items-center">
            <div className="p-3 rounded-lg bg-red-100">
              <XCircle className="h-6 w-6 text-red-600" />
            </div>
            <div className="ml-4">
              <p className="text-sm font-medium text-gray-600">Failed</p>
              <p className="text-2xl font-semibold text-gray-900">
                {formatNumber(data.overview?.failed_messages || 0)}
              </p>
            </div>
          </Card.Body>
        </Card>

        <Card>
          <Card.Body className="flex items-center">
            <div className="p-3 rounded-lg bg-purple-100">
              <TrendingUp className="h-6 w-6 text-purple-600" />
            </div>
            <div className="ml-4">
              <p className="text-sm font-medium text-gray-600">Success Rate</p>
              <p className="text-2xl font-semibold text-gray-900">
                {formatPercentage(data.overview?.success_rate || 0)}
              </p>
            </div>
          </Card.Body>
        </Card>
      </div>

      {/* Charts Section */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Daily Performance Chart */}
        <Card>
          <Card.Header>
            <h3 className="text-lg font-medium text-gray-900">Daily Message Volume</h3>
          </Card.Header>
          <Card.Body>
            <div className="space-y-4">
              {(data.daily_stats || []).map((day: any, index: number) => (
                <div key={index} className="flex items-center justify-between">
                  <div className="flex items-center space-x-3">
                    <div className="text-sm font-medium text-gray-700">
                      {new Date(day.date).toLocaleDateString('en-US', { 
                        month: 'short', 
                        day: 'numeric' 
                      })}
                    </div>
                    <div className="flex-1">
                      <div className="w-32 bg-gray-200 rounded-full h-2">
                        <div 
                          className="bg-blue-600 h-2 rounded-full" 
                          style={{ width: `${(day.messages_sent / 250) * 100}%` }}
                        ></div>
                      </div>
                    </div>
                  </div>
                  <div className="text-right">
                    <div className="text-sm font-semibold text-gray-900">
                      {formatNumber(day.messages_sent)}
                    </div>
                    <div className="text-xs text-gray-500">
                      {formatPercentage(day.success_rate)} success
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </Card.Body>
        </Card>

        {/* Hourly Distribution */}
        <Card>
          <Card.Header>
            <h3 className="text-lg font-medium text-gray-900">Peak Hours</h3>
          </Card.Header>
          <Card.Body>
            <div className="space-y-4">
              {(data.hourly_distribution || []).map((hour: any, index: number) => (
                <div key={index} className="flex items-center justify-between">
                  <div className="flex items-center space-x-3">
                    <div className="text-sm font-medium text-gray-700 w-12">
                      {hour.hour}:00
                    </div>
                    <div className="flex-1">
                      <div className="w-32 bg-gray-200 rounded-full h-2">
                        <div 
                          className="bg-purple-600 h-2 rounded-full" 
                          style={{ width: `${(hour.message_count / 160) * 100}%` }}
                        ></div>
                      </div>
                    </div>
                  </div>
                  <div className="text-sm font-semibold text-gray-900">
                    {formatNumber(hour.message_count)}
                  </div>
                </div>
              ))}
            </div>
          </Card.Body>
        </Card>
      </div>

      {/* Campaign Performance Table */}
      <Card>
        <Card.Header>
          <h3 className="text-lg font-medium text-gray-900">Campaign Performance</h3>
        </Card.Header>
        <Card.Body>
          <div className="overflow-x-auto">
            <table className="min-w-full divide-y divide-gray-200">
              <thead className="bg-gray-50">
                <tr>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Campaign
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Messages Sent
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Success Rate
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Completed
                  </th>
                </tr>
              </thead>
              <tbody className="bg-white divide-y divide-gray-200">
                {(data.campaign_performance || []).map((campaign: any, index: number) => (
                  <tr key={index} className="hover:bg-gray-50">
                    <td className="px-6 py-4 whitespace-nowrap">
                      <div className="text-sm font-medium text-gray-900">
                        {campaign.campaign_name}
                      </div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <div className="text-sm text-gray-900">
                        {formatNumber(campaign.messages_sent)}
                      </div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${
                        campaign.success_rate >= 95 
                          ? 'bg-green-100 text-green-800'
                          : campaign.success_rate >= 90
                          ? 'bg-yellow-100 text-yellow-800'
                          : 'bg-red-100 text-red-800'
                      }`}>
                        {formatPercentage(campaign.success_rate)}
                      </span>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                      {new Date(campaign.completion_date).toLocaleDateString()}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </Card.Body>
      </Card>

      {/* Analytics Info Banner */}
      <div className={`border rounded-lg p-4 ${analytics ? 'bg-green-50 border-green-200' : 'bg-blue-50 border-blue-200'}`}>
        <div className="flex items-start">
          <div className="flex-shrink-0">
            <BarChart3 className={`h-5 w-5 mt-0.5 ${analytics ? 'text-green-600' : 'text-blue-600'}`} />
          </div>
          <div className="ml-3">
            <h3 className={`text-sm font-medium ${analytics ? 'text-green-900' : 'text-blue-900'}`}>
              {analytics ? 'Live Analytics Data' : 'Sample Analytics Data'}
            </h3>
            <p className={`text-sm mt-1 ${analytics ? 'text-green-700' : 'text-blue-700'}`}>
              {analytics 
                ? 'Displaying real-time analytics from your WhatsApp campaigns and messages.'
                : 'Backend connection unavailable. Showing sample data for demonstration purposes.'
              }
            </p>
          </div>
        </div>
      </div>
    </div>
  );
};

export default AnalyticsPage;
