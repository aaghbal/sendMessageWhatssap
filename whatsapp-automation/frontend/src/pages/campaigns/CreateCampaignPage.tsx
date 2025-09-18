import React, { useState, useEffect } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { z } from 'zod';
import { ArrowLeft, Send, Users, MessageSquare } from 'lucide-react';
import Button from '../../components/ui/Button';
import Card from '../../components/ui/Card';
import Input from '../../components/ui/Input';

const createCampaignSchema = z.object({
  name: z.string().min(1, 'Campaign name is required'),
  description: z.string().optional(),
  message_template: z.string().min(1, 'Please select a message template'),
  target_contacts: z.array(z.string()).optional(),
  schedule_type: z.string(),
  scheduled_at: z.string().optional(),
});

type CreateCampaignFormData = z.infer<typeof createCampaignSchema>;

const CreateCampaignPage: React.FC = () => {
  const [loading, setLoading] = useState(false);
  const [currentStep, setCurrentStep] = useState(1);
  const [selectedContacts, setSelectedContacts] = useState<any[]>([]);
  const navigate = useNavigate();
  const location = useLocation();

  const {
    register,
    handleSubmit,
    watch,
    formState: { errors },
  } = useForm<CreateCampaignFormData>({
    resolver: zodResolver(createCampaignSchema),
    defaultValues: {
      schedule_type: 'now',
      target_contacts: [],
    },
  });

  const scheduleType = watch('schedule_type');

  // Handle pre-selected contacts from contact creation
  useEffect(() => {
    const state = location.state as any;
    if (state?.preSelectedContacts && state?.fromContactCreation) {
      setSelectedContacts(state.preSelectedContacts);
      // Start directly on step 2 (contact selection) if coming from contact creation
      setCurrentStep(2);
    }
  }, [location.state]);

  const onSubmit = async (data: CreateCampaignFormData) => {
    setLoading(true);
    try {
      // TODO: Implement campaign creation API call
      console.log('Creating campaign:', data);
      
      // Simulate API call
      await new Promise(resolve => setTimeout(resolve, 2000));
      
      // Navigate back to campaigns page on success
      navigate('/campaigns');
    } catch (error) {
      console.error('Failed to create campaign:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleBack = () => {
    navigate('/campaigns');
  };

  const handleNextStep = () => {
    // Don't allow proceeding to step 3 without contacts
    if (currentStep === 2 && selectedContacts.length === 0) {
      alert('Please select at least one contact before proceeding.');
      return;
    }
    setCurrentStep(prev => Math.min(prev + 1, 3));
  };

  const handlePrevStep = () => {
    setCurrentStep(prev => Math.max(prev - 1, 1));
  };

  const steps = [
    { number: 1, title: 'Campaign Details', icon: MessageSquare },
    { number: 2, title: 'Select Contacts', icon: Users },
    { number: 3, title: 'Review & Send', icon: Send },
  ];

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center space-x-4">
        <Button variant="outline" onClick={handleBack}>
          <ArrowLeft className="h-4 w-4 mr-2" />
          Back to Campaigns
        </Button>
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Create Campaign</h1>
          <p className="text-gray-600">Set up your WhatsApp campaign</p>
        </div>
      </div>

      {/* Progress Steps */}
      <Card>
        <Card.Body>
          <div className="flex items-center justify-between">
            {steps.map((step, index) => {
              const Icon = step.icon;
              const isActive = currentStep === step.number;
              const isCompleted = currentStep > step.number;
              
              return (
                <div key={step.number} className="flex items-center">
                  <div className={`flex items-center justify-center w-10 h-10 rounded-full border-2 ${
                    isActive 
                      ? 'border-primary-600 bg-primary-600' 
                      : isCompleted 
                      ? 'border-green-600 bg-green-600' 
                      : 'border-gray-300'
                  }`}>
                    <Icon className={`h-5 w-5 ${
                      isActive || isCompleted ? 'text-white' : 'text-gray-400'
                    }`} />
                  </div>
                  <div className="ml-3">
                    <p className={`text-sm font-medium ${
                      isActive ? 'text-primary-600' : isCompleted ? 'text-green-600' : 'text-gray-500'
                    }`}>
                      Step {step.number}
                    </p>
                    <p className={`text-sm ${
                      isActive ? 'text-gray-900' : 'text-gray-500'
                    }`}>
                      {step.title}
                    </p>
                  </div>
                  {index < steps.length - 1 && (
                    <div className={`flex-1 h-0.5 mx-4 ${
                      isCompleted ? 'bg-green-600' : 'bg-gray-300'
                    }`} />
                  )}
                </div>
              );
            })}
          </div>
        </Card.Body>
      </Card>

      {/* Form */}
      <form onSubmit={handleSubmit(onSubmit)}>
        {currentStep === 1 && (
          <Card>
            <Card.Header>
              <h3 className="text-lg font-medium text-gray-900">Campaign Details</h3>
            </Card.Header>
            <Card.Body className="space-y-6">
              <Input
                {...register('name')}
                label="Campaign Name"
                placeholder="Enter campaign name"
                error={errors.name?.message}
              />

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Description (Optional)
                </label>
                <textarea
                  {...register('description')}
                  rows={3}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-primary-500 focus:border-primary-500"
                  placeholder="Describe your campaign"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Message Template
                </label>
                <select
                  {...register('message_template')}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-primary-500 focus:border-primary-500"
                >
                  <option value="">Select a template</option>
                  <option value="welcome">Welcome Message</option>
                  <option value="promotion">Promotional Message</option>
                  <option value="reminder">Reminder Message</option>
                </select>
                {errors.message_template && (
                  <p className="mt-1 text-sm text-red-600">{errors.message_template.message}</p>
                )}
              </div>

              <div className="flex items-center space-x-4">
                <div className="flex items-center">
                  <input
                    {...register('schedule_type')}
                    id="send_now"
                    type="radio"
                    value="now"
                    className="h-4 w-4 text-primary-600 focus:ring-primary-500 border-gray-300"
                  />
                  <label htmlFor="send_now" className="ml-2 text-sm text-gray-700">
                    Send Now
                  </label>
                </div>
                <div className="flex items-center">
                  <input
                    {...register('schedule_type')}
                    id="schedule_later"
                    type="radio"
                    value="later"
                    className="h-4 w-4 text-primary-600 focus:ring-primary-500 border-gray-300"
                  />
                  <label htmlFor="schedule_later" className="ml-2 text-sm text-gray-700">
                    Schedule for Later
                  </label>
                </div>
              </div>

              {scheduleType === 'later' && (
                <Input
                  {...register('scheduled_at')}
                  type="datetime-local"
                  label="Schedule Date & Time"
                  error={errors.scheduled_at?.message}
                />
              )}
            </Card.Body>
          </Card>
        )}

        {currentStep === 2 && (
          <Card>
            <Card.Header>
              <h3 className="text-lg font-medium text-gray-900">Select Contacts</h3>
            </Card.Header>
            <Card.Body>
              {selectedContacts.length > 0 ? (
                <div className="space-y-4">
                  <div className="flex items-center justify-between">
                    <p className="text-sm text-gray-600">
                      {selectedContacts.length} contact(s) selected for this campaign
                    </p>
                    <Button 
                      type="button" 
                      variant="outline" 
                      size="sm"
                      onClick={() => navigate('/contacts')}
                    >
                      Add More Contacts
                    </Button>
                  </div>
                  
                  <div className="border rounded-lg divide-y">
                    {selectedContacts.map((contact, index) => (
                      <div key={index} className="p-4 flex items-center justify-between">
                        <div className="flex items-center space-x-3">
                          <div className="h-8 w-8 bg-primary-100 rounded-full flex items-center justify-center">
                            <Users className="h-4 w-4 text-primary-600" />
                          </div>
                          <div>
                            <p className="text-sm font-medium text-gray-900">{contact.name}</p>
                            <p className="text-sm text-gray-500">{contact.phone}</p>
                            {contact.email && (
                              <p className="text-xs text-gray-400">{contact.email}</p>
                            )}
                          </div>
                        </div>
                        <Button
                          type="button"
                          variant="outline"
                          size="sm"
                          onClick={() => {
                            setSelectedContacts(selectedContacts.filter((_, i) => i !== index));
                          }}
                        >
                          Remove
                        </Button>
                      </div>
                    ))}
                  </div>
                </div>
              ) : (
                <div className="text-center py-8">
                  <Users className="mx-auto h-12 w-12 text-gray-400" />
                  <h3 className="mt-2 text-sm font-medium text-gray-900">No contacts selected</h3>
                  <p className="mt-1 text-sm text-gray-500">
                    You need to select contacts for this campaign.
                  </p>
                  <Button 
                    type="button" 
                    variant="outline" 
                    className="mt-4"
                    onClick={() => navigate('/contacts')}
                  >
                    Select Contacts
                  </Button>
                </div>
              )}
            </Card.Body>
          </Card>
        )}

        {currentStep === 3 && (
          <Card>
            <Card.Header>
              <h3 className="text-lg font-medium text-gray-900">Review & Send</h3>
            </Card.Header>
            <Card.Body>
              <div className="space-y-4">
                <div>
                  <h4 className="font-medium text-gray-900">Campaign Summary</h4>
                  <p className="text-sm text-gray-600">
                    Review your campaign details before sending.
                  </p>
                </div>
                
                <div className="bg-gray-50 p-4 rounded-lg space-y-2">
                  <div className="flex justify-between">
                    <span className="text-sm font-medium text-gray-700">Name:</span>
                    <span className="text-sm text-gray-900">{watch('name') || 'Not specified'}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-sm font-medium text-gray-700">Template:</span>
                    <span className="text-sm text-gray-900">{watch('message_template') || 'Not selected'}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-sm font-medium text-gray-700">Recipients:</span>
                    <span className="text-sm text-gray-900">{selectedContacts.length} contact{selectedContacts.length !== 1 ? 's' : ''}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-sm font-medium text-gray-700">Schedule:</span>
                    <span className="text-sm text-gray-900">
                      {scheduleType === 'now' ? 'Send immediately' : 'Scheduled'}
                    </span>
                  </div>
                </div>
              </div>
            </Card.Body>
          </Card>
        )}

        {/* Navigation Buttons */}
        <div className="flex items-center justify-between">
          <div>
            {currentStep > 1 && (
              <Button type="button" variant="outline" onClick={handlePrevStep}>
                Previous
              </Button>
            )}
          </div>
          
          <div className="flex items-center space-x-4">
            {currentStep < 3 ? (
              <Button type="button" onClick={handleNextStep}>
                Next Step
              </Button>
            ) : (
              <Button type="submit" loading={loading}>
                <Send className="h-4 w-4 mr-2" />
                Create Campaign
              </Button>
            )}
          </div>
        </div>
      </form>
    </div>
  );
};

export default CreateCampaignPage;
