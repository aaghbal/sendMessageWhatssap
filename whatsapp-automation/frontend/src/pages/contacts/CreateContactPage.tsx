import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { z } from 'zod';
import { ArrowLeft, User, Phone, Mail, Save, MessageSquare } from 'lucide-react';
import Button from '../../components/ui/Button';
import Card from '../../components/ui/Card';
import Input from '../../components/ui/Input';

const contactSchema = z.object({
  first_name: z.string().min(1, 'First name is required'),
  last_name: z.string().min(1, 'Last name is required'),
  phone_number: z.string().min(1, 'Phone number is required'),
  country_code: z.string().min(1, 'Country code is required'),
  email: z.string().optional(),
  notes: z.string().optional(),
});

type CreateContactFormData = z.infer<typeof contactSchema>;

const CreateContactPage: React.FC = () => {
  const [loading, setLoading] = useState(false);
  const [sendMessage, setSendMessage] = useState(false);
  const navigate = useNavigate();

  const {
    register,
    handleSubmit,
    watch,
    formState: { errors },
  } = useForm<CreateContactFormData>({
    resolver: zodResolver(contactSchema),
    defaultValues: {
      country_code: '+1',
    },
  });

  const onSubmit = async (data: CreateContactFormData) => {
    setLoading(true);
    try {
      // TODO: Implement contact creation API call
      console.log('Creating contact:', data);
      
      // Simulate API call
      await new Promise(resolve => setTimeout(resolve, 1000));
      
      // Create contact object for potential message sending
      const newContact = {
        id: Date.now(), // Temporary ID until real API implementation
        name: `${data.first_name} ${data.last_name}`,
        phone: `${data.country_code}${data.phone_number}`,
        email: data.email || '',
        ...data
      };
      
      if (sendMessage) {
        // Navigate to campaign creation with pre-selected contact
        navigate('/campaigns/create', { 
          state: { 
            preSelectedContacts: [newContact],
            fromContactCreation: true 
          } 
        });
      } else {
        // Navigate back to contacts page
        navigate('/contacts');
      }
    } catch (error) {
      console.error('Failed to create contact:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleBack = () => {
    navigate('/contacts');
  };

  const countryCodes = [
    { value: '+1', label: '+1 (US/Canada)' },
    { value: '+20', label: '+20 (Egypt)' },
    { value: '+212', label: '+212 (Morocco)' },
    { value: '+44', label: '+44 (UK)' },
    { value: '+49', label: '+49 (Germany)' },
    { value: '+33', label: '+33 (France)' },
    { value: '+91', label: '+91 (India)' },
    { value: '+86', label: '+86 (China)' },
    { value: '+81', label: '+81 (Japan)' },
    { value: '+61', label: '+61 (Australia)' },
    { value: '+971', label: '+971 (UAE)' },
  ];

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center space-x-4">
        <Button variant="outline" onClick={handleBack}>
          <ArrowLeft className="h-4 w-4 mr-2" />
          Back to Contacts
        </Button>
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Add New Contact</h1>
          <p className="text-gray-600">Add a new contact to your WhatsApp list</p>
        </div>
      </div>

      {/* Form */}
      <Card>
        <Card.Header>
          <div className="flex items-center">
            <User className="h-5 w-5 text-primary-600 mr-2" />
            <h3 className="text-lg font-medium text-gray-900">Contact Information</h3>
          </div>
        </Card.Header>
        <Card.Body>
          <form onSubmit={handleSubmit(onSubmit)} className="space-y-6">
            {/* First Name */}
            <Input
              {...register('first_name')}
              label="First Name"
              placeholder="Enter first name"
              error={errors.first_name?.message}
              required
            />

            {/* Last Name */}
            <Input
              {...register('last_name')}
              label="Last Name"
              placeholder="Enter last name"
              error={errors.last_name?.message}
              required
            />

            {/* Phone Number */}
            <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Country Code <span className="text-red-500">*</span>
                </label>
                <select
                  {...register('country_code')}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-primary-500 focus:border-primary-500"
                >
                  {countryCodes.map((country) => (
                    <option key={country.value} value={country.value}>
                      {country.label}
                    </option>
                  ))}
                </select>
                {errors.country_code && (
                  <p className="mt-1 text-sm text-red-600">{errors.country_code.message}</p>
                )}
              </div>

              <div className="md:col-span-3">
                <Input
                  {...register('phone_number')}
                  label="Phone Number"
                  placeholder="1234567890"
                  error={errors.phone_number?.message}
                  required
                />
              </div>
            </div>

            {/* Email */}
            <Input
              {...register('email')}
              label="Email Address (Optional)"
              placeholder="contact@example.com"
              error={errors.email?.message as string}
            />            {/* Notes */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Notes (Optional)
              </label>
              <textarea
                {...register('notes')}
                rows={4}
                className="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-primary-500 focus:border-primary-500"
                placeholder="Add any additional notes about this contact..."
              />
            </div>

            {/* Send Message Option */}
            <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
              <div className="flex items-center mb-2">
                <input
                  id="send-message"
                  type="checkbox"
                  checked={sendMessage}
                  onChange={(e) => setSendMessage(e.target.checked)}
                  className="h-4 w-4 text-primary-600 focus:ring-primary-500 border-gray-300 rounded"
                />
                <label htmlFor="send-message" className="ml-2 block text-sm font-medium text-gray-900">
                  Send WhatsApp message to this contact immediately after adding
                </label>
              </div>
              {sendMessage && (
                <div className="mt-3 p-3 bg-white rounded border border-blue-100">
                  <div className="flex items-center text-sm text-blue-700">
                    <MessageSquare className="h-4 w-4 mr-2" />
                    <span>After saving, you'll be redirected to create a campaign for this contact</span>
                  </div>
                  <div className="mt-2 text-xs text-blue-600">
                    Phone: {watch('country_code') || '+1'}{watch('phone_number') || 'Enter phone number'}
                  </div>
                </div>
              )}
            </div>

            {/* Submit Buttons */}
            <div className="flex items-center justify-between">
              <Button 
                type="button" 
                variant="outline" 
                onClick={() => navigate('/contacts')}
                className="text-blue-600 border-blue-300 hover:bg-blue-50"
              >
                <MessageSquare className="h-4 w-4 mr-2" />
                Send Message to Existing Contact
              </Button>
              
              <div className="flex items-center space-x-4">
                <Button type="button" variant="outline" onClick={handleBack}>
                  Cancel
                </Button>
                <Button type="submit" loading={loading}>
                  <Save className="h-4 w-4 mr-2" />
                  {sendMessage ? 'Save & Send Message' : 'Save Contact'}
                </Button>
              </div>
            </div>
          </form>
        </Card.Body>
      </Card>

      {/* Help Card */}
      <Card>
        <Card.Header>
          <h3 className="text-lg font-medium text-gray-900">Tips</h3>
        </Card.Header>
        <Card.Body>
          <div className="space-y-3">
            <div className="flex items-start">
              <Phone className="h-5 w-5 text-primary-600 mr-3 mt-0.5" />
              <div>
                <p className="text-sm font-medium text-gray-900">Phone Number Format</p>
                <p className="text-sm text-gray-600">
                  Enter the phone number without the country code. The country code will be added automatically.
                </p>
              </div>
            </div>
            
            <div className="flex items-start">
              <Mail className="h-5 w-5 text-primary-600 mr-3 mt-0.5" />
              <div>
                <p className="text-sm font-medium text-gray-900">Email Address</p>
                <p className="text-sm text-gray-600">
                  Email is optional but helps you organize and identify your contacts better.
                </p>
              </div>
            </div>

            <div className="flex items-start">
              <User className="h-5 w-5 text-primary-600 mr-3 mt-0.5" />
              <div>
                <p className="text-sm font-medium text-gray-900">Contact Verification</p>
                <p className="text-sm text-gray-600">
                  Make sure the WhatsApp number is active before adding it to your contact list.
                </p>
              </div>
            </div>

            <div className="flex items-start">
              <MessageSquare className="h-5 w-5 text-primary-600 mr-3 mt-0.5" />
              <div>
                <p className="text-sm font-medium text-gray-900">Quick Campaign</p>
                <p className="text-sm text-gray-600">
                  Check "Send WhatsApp message" to immediately create a campaign for this contact after adding them.
                </p>
              </div>
            </div>
          </div>
        </Card.Body>
      </Card>
    </div>
  );
};

export default CreateContactPage;
