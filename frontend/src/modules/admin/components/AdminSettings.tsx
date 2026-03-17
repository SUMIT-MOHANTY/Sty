import React, { useState, useEffect } from 'react';
import { useSystemSettings } from '../hooks/useSystemSettings';
import { ISystemSettings } from '../types';

export const AdminSettings: React.FC = () => {
  const { settings, loading, error, saving, updateSettings } = useSystemSettings();
  const [formData, setFormData] = useState<ISystemSettings | null>(null);
  const [formError, setFormError] = useState<string | null>(null);

  useEffect(() => {
    if (settings) {
      setFormData(settings);
    }
  }, [settings]);

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (!formData) return;

    const { name, value, type } = e.target;

    if (type === 'checkbox') {
      setFormData({
        ...formData,
        [name]: (e.target as HTMLInputElement).checked
      });
    } else if (type === 'number') {
      setFormData({
        ...formData,
        [name]: parseFloat(value)
      });
    } else {
      setFormData({
        ...formData,
        [name]: value
      });
    }
  };

  const handleFileTypeChange = (index: number, value: string) => {
    if (!formData) return;

    const newTypes = [...formData.allowedDocumentTypes];
    newTypes[index] = value;

    setFormData({
      ...formData,
      allowedDocumentTypes: newTypes
    });
  };

  const addFileType = () => {
    if (!formData) return;

    setFormData({
      ...formData,
      allowedDocumentTypes: [...formData.allowedDocumentTypes, '']
    });
  };

  const removeFileType = (index: number) => {
    if (!formData) return;

    const newTypes = [...formData.allowedDocumentTypes];
    newTypes.splice(index, 1);

    setFormData({
      ...formData,
      allowedDocumentTypes: newTypes
    });
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!formData) return;

    setFormError(null);

    try {
      await updateSettings(formData);
    } catch (err) {
      setFormError('Failed to save settings');
    }
  };

  if (loading && !formData) {
    return <div className="loading">Loading system settings...</div>;
  }

  if (error) {
    return <div className="error">{error}</div>;
  }

  if (!formData) {
    return <div className="error">No settings data available</div>;
  }

  return (
    <div className="admin-settings">
      <h2>System Settings</h2>

      {formError && <div className="error-message">{formError}</div>}

      <form onSubmit={handleSubmit}>
        <div className="settings-group">
          <h3>General Settings</h3>

          <div className="form-row">
            <label>
              Application Fee ($):
              <input
                type="number"
                name="applicationFee"
                value={formData.applicationFee}
                onChange={handleInputChange}
                min="0"
                step="0.01"
                required
              />
            </label>
          </div>

          <div className="form-row">
            <label>
              Appointment Slots Per Day:
              <input
                type="number"
                name="appointmentSlotsPerDay"
                value={formData.appointmentSlotsPerDay}
                onChange={handleInputChange}
                min="1"
                max="100"
                required
              />
            </label>
          </div>

          <div className="form-row">
            <label>
              <input
                type="checkbox"
                name="maintenanceMode"
                checked={formData.maintenanceMode}
                onChange={handleInputChange}
              />
              System Maintenance Mode
            </label>
          </div>
        </div>

        <div className="settings-group">
          <h3>Notification Settings</h3>

          <div className="form-row">
            <label>
              Notification Email Address:
              <input
                type="email"
                name="notificationEmail"
                value={formData.notificationEmail}
                onChange={handleInputChange}
                required
              />
            </label>
          </div>
        </div>

        <div className="settings-group">
          <h3>Document Settings</h3>

          <div className="form-row">
            <label>
              Document Retention Period (days):
              <input
                type="number"
                name="documentRetentionDays"
                value={formData.documentRetentionDays}
                onChange={handleInputChange}
                min="1"
                required
              />
            </label>
          </div>

          <div className="form-row">
            <label>Allowed Document Types:</label>
            <div className="file-types-container">
              {formData.allowedDocumentTypes.map((type, index) => (
                <div key={index} className="file-type-input">
                  <input
                    type="text"
                    value={type}
                    onChange={(e) => handleFileTypeChange(index, e.target.value)}
                    placeholder="File extension"
                    required
                  />
                  <button
                    type="button"
                    className="remove-btn"
                    onClick={() => removeFileType(index)}
                  >
                    Remove
                  </button>
                </div>
              ))}
              <button
                type="button"
                className="add-btn"
                onClick={addFileType}
              >
                Add File Type
              </button>
            </div>
          </div>
        </div>

        <div className="form-actions">
          <button
            type="submit"
            className="save-settings-btn"
            disabled={saving}
          >
            {saving ? 'Saving...' : 'Save Settings'}
          </button>
        </div>
      </form>
    </div>
  );
};
