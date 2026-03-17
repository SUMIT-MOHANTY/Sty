import React, { useState } from 'react';
import { format } from 'date-fns';

const AppointmentList = ({
  appointments,
  slots,
  onEditSlot,
  onDeleteSlot,
  isLoading,
  selectedDate
}) => {
  const [filter, setFilter] = useState('all');
  const [expandedSlotId, setExpandedSlotId] = useState(null);

  // Filter slots for the selected date
  const dateStr = selectedDate.toISOString().split('T')[0];
  const dateSlotsArray = slots.filter(slot => slot.date === dateStr);

  // Filter appointments based on selected date
  const dateAppointments = appointments.filter(
    appointment => appointment.date === dateStr
  );

  // Group appointments by slot
  const appointmentsBySlot = dateAppointments.reduce((acc, appointment) => {
    if (!acc[appointment.slot_id]) {
      acc[appointment.slot_id] = [];
    }
    acc[appointment.slot_id].push(appointment);
    return acc;
  }, {});

  // Apply status filter if needed
  let filteredAppointments = dateAppointments;
  if (filter !== 'all') {
    filteredAppointments = dateAppointments.filter(
      appointment => appointment.status === filter
    );
  }

  const handleExpandSlot = (slotId) => {
    if (expandedSlotId === slotId) {
      setExpandedSlotId(null);
    } else {
      setExpandedSlotId(slotId);
    }
  };

  if (isLoading) {
    return <div className="text-center py-4">Loading...</div>;
  }

  if (dateSlotsArray.length === 0) {
    return (
      <div className="text-center py-4">
        No slots available for {format(selectedDate, 'MMMM d, yyyy')}
      </div>
    );
  }

  return (
    <div>
      <div className="flex justify-between items-center mb-4">
        <h3 className="text-lg font-medium">
          {format(selectedDate, 'MMMM d, yyyy')}
        </h3>
        <div className="flex items-center">
          <label htmlFor="filter" className="mr-2">Status:</label>
          <select
            id="filter"
            value={filter}
            onChange={(e) => setFilter(e.target.value)}
            className="border rounded p-1"
          >
            <option value="all">All</option>
            <option value="scheduled">Scheduled</option>
            <option value="completed">Completed</option>
            <option value="cancelled">Cancelled</option>
          </select>
        </div>
      </div>

      {dateSlotsArray.length > 0 ? (
        <div className="space-y-4">
          {dateSlotsArray.map(slot => (
            <div key={slot.id} className="border rounded shadow-sm">
              <div
                className="flex justify-between items-center p-3 cursor-pointer bg-gray-50"
                onClick={() => handleExpandSlot(slot.id)}
              >
                <div>
                  <span className="font-medium">{slot.time}</span>
                  <span className="ml-4 text-sm text-gray-600">
                    {slot.available}/{slot.capacity} available
                  </span>
                </div>
                <div className="flex space-x-2">
                  <button
                    onClick={(e) => {
                      e.stopPropagation();
                      onEditSlot(slot);
                    }}
                    className="bg-blue-500 text-white px-2 py-1 rounded text-sm"
                  >
                    Edit
                  </button>
                  <button
                    onClick={(e) => {
                      e.stopPropagation();
                      if (window.confirm('Are you sure you want to delete this slot?')) {
                        onDeleteSlot(slot.id);
                      }
                    }}
                    className="bg-red-500 text-white px-2 py-1 rounded text-sm"
                    disabled={slot.capacity > slot.available}
                  >
                    Delete
                  </button>
                </div>
              </div>

              {expandedSlotId === slot.id && (
                <div className="p-3 border-t">
                  {appointmentsBySlot[slot.id]?.length ? (
                    <table className="w-full text-sm">
                      <thead>
                        <tr className="border-b">
                          <th className="text-left py-2">Name</th>
                          <th className="text-left py-2">Purpose</th>
                          <th className="text-left py-2">Status</th>
                        </tr>
                      </thead>
                      <tbody>
                        {appointmentsBySlot[slot.id].map(appointment => (
                          <tr key={appointment.id} className="border-b">
                            <td className="py-2">{appointment.user_name}</td>
                            <td className="py-2">{appointment.purpose}</td>
                            <td className="py-2">
                              <span className={`px-2 py-1 rounded text-xs ${
                                appointment.status === 'scheduled' ? 'bg-blue-100 text-blue-800' :
                                appointment.status === 'completed' ? 'bg-green-100 text-green-800' :
                                'bg-red-100 text-red-800'
                              }`}>
                                {appointment.status}
                              </span>
                            </td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  ) : (
                    <p className="text-center text-gray-500 py-2">No appointments booked</p>
                  )}
                </div>
              )}
            </div>
          ))}
        </div>
      ) : (
        <p className="text-center text-gray-500 py-4">No slots available for this date</p>
      )}
    </div>
  );
};

export default AppointmentList;
