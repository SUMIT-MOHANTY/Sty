import React, { useState, useEffect } from 'react';
import { toast } from 'react-toastify';
import SlotCalendar from '../../components/admin/SlotCalendar';
import AppointmentList from '../../components/admin/AppointmentList';
import SlotForm from '../../components/admin/SlotForm';
import { fetchSlots, createSlot, updateSlot, deleteSlot,
         fetchAppointments } from '../../services/appointmentService';

const AppointmentManagement = () => {
  const [slots, setSlots] = useState([]);
  const [appointments, setAppointments] = useState([]);
  const [isLoading, setIsLoading] = useState(false);
  const [selectedDate, setSelectedDate] = useState(new Date());
  const [editSlot, setEditSlot] = useState(null);
  const [showSlotForm, setShowSlotForm] = useState(false);

  useEffect(() => {
    loadData();
  }, [selectedDate]);

  const loadData = async () => {
    setIsLoading(true);
    try {
      // Format date as YYYY-MM-DD
      const dateStr = selectedDate.toISOString().split('T')[0];

      // Fetch slots and appointments for selected date
      const slotsData = await fetchSlots();
      const appointmentsData = await fetchAppointments({ date: dateStr });

      setSlots(slotsData);
      setAppointments(appointmentsData);
    } catch (error) {
      toast.error('Failed to load data');
      console.error(error);
    } finally {
      setIsLoading(false);
    }
  };

  const handleCreateSlot = async (slotData) => {
    try {
      await createSlot(slotData);
      toast.success('Slot created successfully');
      setShowSlotForm(false);
      loadData();
    } catch (error) {
      toast.error('Failed to create slot');
      console.error(error);
    }
  };

  const handleUpdateSlot = async (slotData) => {
    try {
      await updateSlot(editSlot.id, slotData);
      toast.success('Slot updated successfully');
      setEditSlot(null);
      setShowSlotForm(false);
      loadData();
    } catch (error) {
      toast.error('Failed to update slot');
      console.error(error);
    }
  };

  const handleDeleteSlot = async (slotId) => {
    try {
      await deleteSlot(slotId);
      toast.success('Slot deleted successfully');
      loadData();
    } catch (error) {
      toast.error(error.response?.data?.error || 'Failed to delete slot');
      console.error(error);
    }
  };

  const handleEditSlot = (slot) => {
    setEditSlot(slot);
    setShowSlotForm(true);
  };

  return (
    <div className="container mx-auto p-4">
      <h1 className="text-2xl font-bold mb-6">Appointment Management</h1>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <div className="md:col-span-1">
          <div className="bg-white rounded-lg shadow p-4">
            <h2 className="text-xl font-semibold mb-4">Appointment Slots</h2>
            <button
              onClick={() => { setEditSlot(null); setShowSlotForm(true); }}
              className="w-full bg-blue-500 hover:bg-blue-600 text-white py-2 px-4 rounded mb-4"
            >
              Create New Slot
            </button>

            <SlotCalendar
              slots={slots}
              selectedDate={selectedDate}
              onDateChange={setSelectedDate}
            />
          </div>
        </div>

        <div className="md:col-span-2">
          {showSlotForm ? (
            <div className="bg-white rounded-lg shadow p-4 mb-6">
              <SlotForm
                slot={editSlot}
                onSubmit={editSlot ? handleUpdateSlot : handleCreateSlot}
                onCancel={() => setShowSlotForm(false)}
              />
            </div>
          ) : null}

          <div className="bg-white rounded-lg shadow p-4">
            <h2 className="text-xl font-semibold mb-4">Appointments</h2>
            <AppointmentList
              appointments={appointments}
              slots={slots}
              onEditSlot={handleEditSlot}
              onDeleteSlot={handleDeleteSlot}
              isLoading={isLoading}
              selectedDate={selectedDate}
            />
          </div>
        </div>
      </div>
    </div>
  );
};

export default AppointmentManagement;
