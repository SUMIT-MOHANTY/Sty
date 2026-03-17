import { useState, useEffect } from 'react';
import { adminService } from '../services/adminService';
import { ISystemSettings } from '../types';

export const useSystemSettings = () => {
  const [settings, setSettings] = useState<ISystemSettings | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [saving, setSaving] = useState(false);

  useEffect(() => {
    const fetchSettings = async () => {
      try {
        setLoading(true);
        setError(null);
        const data = await adminService.getSystemSettings();
        setSettings(data);
      } catch (err) {
        setError('Failed to fetch system settings');
        console.error(err);
      } finally {
        setLoading(false);
      }
    };

    fetchSettings();
  }, []);

  const updateSettings = async (updatedSettings: ISystemSettings) => {
    try {
      setSaving(true);
      setError(null);
      const data = await adminService.updateSystemSettings(updatedSettings);
      setSettings(data);
      return data;
    } catch (err) {
      setError('Failed to update system settings');
      console.error(err);
      throw err;
    } finally {
      setSaving(false);
    }
  };

  return {
    settings,
    loading,
    error,
    saving,
    updateSettings
  };
};
