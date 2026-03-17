import React, { useState, useEffect } from 'react';
import { useApi } from '../../hooks/useApi';
import { Card } from '../Card';
import { Button } from '../Button';

interface ReminderPreferences {
  email_reminders: boolean;
  sms_reminders: boolean;
  reminder_days_before: number;
  phone_number?: string;
}

interface AppointmentRemindersProps {
  appointmentId: string;
  onClose: () => void;
}

const AppointmentReminders: React.FC<AppointmentRemindersProps> = ({
  appointmentId,
  onClose
}) => {
  const [preferences, setPreferences] = useState<ReminderPreferences>({
    email_reminders: true,
    sms_reminders: false,
    reminder_days_before: 3,
    phone_number: ''
  });

  const [isLoading, setIsLoading] = useState<boolean>(true);
  const [isSaving, setIsSaving] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);
  const [successMessage, setSuccessMessage] = useState<string | null>(null);

  const { get, post } = useApi();

  useEffect(() => {
    const fetchReminderPreferences = async () => {
      setIsLoading(true);
      try {
        const response = await get(`/api/appointments/${appointmentId}/reminders`);
        setPreferences(response);
        setError(null);
      } catch (err) {
        setError('Failed to load reminder preferences. Using defaults.');
        console.error('Error fetching reminder preferences:', err);
      } finally {
        setIsLoading(false);
      }
    };

    fetchReminderPreferences();
  }, [appointmentId, get]);

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement>) => {
    const { name, value, type } = e.target as HTMLInputElement;

    setPreferences(prev => ({
      ...prev,
      [name]: type === 'checkbox' ? (e.target as HTMLInputElement).checked : value
    }));

    setError(null);
    setSuccessMessage(null);
  };

  const handleSave = async () => {
    // Validate phone number if SMS reminders are enabled
    if (preferences.sms_reminders && (!preferences.phone_number || preferences.phone_number.trim() === '')) {
      setError('Please enter a phone number for SMS reminders.');
      return;
    }

    setIsSaving(true);
    try {
      await post(`/api/appointments/${appointmentId}/reminders`, preferences);
      setSuccessMessage('Reminder preferences saved successfully!');
      setError(null);
    } catch (err) {
      setError('Failed to save reminder preferences. Please try again.');
      console.error('Error saving reminder preferences:', err);
      setSuccessMessage(null);
    } finally {
      setIsSaving(false);
    }
  };

  return (
    <Card className="appointment-reminders p-6">
      <h2 className="text-2xl font-bold mb-4">Appointment Reminders</h2>

      {isLoading ? (
        <div className="text-center py-4">Loading preferences...</div>
      ) : (
        <div className="reminder-form space-y-6">
          <div className="reminder-option">
            <label className="flex items-center cursor-pointer">
              <input
                type="checkbox"
                name="email_reminders"
                checked={preferences.email_reminders}
                onChange={handleInputChange}
                className="mr-2 h-5 w-5"
              />
              <span>Send email reminders</span>
            </label>
          </div>

          <div className="reminder-option">
            <label className="flex items-center cursor-pointer">
              <input
                type="checkbox"
                name="sms_reminders"
                checked={preferences.sms_reminders}
                onChange={handleInputChange}
                className="mr-2 h-5 w-5"
              />
              <span>Send SMS reminders</span>
            </label>

            {preferences.sms_reminders && (
              <div className="mt-3 ml-7">
                <label htmlFor="phone_number" className="block text-sm text-gray-700 mb-1">
                  Phone Number for SMS
                </label>
                <input
                  type="tel"
                  id="phone_number"
                  name="phone_number"
                  value={preferences.phone_number || ''}
                  onChange={handleInputChange}
                  placeholder="Enter your phone number"
                  className="border rounded px-3 py-2 w-full"
                />
              </div>
            )}
          </div>

          <div className="reminder-timing">
            <label htmlFor="reminder_days_before" className="block text-sm text-gray-700 mb-1">
              Send reminders before appointment
            </label>
            <select
              id="reminder_days_before"
              name="reminder_days_before"
              value={preferences.reminder_days_before}
              onChange={handleInputChange}
              className="border rounded px-3 py-2 w-full"
            >
              <option value={1}>1 day before</option>
              <option value={2}>2 days before</option>
              <option value={3}>3 days before</option>
              <option value={5}>5 days before</option>
              <option value={7}>1 week before</option>
            </select>
          </div>

          {error && (
            <div className="error-message text-red-600 bg-red-100 p-3 rounded">
              {error}
            </div>
          )}

          {successMessage && (
            <div className="success-message text-green-600 bg-green-100 p-3 rounded">
              {successMessage}
            </div>
          )}
        </div>
      )}

      <div className="flex flex-col md:flex-row gap-3 mt-6">
        <Button
          variant="secondary"
          onClick={onClose}
          className="flex-1"
        >
          Close
        </Button>

        <Button
          variant="primary"
          onClick={handleSave}
          disabled={isSaving || isLoading}
          className="flex-1"
        >
          {isSaving ? 'Saving...' : 'Save Preferences'}
        </Button>
      </div>
    </Card>
  );
};

export default AppointmentReminders;
