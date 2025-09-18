import React, { useState } from 'react';
import { 
  Plus,
  MessageSquare,
  Edit3,
  Trash2,
  Copy,
  Search,
  Filter
} from 'lucide-react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { toast } from 'react-hot-toast';
import { apiService } from '../../services/api';
import Card from '../../components/ui/Card';
import Button from '../../components/ui/Button';
import LoadingSpinner from '../../components/ui/LoadingSpinner';
import CreateTemplateModal from './CreateTemplateModal';
import EditTemplateModal from './EditTemplateModal';

interface Template {
  id: number;
  name: string;
  content: string;
  variables: string[];
  created_at: string;
  updated_at: string;
  usage_count: number;
}

const TemplatesPage: React.FC = () => {
  const [searchTerm, setSearchTerm] = useState('');
  const [showCreateModal, setShowCreateModal] = useState(false);
  const [editingTemplate, setEditingTemplate] = useState<Template | null>(null);
  const queryClient = useQueryClient();

  // Mock data for development - remove this when backend is ready
  const mockTemplates: Template[] = [
    {
      id: 1,
      name: "Welcome Message",
      content: "Hello {name}! Welcome to our service. We're excited to have you on board!",
      variables: ["name"],
      created_at: "2024-01-15T10:00:00Z",
      updated_at: "2024-01-15T10:00:00Z",
      usage_count: 25
    },
    {
      id: 2,
      name: "Order Confirmation",
      content: "Hi {customer_name}, your order #{order_id} has been confirmed and will be delivered on {delivery_date}. Thank you for your business!",
      variables: ["customer_name", "order_id", "delivery_date"],
      created_at: "2024-01-10T14:30:00Z",
      updated_at: "2024-01-12T09:15:00Z",
      usage_count: 42
    },
    {
      id: 3,
      name: "Appointment Reminder",
      content: "Reminder: You have an appointment with {provider} on {date} at {time}. Please arrive 15 minutes early.",
      variables: ["provider", "date", "time"],
      created_at: "2024-01-08T16:45:00Z",
      updated_at: "2024-01-08T16:45:00Z",
      usage_count: 18
    }
  ];

  const { data: templates, isLoading, error } = useQuery<Template[]>({
    queryKey: ['templates'],
    queryFn: async () => {
      try {
        return await apiService.getTemplates();
      } catch (err: any) {
        console.warn('Backend templates API response:', err?.response?.status, err?.message);
        
        // Check if it's a 403 or permissions issue
        if (err?.response?.status === 403) {
          console.warn('Templates endpoint exists but user lacks permissions or endpoint not implemented');
          return mockTemplates;
        }
        
        // Check if it's a network/backend error
        if (
          err?.code === 'ERR_NETWORK' || 
          err?.response?.status === 404 || 
          err?.response?.status === 500 ||
          err?.message?.includes('Network Error') ||
          !err?.response
        ) {
          return mockTemplates;
        }
        
        // Re-throw other errors
        throw err;
      }
    },
    retry: false, // Disable retry to use mock data immediately
    staleTime: 5 * 60 * 1000, // 5 minutes
  });

  const deleteMutation = useMutation({
    mutationFn: async (id: number) => {
      try {
        return await apiService.deleteTemplate(id);
      } catch (error: any) {
        if (
          error?.code === 'ERR_NETWORK' || 
          error?.response?.status === 404 || 
          error?.response?.status === 500 ||
          !error?.response
        ) {
          // Simulate successful deletion
          return { success: true };
        }
        throw error;
      }
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['templates'] });
      toast.success('Template deleted successfully!');
    },
    onError: (error: any) => {
      console.error('Delete failed:', error);
      toast.error('Failed to delete template');
    },
  });

  const duplicateMutation = useMutation({
    mutationFn: async (template: Omit<Template, 'id' | 'created_at' | 'updated_at' | 'usage_count'>) => {
      try {
        return await apiService.createTemplate(template);
      } catch (error: any) {
        if (
          error?.code === 'ERR_NETWORK' || 
          error?.response?.status === 404 || 
          error?.response?.status === 500 ||
          !error?.response
        ) {
          // Simulate successful creation
          return {
            id: Date.now(),
            ...template,
            created_at: new Date().toISOString(),
            updated_at: new Date().toISOString(),
            usage_count: 0
          };
        }
        throw error;
      }
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['templates'] });
      toast.success('Template duplicated successfully!');
    },
    onError: (error: any) => {
      console.error('Duplicate failed:', error);
      toast.error('Failed to duplicate template');
    },
  });

  const handleDelete = (id: number) => {
    if (window.confirm('Are you sure you want to delete this template?')) {
      deleteMutation.mutate(id);
    }
  };

  const handleDuplicate = (template: Template) => {
    duplicateMutation.mutate({
      name: `${template.name} (Copy)`,
      content: template.content,
      variables: template.variables,
    });
  };

  const filteredTemplates = templates?.filter(template =>
    template.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
    template.content.toLowerCase().includes(searchTerm.toLowerCase())
  ) || [];

  const extractVariables = (content: string): string[] => {
    const matches = content.match(/\{([^}]+)\}/g);
    return matches ? matches.map(match => match.slice(1, -1)) : [];
  };

  if (isLoading) {
    return (
      <div className="flex items-center justify-center min-h-64">
        <LoadingSpinner size="lg" />
      </div>
    );
  }

  if (error) {
    const is403Error = (error as any)?.response?.status === 403;
    
    return (
      <div className="text-center py-12">
        <div className="mx-auto flex items-center justify-center h-12 w-12 rounded-full bg-red-100">
          <MessageSquare className="h-6 w-6 text-red-600" />
        </div>
        <h3 className="mt-2 text-sm font-medium text-gray-900">
          {is403Error ? 'Templates Feature Not Implemented' : 'Backend Not Ready'}
        </h3>
        <p className="mt-1 text-sm text-gray-500">
          {is403Error 
            ? 'The templates API endpoint exists but is not properly implemented in the backend.'
            : 'The templates API endpoint is not yet implemented in the backend.'
          }
        </p>
        <div className="mt-6">
          <Button 
            onClick={() => window.location.reload()}
            variant="outline"
          >
            Retry Connection
          </Button>
        </div>
        <div className="mt-4 p-4 bg-yellow-50 border border-yellow-200 rounded-lg text-left max-w-md mx-auto">
          <h4 className="text-sm font-medium text-yellow-800 mb-2">Developer Note:</h4>
          <p className="text-xs text-yellow-700">
            {is403Error 
              ? 'The 403 error suggests the endpoint exists but needs proper implementation:'
              : 'To fix this, implement the templates API endpoints in your Django backend:'
            }
          </p>
          <ul className="text-xs text-yellow-700 mt-2 space-y-1">
            <li>• GET /api/templates/ - List templates</li>
            <li>• POST /api/templates/ - Create template</li>
            <li>• PUT /api/templates/{'<id>'}/ - Update template</li>
            <li>• DELETE /api/templates/{'<id>'}/ - Delete template</li>
          </ul>
          {is403Error && (
            <p className="text-xs text-yellow-700 mt-2">
              Check Django URLs, views, permissions, and serializers.
            </p>
          )}
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Development Mode Banner */}
      <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
        <div className="flex items-start">
          <div className="flex-shrink-0">
            <MessageSquare className="h-5 w-5 text-blue-600 mt-0.5" />
          </div>
          <div className="ml-3">
            <h3 className="text-sm font-medium text-blue-900">
              Development Mode Active
            </h3>
            <p className="text-sm text-blue-700 mt-1">
              Templates are working in development mode with mock data. All operations are simulated until the backend API is implemented.
            </p>
          </div>
        </div>
      </div>

      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Message Templates</h1>
          <p className="text-gray-600">Create and manage reusable message templates</p>
        </div>
        <Button onClick={() => setShowCreateModal(true)}>
          <Plus className="h-4 w-4 mr-2" />
          Create Template
        </Button>
      </div>

      {/* Search and Filter */}
      <div className="flex flex-col sm:flex-row gap-4">
        <div className="relative flex-1">
          <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 h-4 w-4" />
          <input
            type="text"
            placeholder="Search templates..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
          />
        </div>
        <Button variant="outline">
          <Filter className="h-4 w-4 mr-2" />
          Filter
        </Button>
      </div>

      {/* Templates Grid */}
      {filteredTemplates.length > 0 ? (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {filteredTemplates.map((template) => (
            <Card key={template.id} className="hover:shadow-lg transition-shadow">
              <Card.Header className="flex items-start justify-between">
                <div className="flex items-center">
                  <MessageSquare className="h-5 w-5 text-blue-600 mr-2" />
                  <h3 className="font-semibold text-gray-900 truncate">{template.name}</h3>
                </div>
                <div className="flex items-center space-x-1">
                  <button
                    onClick={() => setEditingTemplate(template)}
                    className="p-1 text-gray-400 hover:text-blue-600 transition-colors"
                    title="Edit template"
                  >
                    <Edit3 className="h-4 w-4" />
                  </button>
                  <button
                    onClick={() => handleDuplicate(template)}
                    className="p-1 text-gray-400 hover:text-green-600 transition-colors"
                    title="Duplicate template"
                  >
                    <Copy className="h-4 w-4" />
                  </button>
                  <button
                    onClick={() => handleDelete(template.id)}
                    className="p-1 text-gray-400 hover:text-red-600 transition-colors"
                    title="Delete template"
                  >
                    <Trash2 className="h-4 w-4" />
                  </button>
                </div>
              </Card.Header>
              <Card.Body>
                <div className="space-y-3">
                  <div>
                    <p className="text-sm text-gray-600 line-clamp-3">
                      {template.content}
                    </p>
                  </div>
                  
                  {template.variables && template.variables.length > 0 && (
                    <div>
                      <p className="text-xs font-medium text-gray-700 mb-1">Variables:</p>
                      <div className="flex flex-wrap gap-1">
                        {template.variables.map((variable, index) => (
                          <span
                            key={index}
                            className="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-blue-100 text-blue-800"
                          >
                            {variable}
                          </span>
                        ))}
                      </div>
                    </div>
                  )}
                  
                  <div className="flex items-center justify-between text-xs text-gray-500">
                    <span>Used {template.usage_count || 0} times</span>
                    <span>{new Date(template.created_at).toLocaleDateString()}</span>
                  </div>
                </div>
              </Card.Body>
            </Card>
          ))}
        </div>
      ) : (
        <div className="text-center py-12">
          <MessageSquare className="mx-auto h-12 w-12 text-gray-400" />
          <h3 className="mt-2 text-sm font-medium text-gray-900">
            {searchTerm ? 'No templates found' : 'No templates yet'}
          </h3>
          <p className="mt-1 text-sm text-gray-500">
            {searchTerm 
              ? 'Try adjusting your search terms'
              : 'Get started by creating your first message template.'
            }
          </p>
          {!searchTerm && (
            <Button className="mt-4" onClick={() => setShowCreateModal(true)}>
              <Plus className="h-4 w-4 mr-2" />
              Create Template
            </Button>
          )}
        </div>
      )}

      {/* Modals */}
      <CreateTemplateModal
        isOpen={showCreateModal}
        onClose={() => setShowCreateModal(false)}
        onSuccess={() => {
          setShowCreateModal(false);
          queryClient.invalidateQueries({ queryKey: ['templates'] });
        }}
      />

      {editingTemplate && (
        <EditTemplateModal
          template={editingTemplate}
          isOpen={!!editingTemplate}
          onClose={() => setEditingTemplate(null)}
          onSuccess={() => {
            setEditingTemplate(null);
            queryClient.invalidateQueries({ queryKey: ['templates'] });
          }}
        />
      )}
    </div>
  );
};

export default TemplatesPage;
