import React, { useState } from 'react';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { z } from 'zod';
import { Upload, Download, Plus, Trash2, Send, MessageSquare, Phone } from 'lucide-react';
import Button from '../../components/ui/Button';
import Card from '../../components/ui/Card';

const sendMessageSchema = z.object({
  message: z.string().min(1, 'Message is required'),
  phone_number: z.string().optional(),
});

type SendMessageFormData = z.infer<typeof sendMessageSchema>;

interface PhoneNumber {
  id: string;
  number: string;
  country_code: string;
  name?: string;
}

const SendMessagePage: React.FC = () => {
  const [currentStep, setCurrentStep] = useState(1);
  const [phoneNumbers, setPhoneNumbers] = useState<PhoneNumber[]>([]);
  const [loading, setLoading] = useState(false);
  const [newPhoneNumber, setNewPhoneNumber] = useState('');
  const [selectedCountryCode, setSelectedCountryCode] = useState('+1');

  const {
    register,
    handleSubmit,
    watch,
    formState: { errors },
  } = useForm<SendMessageFormData>({
    resolver: zodResolver(sendMessageSchema),
  });

  const message = watch('message');

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

  const addPhoneNumber = () => {
    if (newPhoneNumber.trim()) {
      const newPhone: PhoneNumber = {
        id: Date.now().toString(),
        number: newPhoneNumber.trim(),
        country_code: selectedCountryCode,
      };
      setPhoneNumbers([...phoneNumbers, newPhone]);
      setNewPhoneNumber('');
    }
  };

  const removePhoneNumber = (id: string) => {
    setPhoneNumbers(phoneNumbers.filter(phone => phone.id !== id));
  };

  const handleFileImport = (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (file) {
      const reader = new FileReader();
      reader.onload = (e) => {
        const text = e.target?.result as string;
        const lines = text.split('\n').filter(line => line.trim());
        
        const importedNumbers: PhoneNumber[] = lines.map((line, index) => {
          const parts = line.split(',');
          const number = parts[0]?.trim();
          const name = parts[1]?.trim();
          
          if (number) {
            return {
              id: `imported-${Date.now()}-${index}`,
              number: number.replace(/[^\d+]/g, ''),
              country_code: number.startsWith('+') ? number.substring(0, number.length - number.replace(/[^\d]/g, '').length) : '+1',
              name: name || undefined,
            };
          }
          return null;
        }).filter(Boolean) as PhoneNumber[];

        setPhoneNumbers([...phoneNumbers, ...importedNumbers]);
      };
      reader.readAsText(file);
    }
  };

  const downloadTemplate = () => {
    const template = `+1234567890,John Doe
+1987654321,Jane Smith
+44123456789,Mike Johnson`;
    
    const blob = new Blob([template], { type: 'text/plain' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = 'phone_numbers_template.csv';
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
  };

  const onSubmit = async (data: SendMessageFormData) => {
    if (phoneNumbers.length === 0) {
      alert('Please add at least one phone number before sending.');
      return;
    }

    setLoading(true);
    try {
      // Import the API service
      const { apiService } = await import('../../services/api');
      
      // Prepare recipients array
      const recipients = phoneNumbers.map(p => p.country_code + p.number);
      
      console.log('Sending WhatsApp messages to:', recipients);
      
      // Call the real backend API
      const result = await apiService.sendBulkMessages({
        recipients: recipients,
        message: data.message
      });
      
      console.log('WhatsApp API Response:', result);
      
      if (result.success) {
        alert(`Message sent successfully!\n\n✅ Successful: ${result.successful_sends}\n❌ Failed: ${result.failed_sends}\n📱 Total: ${result.total_recipients}`);
        
        // Reset form
        setPhoneNumbers([]);
        setCurrentStep(1);
      } else {
        alert('Some messages failed to send. Please check the console for details.');
      }
    } catch (error: any) {
      console.error('Failed to send messages:', error);
      
      // More detailed error message
      let errorMessage = 'Failed to send messages. ';
      if (error.response?.data?.error) {
        errorMessage += error.response.data.error;
      } else if (error.message) {
        errorMessage += error.message;
      } else {
        errorMessage += 'Please check your internet connection and try again.';
      }
      
      alert(errorMessage);
    } finally {
      setLoading(false);
    }
  };

  const steps = [
    { number: 1, title: 'Add Phone Numbers', icon: Phone },
    { number: 2, title: 'Compose Message', icon: MessageSquare },
    { number: 3, title: 'Review & Send', icon: Send },
  ];

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-2xl font-bold text-gray-900">Send WhatsApp Messages</h1>
        <p className="text-gray-600">Send messages to multiple WhatsApp numbers at once</p>
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

      {/* Step 1: Add Phone Numbers */}
      {currentStep === 1 && (
        <div className="space-y-6">
          {/* Manual Input Section */}
          <Card>
            <Card.Header>
              <h3 className="text-lg font-medium text-gray-900">Add Phone Numbers Manually</h3>
            </Card.Header>
            <Card.Body>
              <div className="flex items-end space-x-4">
                <div className="flex-1">
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Country Code
                  </label>
                  <select
                    value={selectedCountryCode}
                    onChange={(e) => setSelectedCountryCode(e.target.value)}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-primary-500 focus:border-primary-500"
                  >
                    {countryCodes.map((country) => (
                      <option key={country.value} value={country.value}>
                        {country.label}
                      </option>
                    ))}
                  </select>
                </div>
                <div className="flex-2">
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Phone Number
                  </label>
                  <input
                    type="text"
                    value={newPhoneNumber}
                    onChange={(e) => setNewPhoneNumber(e.target.value)}
                    placeholder="1234567890"
                    className="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-primary-500 focus:border-primary-500"
                    onKeyPress={(e) => e.key === 'Enter' && addPhoneNumber()}
                  />
                </div>
                <Button onClick={addPhoneNumber} disabled={!newPhoneNumber.trim()}>
                  <Plus className="h-4 w-4 mr-2" />
                  Add
                </Button>
              </div>
            </Card.Body>
          </Card>

          {/* File Import Section */}
          <Card>
            <Card.Header>
              <div className="flex items-center justify-between">
                <h3 className="text-lg font-medium text-gray-900">Import from File</h3>
                <Button variant="outline" size="sm" onClick={downloadTemplate}>
                  <Download className="h-4 w-4 mr-2" />
                  Download Template
                </Button>
              </div>
            </Card.Header>
            <Card.Body>
              <div className="border-2 border-dashed border-gray-300 rounded-lg p-6">
                <div className="text-center">
                  <Upload className="mx-auto h-12 w-12 text-gray-400" />
                  <div className="mt-4">
                    <label htmlFor="file-upload" className="cursor-pointer">
                      <span className="mt-2 block text-sm font-medium text-gray-900">
                        Upload a CSV file with phone numbers
                      </span>
                      <span className="mt-1 block text-sm text-gray-500">
                        Format: +1234567890,Name (one per line)
                      </span>
                    </label>
                    <input
                      id="file-upload"
                      name="file-upload"
                      type="file"
                      accept=".csv,.txt"
                      onChange={handleFileImport}
                      className="sr-only"
                    />
                  </div>
                  <Button variant="outline" className="mt-4" onClick={() => document.getElementById('file-upload')?.click()}>
                    <Upload className="h-4 w-4 mr-2" />
                    Choose File
                  </Button>
                </div>
              </div>
            </Card.Body>
          </Card>

          {/* Phone Numbers List */}
          {phoneNumbers.length > 0 && (
            <Card>
              <Card.Header>
                <div className="flex items-center justify-between">
                  <h3 className="text-lg font-medium text-gray-900">
                    Phone Numbers ({phoneNumbers.length})
                  </h3>
                  <Button 
                    variant="outline" 
                    size="sm"
                    onClick={() => setPhoneNumbers([])}
                  >
                    Clear All
                  </Button>
                </div>
              </Card.Header>
              <Card.Body>
                <div className="max-h-64 overflow-y-auto">
                  <div className="space-y-2">
                    {phoneNumbers.map((phone) => (
                      <div key={phone.id} className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                        <div className="flex items-center space-x-3">
                          <div className="h-8 w-8 bg-primary-100 rounded-full flex items-center justify-center">
                            <Phone className="h-4 w-4 text-primary-600" />
                          </div>
                          <div>
                            <p className="text-sm font-medium text-gray-900">
                              {phone.country_code}{phone.number}
                            </p>
                            {phone.name && (
                              <p className="text-xs text-gray-500">{phone.name}</p>
                            )}
                          </div>
                        </div>
                        <Button
                          variant="outline"
                          size="sm"
                          onClick={() => removePhoneNumber(phone.id)}
                        >
                          <Trash2 className="h-4 w-4" />
                        </Button>
                      </div>
                    ))}
                  </div>
                </div>
              </Card.Body>
            </Card>
          )}

          {/* Navigation */}
          <div className="flex justify-end">
            <Button 
              onClick={() => setCurrentStep(2)}
              disabled={phoneNumbers.length === 0}
            >
              Next: Compose Message
            </Button>
          </div>
        </div>
      )}

      {/* Step 2: Compose Message */}
      {currentStep === 2 && (
        <Card>
          <Card.Header>
            <h3 className="text-lg font-medium text-gray-900">Compose Your Message</h3>
          </Card.Header>
          <Card.Body className="space-y-6">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Message Text <span className="text-red-500">*</span>
              </label>
              <textarea
                {...register('message')}
                rows={6}
                className="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-primary-500 focus:border-primary-500"
                placeholder="Type your WhatsApp message here..."
              />
              {errors.message && (
                <p className="mt-1 text-sm text-red-600">{errors.message.message}</p>
              )}
              <div className="mt-2 flex justify-between text-sm text-gray-500">
                <span>Write a clear and engaging message</span>
                <span>{message?.length || 0} characters</span>
              </div>
            </div>

            {/* Message Preview */}
            {message && (
              <div className="bg-green-50 border border-green-200 rounded-lg p-4">
                <h4 className="font-medium text-green-800 mb-2">Message Preview:</h4>
                <div className="bg-white rounded-lg p-3 shadow-sm border">
                  <p className="text-sm text-gray-900 whitespace-pre-wrap">{message}</p>
                </div>
              </div>
            )}

            {/* Navigation */}
            <div className="flex justify-between">
              <Button variant="outline" onClick={() => setCurrentStep(1)}>
                Back: Edit Numbers
              </Button>
              <Button 
                onClick={() => setCurrentStep(3)}
                disabled={!message?.trim()}
              >
                Next: Review & Send
              </Button>
            </div>
          </Card.Body>
        </Card>
      )}

      {/* Step 3: Review & Send */}
      {currentStep === 3 && (
        <form onSubmit={handleSubmit(onSubmit)}>
          <Card>
            <Card.Header>
              <h3 className="text-lg font-medium text-gray-900">Review & Send</h3>
            </Card.Header>
            <Card.Body className="space-y-6">
              {/* Summary */}
              <div className="bg-gray-50 p-4 rounded-lg space-y-3">
                <div className="flex justify-between">
                  <span className="text-sm font-medium text-gray-700">Recipients:</span>
                  <span className="text-sm text-gray-900">{phoneNumbers.length} numbers</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-sm font-medium text-gray-700">Message Length:</span>
                  <span className="text-sm text-gray-900">{message?.length || 0} characters</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-sm font-medium text-gray-700">Status:</span>
                  <span className="text-sm text-green-600">Ready to send</span>
                </div>
              </div>

              {/* Message Preview */}
              <div>
                <h4 className="font-medium text-gray-900 mb-2">Final Message:</h4>
                <div className="bg-white border rounded-lg p-4">
                  <p className="text-sm text-gray-900 whitespace-pre-wrap">{message}</p>
                </div>
              </div>

              {/* Recipients Preview */}
              <div>
                <h4 className="font-medium text-gray-900 mb-2">Recipients Preview:</h4>
                <div className="bg-white border rounded-lg p-4 max-h-32 overflow-y-auto">
                  <div className="text-sm text-gray-600">
                    {phoneNumbers.slice(0, 5).map((phone, index) => (
                      <div key={phone.id}>
                        {phone.country_code}{phone.number} {phone.name && `(${phone.name})`}
                      </div>
                    ))}
                    {phoneNumbers.length > 5 && (
                      <div className="text-gray-500 italic">
                        ... and {phoneNumbers.length - 5} more numbers
                      </div>
                    )}
                  </div>
                </div>
              </div>

              {/* Warning */}
              <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4">
                <div className="flex">
                  <MessageSquare className="h-5 w-5 text-yellow-600 mr-3 mt-0.5" />
                  <div>
                    <h4 className="text-sm font-medium text-yellow-800">Important Notice</h4>
                    <p className="text-sm text-yellow-700 mt-1">
                      Make sure all phone numbers are valid WhatsApp numbers. Invalid numbers may result in delivery failures.
                    </p>
                  </div>
                </div>
              </div>

              {/* Navigation */}
              <div className="flex justify-between">
                <Button variant="outline" onClick={() => setCurrentStep(2)}>
                  Back: Edit Message
                </Button>
                <Button type="submit" loading={loading} className="bg-green-600 hover:bg-green-700">
                  <Send className="h-4 w-4 mr-2" />
                  Send to {phoneNumbers.length} Numbers
                </Button>
              </div>
            </Card.Body>
          </Card>
        </form>
      )}
    </div>
  );
};

export default SendMessagePage;
